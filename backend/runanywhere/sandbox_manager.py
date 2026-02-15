"""
Sandbox Manager - Manages isolated Docker containers for safe code execution
"""

import asyncio
import docker
import hashlib
import time
import uuid
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta


class SandboxManager:
    """
    Manages Docker-based sandboxes for safe repository testing and code execution.
    
    Features:
    - Isolated container environments
    - Resource limits (CPU, memory, network)
    - Automatic cleanup
    - Multi-language support
    """
    
    def __init__(self):
        """Initialize Docker client and sandbox registry"""
        try:
            self.docker_client = docker.from_env()
            self.active_sandboxes: Dict[str, Dict[str, Any]] = {}
            self.docker_available = True
        except Exception as e:
            print(f"Docker not available: {e}")
            self.docker_client = None
            self.active_sandboxes = {}
            self.docker_available = False
    
    def is_available(self) -> bool:
        """Check if Docker is available"""
        return self.docker_available and self.docker_client is not None
    
    async def create_sandbox(
        self,
        language: str,
        memory_limit: str = "512m",
        cpu_limit: float = 1.0,
        timeout: int = 300,
        network_enabled: bool = True
    ) -> Optional[str]:
        """
        Create a new isolated sandbox environment.
        
        Args:
            language: Programming language (python, node, java, flutter, etc.)
            memory_limit: Memory limit (e.g., "512m", "1g")
            cpu_limit: CPU limit (number of cores)
            timeout: Execution timeout in seconds
            network_enabled: Whether to allow network access
            
        Returns:
            sandbox_id: Unique identifier for the sandbox, or None if failed
        """
        if not self.is_available():
            return None
        
        sandbox_id = str(uuid.uuid4())
        image_map = {
            "python": "python:3.11-slim",
            "node": "node:18-alpine",
            "javascript": "node:18-alpine",
            "java": "openjdk:17-slim",
            "go": "golang:1.21-alpine",
            "rust": "rust:1.75-slim",
            "flutter": "cirrusci/flutter:stable",
            "dart": "dart:stable",
            "ruby": "ruby:3.2-alpine",
            "php": "php:8.2-cli-alpine",
            "cpp": "gcc:13-alpine",
            "c": "gcc:13-alpine",
        }
        
        image = image_map.get(language.lower(), "ubuntu:22.04")
        
        try:
            # Pull image if not available
            try:
                self.docker_client.images.get(image)
            except docker.errors.ImageNotFound:
                print(f"Pulling image {image}...")
                self.docker_client.images.pull(image)
            
            # Create container with resource limits
            container = self.docker_client.containers.create(
                image=image,
                command="/bin/sleep 3600",  # Keep alive
                detach=True,
                mem_limit=memory_limit,
                nano_cpus=int(cpu_limit * 1e9),
                network_mode="bridge" if network_enabled else "none",
                network_disabled=not network_enabled,
                # Security settings
                cap_drop=["ALL"],
                security_opt=["no-new-privileges"],
                read_only=False,  # Allow writes to /tmp
                tmpfs={'/tmp': 'size=100m,mode=1777'},
                labels={
                    "hackhub.sandbox": "true",
                    "hackhub.sandbox_id": sandbox_id,
                    "hackhub.language": language
                }
            )
            
            container.start()
            
            # Register sandbox
            self.active_sandboxes[sandbox_id] = {
                "container_id": container.id,
                "container": container,
                "language": language,
                "created_at": datetime.now(),
                "timeout": timeout,
                "memory_limit": memory_limit,
                "cpu_limit": cpu_limit,
                "network_enabled": network_enabled,
                "status": "running"
            }
            
            print(f"Created sandbox {sandbox_id} with {language} environment")
            return sandbox_id
            
        except Exception as e:
            print(f"Failed to create sandbox: {e}")
            return None
    
    async def execute_in_sandbox(
        self,
        sandbox_id: str,
        command: str,
        working_dir: str = "/tmp",
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Execute a command in an existing sandbox.
        
        Args:
            sandbox_id: Sandbox identifier
            command: Command to execute
            working_dir: Working directory for execution
            timeout: Command timeout in seconds
            
        Returns:
            Result dict with stdout, stderr, exit_code, execution_time
        """
        if sandbox_id not in self.active_sandboxes:
            return {
                "success": False,
                "error": "Sandbox not found",
                "stdout": "",
                "stderr": "Sandbox does not exist",
                "exit_code": -1,
                "execution_time": 0
            }
        
        sandbox = self.active_sandboxes[sandbox_id]
        container = sandbox["container"]
        
        try:
            start_time = time.time()
            
            # Execute command with timeout
            exec_result = container.exec_run(
                cmd=f"sh -c 'cd {working_dir} && {command}'",
                demux=True,
                stream=False,
                tty=False,
                environment={},
                workdir=working_dir
            )
            
            execution_time = time.time() - start_time
            
            # Check timeout
            if execution_time > timeout:
                return {
                    "success": False,
                    "error": "Execution timeout",
                    "stdout": "",
                    "stderr": f"Command exceeded {timeout}s timeout",
                    "exit_code": -1,
                    "execution_time": execution_time
                }
            
            # Decode output
            stdout = exec_result.output[0].decode('utf-8') if exec_result.output[0] else ""
            stderr = exec_result.output[1].decode('utf-8') if exec_result.output[1] else ""
            
            return {
                "success": exec_result.exit_code == 0,
                "error": None,
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exec_result.exit_code,
                "execution_time": execution_time
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "execution_time": 0
            }
    
    async def upload_file_to_sandbox(
        self,
        sandbox_id: str,
        file_content: bytes,
        destination_path: str
    ) -> bool:
        """Upload a file to sandbox"""
        if sandbox_id not in self.active_sandboxes:
            return False
        
        try:
            import tarfile
            import io
            
            sandbox = self.active_sandboxes[sandbox_id]
            container = sandbox["container"]
            
            # Create tar archive
            tar_stream = io.BytesIO()
            tar = tarfile.TarFile(fileobj=tar_stream, mode='w')
            
            # Add file to tar
            file_data = io.BytesIO(file_content)
            tarinfo = tarfile.TarInfo(name=destination_path.split('/')[-1])
            tarinfo.size = len(file_content)
            tar.addfile(tarinfo, file_data)
            tar.close()
            
            # Upload to container
            tar_stream.seek(0)
            container.put_archive('/tmp', tar_stream)
            
            return True
            
        except Exception as e:
            print(f"Failed to upload file: {e}")
            return False
    
    async def download_file_from_sandbox(
        self,
        sandbox_id: str,
        source_path: str
    ) -> Optional[bytes]:
        """Download a file from sandbox"""
        if sandbox_id not in self.active_sandboxes:
            return None
        
        try:
            import tarfile
            import io
            
            sandbox = self.active_sandboxes[sandbox_id]
            container = sandbox["container"]
            
            # Get file as tar archive
            bits, stat = container.get_archive(source_path)
            
            # Extract from tar
            tar_stream = io.BytesIO(b''.join(bits))
            tar = tarfile.TarFile(fileobj=tar_stream)
            
            # Get first file
            member = tar.getmembers()[0]
            file_obj = tar.extractfile(member)
            
            if file_obj:
                return file_obj.read()
            
            return None
            
        except Exception as e:
            print(f"Failed to download file: {e}")
            return None
    
    async def get_sandbox_stats(self, sandbox_id: str) -> Optional[Dict[str, Any]]:
        """Get resource usage statistics for a sandbox"""
        if sandbox_id not in self.active_sandboxes:
            return None
        
        try:
            sandbox = self.active_sandboxes[sandbox_id]
            container = sandbox["container"]
            
            stats = container.stats(stream=False)
            
            # Calculate CPU usage
            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                       stats['precpu_stats']['cpu_usage']['total_usage']
            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                          stats['precpu_stats']['system_cpu_usage']
            cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
            
            # Memory usage
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 0)
            memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0
            
            return {
                "sandbox_id": sandbox_id,
                "cpu_percent": cpu_percent,
                "memory_usage_mb": memory_usage / (1024 * 1024),
                "memory_limit_mb": memory_limit / (1024 * 1024),
                "memory_percent": memory_percent,
                "network_rx_bytes": stats['networks']['eth0']['rx_bytes'] if 'networks' in stats else 0,
                "network_tx_bytes": stats['networks']['eth0']['tx_bytes'] if 'networks' in stats else 0,
            }
            
        except Exception as e:
            print(f"Failed to get stats: {e}")
            return None
    
    async def stop_sandbox(self, sandbox_id: str) -> bool:
        """Stop and remove a sandbox"""
        if sandbox_id not in self.active_sandboxes:
            return False
        
        try:
            sandbox = self.active_sandboxes[sandbox_id]
            container = sandbox["container"]
            
            container.stop(timeout=5)
            container.remove()
            
            del self.active_sandboxes[sandbox_id]
            print(f"Stopped sandbox {sandbox_id}")
            return True
            
        except Exception as e:
            print(f"Failed to stop sandbox: {e}")
            return False
    
    async def cleanup_expired_sandboxes(self) -> int:
        """Remove sandboxes that have exceeded their timeout"""
        cleaned = 0
        now = datetime.now()
        
        expired_ids = []
        for sandbox_id, sandbox in self.active_sandboxes.items():
            age = now - sandbox["created_at"]
            if age.total_seconds() > sandbox["timeout"]:
                expired_ids.append(sandbox_id)
        
        for sandbox_id in expired_ids:
            if await self.stop_sandbox(sandbox_id):
                cleaned += 1
        
        return cleaned
    
    async def cleanup_all_sandboxes(self) -> int:
        """Stop and remove all active sandboxes"""
        sandbox_ids = list(self.active_sandboxes.keys())
        cleaned = 0
        
        for sandbox_id in sandbox_ids:
            if await self.stop_sandbox(sandbox_id):
                cleaned += 1
        
        return cleaned
    
    def get_active_sandboxes(self) -> List[Dict[str, Any]]:
        """Get list of all active sandboxes"""
        return [
            {
                "sandbox_id": sandbox_id,
                "language": sandbox["language"],
                "created_at": sandbox["created_at"].isoformat(),
                "age_seconds": (datetime.now() - sandbox["created_at"]).total_seconds(),
                "timeout": sandbox["timeout"],
                "memory_limit": sandbox["memory_limit"],
                "cpu_limit": sandbox["cpu_limit"],
                "status": sandbox["status"]
            }
            for sandbox_id, sandbox in self.active_sandboxes.items()
        ]


# Global sandbox manager instance
_sandbox_manager: Optional[SandboxManager] = None


def get_sandbox_manager() -> SandboxManager:
    """Get or create global sandbox manager instance"""
    global _sandbox_manager
    if _sandbox_manager is None:
        _sandbox_manager = SandboxManager()
    return _sandbox_manager
