"""
GitHub Analyzer - Deep analysis of repository contents
"""

from typing import Dict, Any, List, Optional
import httpx
import json


class GitHubAnalyzer:
    """
    Performs deep analysis of GitHub repositories by fetching
    additional data like README, package files, and file structure.
    """
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize analyzer with optional GitHub token for higher rate limits.
        
        Args:
            github_token: Personal Access Token for GitHub API
        """
        self.github_token = github_token
        self.headers = {}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"
    
    async def fetch_readme(self, repo_full_name: str) -> Optional[str]:
        """
        Fetch README content for a repository.
        
        Args:
            repo_full_name: Repository full name (owner/repo)
            
        Returns:
            README content as string, or None if not found
        """
        url = f"https://api.github.com/repos/{repo_full_name}/readme"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    # README is base64 encoded
                    import base64
                    content = base64.b64decode(data["content"]).decode("utf-8")
                    return content
                else:
                    return None
        except Exception as e:
            print(f"[GitHubAnalyzer] Error fetching README for {repo_full_name}: {e}")
            return None
    
    async def fetch_package_file(
        self,
        repo_full_name: str,
        filename: str
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch and parse a package file (package.json, requirements.txt, etc.).
        
        Args:
            repo_full_name: Repository full name
            filename: File to fetch (e.g., "package.json")
            
        Returns:
            Parsed file content as dict, or None if not found
        """
        url = f"https://api.github.com/repos/{repo_full_name}/contents/{filename}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    import base64
                    content = base64.b64decode(data["content"]).decode("utf-8")
                    
                    # Parse based on file type
                    if filename.endswith(".json"):
                        return json.loads(content)
                    elif filename.endswith(".txt"):
                        return {"dependencies": content.split("\n")}
                    else:
                        return {"raw": content}
                else:
                    return None
        except Exception as e:
            print(f"[GitHubAnalyzer] Error fetching {filename} for {repo_full_name}: {e}")
            return None
    
    async def analyze_dependencies(self, repo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze repository dependencies by fetching package files.
        
        Args:
            repo: Repository dict
            
        Returns:
            Dict with detected dependencies and tech stack
        """
        full_name = repo.get("full_name")
        language = repo.get("language", "").lower()
        
        dependencies = {
            "detected": False,
            "tech_stacks": [],
            "frameworks": [],
            "libraries": []
        }
        
        try:
            # Check for package.json (Node.js / JavaScript)
            if language in ["javascript", "typescript"]:
                package_json = await self.fetch_package_file(full_name, "package.json")
                if package_json:
                    dependencies["detected"] = True
                    deps = package_json.get("dependencies", {})
                    dev_deps = package_json.get("devDependencies", {})
                    
                    all_deps = list(deps.keys()) + list(dev_deps.keys())
                    dependencies["libraries"] = all_deps
                    
                    # Detect frameworks
                    if "react" in all_deps:
                        dependencies["frameworks"].append("React")
                        dependencies["tech_stacks"].append("React")
                    if "vue" in all_deps:
                        dependencies["frameworks"].append("Vue.js")
                        dependencies["tech_stacks"].append("Modern Frontend")
                    if "express" in all_deps:
                        dependencies["frameworks"].append("Express")
                        dependencies["tech_stacks"].append("Backend Strong")
                    if "next" in all_deps:
                        dependencies["frameworks"].append("Next.js")
                        dependencies["tech_stacks"].append("Modern Frontend")
            
            # Check for requirements.txt (Python)
            elif language == "python":
                requirements = await self.fetch_package_file(full_name, "requirements.txt")
                if requirements:
                    dependencies["detected"] = True
                    deps = requirements.get("dependencies", [])
                    dependencies["libraries"] = [d.split("==")[0].split(">=")[0] for d in deps if d.strip()]
                    
                    # Detect frameworks
                    deps_lower = [d.lower() for d in dependencies["libraries"]]
                    if any(x in deps_lower for x in ["tensorflow", "pytorch", "sklearn"]):
                        dependencies["tech_stacks"].append("Machine Learning")
                    if any(x in deps_lower for x in ["pandas", "numpy", "matplotlib"]):
                        dependencies["tech_stacks"].append("Data Science")
                    if any(x in deps_lower for x in ["django", "flask", "fastapi"]):
                        dependencies["tech_stacks"].append("Backend Strong")
            
            # Check for pubspec.yaml (Flutter/Dart)
            elif language == "dart":
                pubspec = await self.fetch_package_file(full_name, "pubspec.yaml")
                if pubspec:
                    dependencies["detected"] = True
                    dependencies["tech_stacks"].append("Flutter")
        
        except Exception as e:
            print(f"[GitHubAnalyzer] Error analyzing dependencies: {e}")
        
        return dependencies
    
    async def get_file_structure(self, repo_full_name: str) -> List[str]:
        """
        Get repository file structure (tree).
        
        Args:
            repo_full_name: Repository full name
            
        Returns:
            List of file paths
        """
        url = f"https://api.github.com/repos/{repo_full_name}/git/trees/main?recursive=1"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    tree = data.get("tree", [])
                    return [item["path"] for item in tree if item["type"] == "blob"]
                else:
                    # Try 'master' branch
                    url = url.replace("/main?", "/master?")
                    response = await client.get(url, headers=self.headers)
                    if response.status_code == 200:
                        data = response.json()
                        tree = data.get("tree", [])
                        return [item["path"] for item in tree if item["type"] == "blob"]
                    return []
        except Exception as e:
            print(f"[GitHubAnalyzer] Error fetching file structure: {e}")
            return []
    
    def detect_tech_from_files(self, file_paths: List[str]) -> List[str]:
        """
        Detect tech stacks from file structure.
        
        Args:
            file_paths: List of file paths in repo
            
        Returns:
            List of detected tech stacks
        """
        tech_stacks = set()
        
        # Check for common patterns
        for path in file_paths:
            path_lower = path.lower()
            
            # Frontend frameworks
            if "webpack.config" in path_lower or "vite.config" in path_lower:
                tech_stacks.add("Modern Frontend")
            if path_lower.endswith(".tsx") or path_lower.endswith(".jsx"):
                tech_stacks.add("React")
            if path_lower.endswith(".vue"):
                tech_stacks.add("Modern Frontend")
            
            # Testing
            if "/test/" in path_lower or path_lower.startswith("test/"):
                tech_stacks.add("Tested")
            if "jest.config" in path_lower or "pytest.ini" in path_lower:
                tech_stacks.add("Tested")
            
            # CI/CD
            if ".github/workflows" in path_lower:
                tech_stacks.add("CI/CD")
            if ".travis.yml" in path_lower or ".circleci" in path_lower:
                tech_stacks.add("CI/CD")
            
            # Docker
            if "dockerfile" in path_lower or "docker-compose" in path_lower:
                tech_stacks.add("DevOps")
        
        return list(tech_stacks)


# Global singleton
_github_analyzer = None

def get_github_analyzer(github_token: Optional[str] = None) -> GitHubAnalyzer:
    """Get global GitHub analyzer instance"""
    global _github_analyzer
    if _github_analyzer is None:
        _github_analyzer = GitHubAnalyzer(github_token)
    return _github_analyzer
