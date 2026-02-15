"""
Execution Controller - Orchestrates repository testing and code execution
"""

import asyncio
import json
import re
import uuid
from typing import Dict, Optional, List, Any, Tuple
from datetime import datetime
from .sandbox_manager import get_sandbox_manager


class ExecutionController:
    """
    High-level controller for executing repositories and code in sandboxes.
    
    Features:
    - Automatic language detection
    - Dependency installation
    - Build and test execution
    - README instruction validation
    - Performance profiling
    """
    
    def __init__(self):
        self.sandbox_manager = get_sandbox_manager()
        self.execution_history: Dict[str, Dict[str, Any]] = {}
    
    async def analyze_repository_executability(
        self,
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze if a repository can be executed and extract setup instructions.
        
        Args:
            repo_data: Repository metadata (from GitHub API or HackHub)
            
        Returns:
            Analysis results including executability, runtime, commands, etc.
        """
        analysis = {
            "is_executable": False,
            "detected_runtime": None,
            "languages": [],
            "setup_commands": [],
            "run_command": None,
            "test_command": None,
            "build_command": None,
            "dependencies": [],
            "estimated_complexity": "unknown",
            "requires_docker": False,
            "requires_database": False,
            "confidence": 0.0,
            "issues": []
        }
        
        # Extract language information
        language = repo_data.get("language", "").lower()
        if language:
            analysis["languages"].append(language)
        
        # Detect runtime from tech stack or files
        tech_stack = repo_data.get("tech_stack", [])
        
        # Python detection
        if "python" in language or any("python" in t.lower() for t in tech_stack):
            analysis["detected_runtime"] = "python"
            analysis["is_executable"] = True
            analysis["setup_commands"] = [
                "pip install --upgrade pip",
                "pip install -r requirements.txt || echo 'No requirements.txt found'"
            ]
            analysis["run_command"] = "python main.py || python app.py || python src/main.py"
            analysis["test_command"] = "pytest || python -m unittest discover"
            analysis["confidence"] = 0.85
        
        # Node.js / JavaScript detection
        elif any(x in language for x in ["javascript", "typescript"]) or \
             any(x in ["node", "react", "vue", "angular", "nextjs"] for x in [t.lower() for t in tech_stack]):
            analysis["detected_runtime"] = "node"
            analysis["is_executable"] = True
            analysis["setup_commands"] = [
                "npm install || yarn install"
            ]
            analysis["run_command"] = "npm start || node index.js || node server.js"
            analysis["test_command"] = "npm test"
            analysis["build_command"] = "npm run build"
            analysis["confidence"] = 0.9
        
        # Flutter detection
        elif "flutter" in [t.lower() for t in tech_stack] or "dart" in language:
            analysis["detected_runtime"] = "flutter"
            analysis["is_executable"] = True
            analysis["setup_commands"] = [
                "flutter pub get"
            ]
            analysis["run_command"] = "flutter run -d web-server --web-port=8080"
            analysis["test_command"] = "flutter test"
            analysis["build_command"] = "flutter build web"
            analysis["confidence"] = 0.8
        
        # Java detection
        elif "java" in language or any(x in ["spring", "maven", "gradle"] for x in [t.lower() for t in tech_stack]):
            analysis["detected_runtime"] = "java"
            analysis["is_executable"] = True
            analysis["setup_commands"] = [
                "mvn clean install || gradle build"
            ]
            analysis["run_command"] = "mvn spring-boot:run || gradle bootRun || java -jar target/*.jar"
            analysis["test_command"] = "mvn test || gradle test"
            analysis["build_command"] = "mvn package || gradle build"
            analysis["confidence"] = 0.75
        
        # Go detection
        elif "go" in language or "golang" in language:
            analysis["detected_runtime"] = "go"
            analysis["is_executable"] = True
            analysis["setup_commands"] = [
                "go mod download"
            ]
            analysis["run_command"] = "go run main.go || go run ."
            analysis["test_command"] = "go test ./..."
            analysis["build_command"] = "go build"
            analysis["confidence"] = 0.85
        
        # Rust detection
        elif "rust" in language:
            analysis["detected_runtime"] = "rust"
            analysis["is_executable"] = True
            analysis["setup_commands"] = [
                "cargo fetch"
            ]
            analysis["run_command"] = "cargo run"
            analysis["test_command"] = "cargo test"
            analysis["build_command"] = "cargo build --release"
            analysis["confidence"] = 0.85
        
        # Detect Docker requirement
        if any(x in ["docker", "kubernetes", "containerized"] for x in [t.lower() for t in tech_stack]):
            analysis["requires_docker"] = True
            analysis["setup_commands"].insert(0, "docker-compose up -d || docker build -t app .")
        
        # Detect database requirement
        if any(x in ["postgresql", "mysql", "mongodb", "redis", "database"] for x in [t.lower() for t in tech_stack]):
            analysis["requires_database"] = True
            analysis["issues"].append("Repository requires database setup")
        
        # Estimate complexity
        stars = repo_data.get("stars", 0)
        open_issues = repo_data.get("open_issues_count", 0)
        
        if stars < 100 and open_issues < 10:
            analysis["estimated_complexity"] = "simple"
        elif stars < 1000 and open_issues < 50:
            analysis["estimated_complexity"] = "moderate"
        else:
            analysis["estimated_complexity"] = "complex"
        
        return analysis
    
    async def execute_repository(
        self,
        repo_url: str,
        repo_data: Dict[str, Any],
        steps: List[str] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute a repository in a sandbox environment.
        
        Args:
            repo_url: GitHub repository URL
            repo_data: Repository metadata
            steps: Optional custom execution steps
            timeout: Execution timeout in seconds
            
        Returns:
            Execution results with logs, status, and outputs
        """
        execution_id = str(uuid.uuid4())
        
        # Analyze executability first
        analysis = await self.analyze_repository_executability(repo_data)
        
        if not analysis["is_executable"]:
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": "Repository is not executable",
                "analysis": analysis,
                "logs": []
            }
        
        # Create sandbox
        runtime = analysis["detected_runtime"]
        sandbox_id = await self.sandbox_manager.create_sandbox(
            language=runtime,
            memory_limit="1g",
            cpu_limit=2.0,
            timeout=timeout,
            network_enabled=True
        )
        
        if not sandbox_id:
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": "Failed to create sandbox (Docker not available)",
                "analysis": analysis,
                "logs": []
            }
        
        execution_log = []
        start_time = datetime.now()
        
        try:
            # Step 1: Clone repository
            execution_log.append({
                "step": "clone",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            })
            
            clone_result = await self.sandbox_manager.execute_in_sandbox(
                sandbox_id=sandbox_id,
                command=f"git clone {repo_url} /tmp/repo",
                timeout=120
            )
            
            if not clone_result["success"]:
                execution_log.append({
                    "step": "clone",
                    "status": "failed",
                    "error": clone_result["stderr"],
                    "timestamp": datetime.now().isoformat()
                })
                
                await self.sandbox_manager.stop_sandbox(sandbox_id)
                
                return {
                    "execution_id": execution_id,
                    "sandbox_id": sandbox_id,
                    "status": "failed",
                    "error": "Failed to clone repository",
                    "analysis": analysis,
                    "logs": execution_log
                }
            
            execution_log.append({
                "step": "clone",
                "status": "success",
                "output": clone_result["stdout"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Step 2: Run setup commands
            for i, cmd in enumerate(analysis["setup_commands"]):
                execution_log.append({
                    "step": f"setup_{i}",
                    "command": cmd,
                    "status": "running",
                    "timestamp": datetime.now().isoformat()
                })
                
                setup_result = await self.sandbox_manager.execute_in_sandbox(
                    sandbox_id=sandbox_id,
                    command=cmd,
                    working_dir="/tmp/repo",
                    timeout=180
                )
                
                execution_log.append({
                    "step": f"setup_{i}",
                    "command": cmd,
                    "status": "success" if setup_result["success"] else "warning",
                    "output": setup_result["stdout"],
                    "error": setup_result["stderr"],
                    "execution_time": setup_result["execution_time"],
                    "timestamp": datetime.now().isoformat()
                })
            
            # Step 3: Run tests (if available)
            if analysis["test_command"]:
                execution_log.append({
                    "step": "test",
                    "command": analysis["test_command"],
                    "status": "running",
                    "timestamp": datetime.now().isoformat()
                })
                
                test_result = await self.sandbox_manager.execute_in_sandbox(
                    sandbox_id=sandbox_id,
                    command=analysis["test_command"],
                    working_dir="/tmp/repo",
                    timeout=120
                )
                
                execution_log.append({
                    "step": "test",
                    "command": analysis["test_command"],
                    "status": "success" if test_result["success"] else "failed",
                    "output": test_result["stdout"],
                    "error": test_result["stderr"],
                    "execution_time": test_result["execution_time"],
                    "timestamp": datetime.now().isoformat()
                })
            
            # Step 4: Build (if needed)
            if analysis["build_command"]:
                execution_log.append({
                    "step": "build",
                    "command": analysis["build_command"],
                    "status": "running",
                    "timestamp": datetime.now().isoformat()
                })
                
                build_result = await self.sandbox_manager.execute_in_sandbox(
                    sandbox_id=sandbox_id,
                    command=analysis["build_command"],
                    working_dir="/tmp/repo",
                    timeout=240
                )
                
                execution_log.append({
                    "step": "build",
                    "command": analysis["build_command"],
                    "status": "success" if build_result["success"] else "failed",
                    "output": build_result["stdout"],
                    "error": build_result["stderr"],
                    "execution_time": build_result["execution_time"],
                    "timestamp": datetime.now().isoformat()
                })
            
            # Get resource stats
            stats = await self.sandbox_manager.get_sandbox_stats(sandbox_id)
            
            # Cleanup sandbox
            await self.sandbox_manager.stop_sandbox(sandbox_id)
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            # Determine overall status
            failed_critical = any(
                log.get("status") == "failed" and log.get("step") in ["clone", "build"]
                for log in execution_log
            )
            
            execution_result = {
                "execution_id": execution_id,
                "sandbox_id": sandbox_id,
                "status": "failed" if failed_critical else "success",
                "analysis": analysis,
                "logs": execution_log,
                "total_execution_time": total_time,
                "resource_stats": stats,
                "timestamp": start_time.isoformat()
            }
            
            # Store in history
            self.execution_history[execution_id] = execution_result
            
            return execution_result
            
        except Exception as e:
            await self.sandbox_manager.stop_sandbox(sandbox_id)
            
            return {
                "execution_id": execution_id,
                "sandbox_id": sandbox_id,
                "status": "error",
                "error": str(e),
                "analysis": analysis,
                "logs": execution_log
            }
    
    async def execute_code_snippet(
        self,
        code: str,
        language: str,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Execute a code snippet in a sandbox.
        
        Args:
            code: Code to execute
            language: Programming language
            timeout: Execution timeout in seconds
            
        Returns:
            Execution results
        """
        execution_id = str(uuid.uuid4())
        
        # Create sandbox
        sandbox_id = await self.sandbox_manager.create_sandbox(
            language=language,
            memory_limit="256m",
            cpu_limit=0.5,
            timeout=timeout,
            network_enabled=False  # Disable network for code snippets
        )
        
        if not sandbox_id:
            return {
                "execution_id": execution_id,
                "status": "failed",
                "error": "Failed to create sandbox (Docker not available)",
                "stdout": "",
                "stderr": ""
            }
        
        try:
            # Create temporary file with code
            filename = f"code_{execution_id}.{self._get_file_extension(language)}"
            
            await self.sandbox_manager.upload_file_to_sandbox(
                sandbox_id=sandbox_id,
                file_content=code.encode('utf-8'),
                destination_path=f"/tmp/{filename}"
            )
            
            # Execute code
            run_command = self._get_run_command(language, filename)
            
            result = await self.sandbox_manager.execute_in_sandbox(
                sandbox_id=sandbox_id,
                command=run_command,
                working_dir="/tmp",
                timeout=timeout
            )
            
            # Cleanup
            await self.sandbox_manager.stop_sandbox(sandbox_id)
            
            return {
                "execution_id": execution_id,
                "sandbox_id": sandbox_id,
                "status": "success" if result["success"] else "failed",
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "exit_code": result["exit_code"],
                "execution_time": result["execution_time"]
            }
            
        except Exception as e:
            await self.sandbox_manager.stop_sandbox(sandbox_id)
            
            return {
                "execution_id": execution_id,
                "sandbox_id": sandbox_id,
                "status": "error",
                "error": str(e),
                "stdout": "",
                "stderr": str(e)
            }
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "node": "js",
            "typescript": "ts",
            "java": "java",
            "go": "go",
            "rust": "rs",
            "cpp": "cpp",
            "c": "c",
            "ruby": "rb",
            "php": "php",
        }
        return extensions.get(language.lower(), "txt")
    
    def _get_run_command(self, language: str, filename: str) -> str:
        """Get command to run a file"""
        commands = {
            "python": f"python /tmp/{filename}",
            "javascript": f"node /tmp/{filename}",
            "node": f"node /tmp/{filename}",
            "typescript": f"ts-node /tmp/{filename}",
            "java": f"javac /tmp/{filename} && java {filename.replace('.java', '')}",
            "go": f"go run /tmp/{filename}",
            "rust": f"rustc /tmp/{filename} -o /tmp/output && /tmp/output",
            "cpp": f"g++ /tmp/{filename} -o /tmp/output && /tmp/output",
            "c": f"gcc /tmp/{filename} -o /tmp/output && /tmp/output",
            "ruby": f"ruby /tmp/{filename}",
            "php": f"php /tmp/{filename}",
        }
        return commands.get(language.lower(), f"cat /tmp/{filename}")
    
    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent execution history"""
        history = sorted(
            self.execution_history.values(),
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        return history[:limit]
    
    def get_execution_result(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get specific execution result"""
        return self.execution_history.get(execution_id)


# Global execution controller instance
_execution_controller: Optional[ExecutionController] = None


def get_execution_controller() -> ExecutionController:
    """Get or create global execution controller instance"""
    global _execution_controller
    if _execution_controller is None:
        _execution_controller = ExecutionController()
    return _execution_controller
