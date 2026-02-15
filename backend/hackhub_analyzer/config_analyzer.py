"""
Config Analyzer - Analyzes project configuration files for issues
"""

import json
import re
from typing import Dict, List, Optional, Any


class ConfigAnalyzer:
    """
    Analyzes project configuration files to detect issues and best practices.
    
    Features:
    - Check CI/CD configurations
    - Validate dependency files
    - Detect security issues
    - Check for best practices
    """
    
    def __init__(self):
        pass
    
    def analyze_configurations(
        self,
        repo_data: Dict[str, Any],
        files: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """
        Analyze all configuration files in a repository.
        
        Args:
            repo_data: Repository metadata
            files: Dict of filename -> content
            
        Returns:
            Analysis results with scores and issues
        """
        analysis = {
            "overall_score": 0.0,
            "ci_cd_score": 0.0,
            "dependency_score": 0.0,
            "security_score": 0.0,
            "best_practices_score": 0.0,
            "issues": [],
            "warnings": [],
            "recommendations": []
        }
        
        if not files:
            files = {}
        
        # Analyze CI/CD configuration
        ci_cd_analysis = self._analyze_ci_cd(files)
        analysis["ci_cd_score"] = ci_cd_analysis["score"]
        analysis["issues"].extend(ci_cd_analysis.get("issues", []))
        analysis["recommendations"].extend(ci_cd_analysis.get("recommendations", []))
        
        # Analyze dependencies
        dep_analysis = self._analyze_dependencies(files, repo_data)
        analysis["dependency_score"] = dep_analysis["score"]
        analysis["warnings"].extend(dep_analysis.get("warnings", []))
        
        # Analyze security
        sec_analysis = self._analyze_security(files)
        analysis["security_score"] = sec_analysis["score"]
        analysis["issues"].extend(sec_analysis.get("issues", []))
        
        # Check best practices
        bp_analysis = self._check_best_practices(files, repo_data)
        analysis["best_practices_score"] = bp_analysis["score"]
        analysis["recommendations"].extend(bp_analysis.get("recommendations", []))
        
        # Calculate overall score (weighted average)
        analysis["overall_score"] = (
            analysis["ci_cd_score"] * 0.25 +
            analysis["dependency_score"] * 0.25 +
            analysis["security_score"] * 0.30 +
            analysis["best_practices_score"] * 0.20
        )
        
        return analysis
    
    def _analyze_ci_cd(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Analyze CI/CD configuration"""
        score = 0.0
        issues = []
        recommendations = []
        
        # Check for CI/CD files
        ci_files = [
            ".github/workflows",
            ".gitlab-ci.yml",
            ".travis.yml",
            "circle.yml",
            ".circleci/config.yml",
            "azure-pipelines.yml",
            "jenkinsfile"
        ]
        
        has_ci = any(
            ci_file.lower() in filename.lower()
            for filename in files.keys()
            for ci_file in ci_files
        )
        
        if has_ci:
            score += 50
        else:
            recommendations.append("Add CI/CD pipeline (GitHub Actions, GitLab CI, etc.)")
        
        # Check for specific workflows
        workflow_checks = {
            "test": 20,
            "build": 15,
            "deploy": 10,
            "lint": 5
        }
        
        for workflow, points in workflow_checks.items():
            if any(workflow in content.lower() for content in files.values()):
                score += points
        
        return {
            "score": min(100.0, score),
            "issues": issues,
            "recommendations": recommendations
        }
    
    def _analyze_dependencies(
        self,
        files: Dict[str, str],
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze dependency management"""
        score = 0.0
        warnings = []
        
        # Check for dependency files
        dep_files = {
            "package.json": "Node.js",
            "requirements.txt": "Python",
            "Pipfile": "Python (Pipenv)",
            "pubspec.yaml": "Dart/Flutter",
            "pom.xml": "Java (Maven)",
            "build.gradle": "Java (Gradle)",
            "Cargo.toml": "Rust",
            "go.mod": "Go",
            "Gemfile": "Ruby"
        }
        
        found_dep_files = []
        for dep_file, language in dep_files.items():
            if dep_file in files:
                found_dep_files.append((dep_file, language))
                score += 40
                break  # Only count once
        
        if not found_dep_files:
            warnings.append({
                "type": "missing_dependency_file",
                "severity": "medium",
                "message": "No dependency management file found"
            })
        else:
            # Check for lock files
            lock_files = {
                "package-lock.json": "package.json",
                "yarn.lock": "package.json",
                "Pipfile.lock": "Pipfile",
                "pubspec.lock": "pubspec.yaml",
                "Cargo.lock": "Cargo.toml",
                "go.sum": "go.mod",
                "Gemfile.lock": "Gemfile"
            }
            
            for lock_file, dep_file in lock_files.items():
                if dep_file in files and lock_file in files:
                    score += 30
                    break
                elif dep_file in files and lock_file not in files:
                    warnings.append({
                        "type": "missing_lock_file",
                        "severity": "low",
                        "message": f"Consider committing {lock_file} for reproducible builds"
                    })
        
        # Check for version pinning (in package.json)
        if "package.json" in files:
            try:
                pkg = json.loads(files["package.json"])
                deps = pkg.get("dependencies", {})
                
                unpinned = [
                    name for name, version in deps.items()
                    if version.startswith("^") or version.startswith("~")
                ]
                
                if unpinned:
                    warnings.append({
                        "type": "unpinned_dependencies",
                        "severity": "low",
                        "message": f"{len(unpinned)} dependencies use flexible versioning"
                    })
                else:
                    score += 30
            except json.JSONDecodeError:
                warnings.append({
                    "type": "invalid_json",
                    "severity": "high",
                    "message": "package.json is not valid JSON"
                })
        
        return {
            "score": min(100.0, score),
            "warnings": warnings
        }
    
    def _analyze_security(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Analyze security configuration"""
        score = 100.0  # Start with perfect score, deduct for issues
        issues = []
        
        # Check for sensitive files that shouldn't be committed
        sensitive_patterns = [
            r"\.env$",
            r"\.env\.local$",
            r"\.env\.production$",
            r"credentials",
            r"secrets",
            r"private.*key",
            r".*\.pem$",
            r".*\.key$"
        ]
        
        for filename in files.keys():
            for pattern in sensitive_patterns:
                if re.search(pattern, filename, re.IGNORECASE):
                    issues.append({
                        "type": "sensitive_file_committed",
                        "severity": "critical",
                        "file": filename,
                        "message": f"Sensitive file '{filename}' should not be committed"
                    })
                    score -= 30
        
        # Check for .gitignore
        if ".gitignore" not in files:
            issues.append({
                "type": "missing_gitignore",
                "severity": "medium",
                "message": "No .gitignore file found"
            })
            score -= 10
        else:
            # Check if .gitignore includes common patterns
            gitignore = files[".gitignore"]
            recommended_patterns = ["node_modules", ".env", "*.pyc", ".DS_Store"]
            
            for pattern in recommended_patterns:
                if pattern not in gitignore:
                    score -= 5
        
        # Check for security.md or similar
        if any("security" in f.lower() for f in files.keys()):
            score += 10
        
        return {
            "score": max(0.0, min(100.0, score)),
            "issues": issues
        }
    
    def _check_best_practices(
        self,
        files: Dict[str, str],
        repo_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for general best practices"""
        score = 0.0
        recommendations = []
        
        # Check for essential files
        essential_files = {
            "README.md": 30,
            "LICENSE": 20,
            "CONTRIBUTING.md": 10,
            "CODE_OF_CONDUCT.md": 5,
            ".editorconfig": 5,
            ".gitattributes": 5
        }
        
        for file, points in essential_files.items():
            if any(file.lower() == f.lower() for f in files.keys()):
                score += points
            elif points >= 20:  # Only recommend high-value files
                recommendations.append(f"Add {file} to the repository")
        
        # Check for testing setup
        test_patterns = [
            r"test",
            r"spec",
            r"__tests__",
            r"pytest",
            r"jest",
            r"mocha"
        ]
        
        has_tests = any(
            any(re.search(pattern, filename, re.IGNORECASE) for pattern in test_patterns)
            for filename in files.keys()
        )
        
        if has_tests:
            score += 25
        else:
            recommendations.append("Add automated tests to the project")
        
        return {
            "score": min(100.0, score),
            "recommendations": recommendations
        }


# Global instance
_config_analyzer: Optional[ConfigAnalyzer] = None


def get_config_analyzer() -> ConfigAnalyzer:
    """Get or create global config analyzer instance"""
    global _config_analyzer
    if _config_analyzer is None:
        _config_analyzer = ConfigAnalyzer()
    return _config_analyzer
