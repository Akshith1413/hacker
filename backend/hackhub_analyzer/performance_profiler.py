"""
Performance Profiler - Profiles repository performance and build metrics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime


class PerformanceProfiler:
    """
    Profiles repository performance metrics.
    
    Features:
    - Build time estimation
    - Dependency count analysis
    - Code complexity metrics
    - Performance scoring
    """
    
    def __init__(self):
        pass
    
    def profile_repository(
        self,
        repo_data: Dict[str, Any],
        execution_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Profile repository performance.
        
        Args:
            repo_data: Repository metadata
            execution_result: Optional execution results from RunAnywhere
            
        Returns:
            Performance profile with metrics and scores
        """
        profile = {
            "overall_score": 0.0,
            "build_time_seconds": 0.0,
            "install_time_seconds": 0.0,
            "test_time_seconds": 0.0,
            "total_dependencies": 0,
            "repository_size_mb": 0.0,
            "code_complexity": "unknown",
            "performance_grade": "unknown",
            "bottlenecks": [],
            "optimizations": []
        }
        
        # Extract from execution results if available
        if execution_result and execution_result.get("status") == "success":
            logs = execution_result.get("logs", [])
            
            for log in logs:
                step = log.get("step", "")
                exec_time = log.get("execution_time", 0)
                
                if "setup" in step:
                    profile["install_time_seconds"] += exec_time
                elif step == "build":
                    profile["build_time_seconds"] = exec_time
                elif step == "test":
                    profile["test_time_seconds"] = exec_time
            
            profile["total_time_seconds"] = execution_result.get("total_execution_time", 0)
        
        # Estimate from repository data if no execution
        else:
            profile = self._estimate_performance(repo_data)
        
        # Calculate performance score
        profile["overall_score"] = self._calculate_performance_score(profile)
        profile["performance_grade"] = self._get_performance_grade(profile["overall_score"])
        
        # Detect bottlenecks
        profile["bottlenecks"] = self._detect_bottlenecks(profile)
        profile["optimizations"] = self._suggest_optimizations(profile, repo_data)
        
        return profile
    
    def _estimate_performance(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate performance metrics without execution"""
        profile = {
            "build_time_seconds": 0.0,
            "install_time_seconds": 0.0,
            "test_time_seconds": 0.0,
            "total_dependencies": 0,
            "repository_size_mb": repo_data.get("size", 0) / 1024.0,  # Convert KB to MB
            "code_complexity": "unknown"
        }
        
        # Estimate based on tech stack
        tech_stack = repo_data.get("tech_stack", [])
        
        if any("node" in t.lower() or "javascript" in t.lower() for t in tech_stack):
            profile["install_time_seconds"] = 45.0  # npm install
            profile["build_time_seconds"] = 60.0
            profile["test_time_seconds"] = 30.0
            profile["total_dependencies"] = 50
        
        elif any("python" in t.lower() for t in tech_stack):
            profile["install_time_seconds"] = 30.0
            profile["build_time_seconds"] = 20.0
            profile["test_time_seconds"] = 20.0
            profile["total_dependencies"] = 20
        
        elif any("flutter" in t.lower() for t in tech_stack):
            profile["install_time_seconds"] = 60.0
            profile["build_time_seconds"] = 120.0
            profile["test_time_seconds"] = 40.0
            profile["total_dependencies"] = 30
        
        elif any("java" in t.lower() for t in tech_stack):
            profile["install_time_seconds"] = 90.0
            profile["build_time_seconds"] = 180.0
            profile["test_time_seconds"] = 60.0
            profile["total_dependencies"] = 40
        
        # Estimate complexity from stars and size
        stars = repo_data.get("stars", 0)
        size_mb = profile["repository_size_mb"]
        
        if stars < 100 and size_mb < 10:
            profile["code_complexity"] = "simple"
        elif stars < 1000 and size_mb < 50:
            profile["code_complexity"] = "moderate"
        else:
            profile["code_complexity"] = "complex"
        
        return profile
    
    def _calculate_performance_score(self, profile: Dict[str, Any]) -> float:
        """Calculate overall performance score (0-100)"""
        score = 100.0
        
        # Penalize slow build times
        build_time = profile.get("build_time_seconds", 0)
        if build_time > 300:  # > 5 minutes
            score -= 30
        elif build_time > 120:  # > 2 minutes
            score -= 15
        
        # Penalize slow install times
        install_time = profile.get("install_time_seconds", 0)
        if install_time > 180:  # > 3 minutes
            score -= 20
        elif install_time > 60:  # > 1 minute
            score -= 10
        
        # Penalize large dependency counts
        deps = profile.get("total_dependencies", 0)
        if deps > 100:
            score -= 15
        elif deps > 50:
            score -= 5
        
        # Penalize large repository size
        size_mb = profile.get("repository_size_mb", 0)
        if size_mb > 500:
            score -= 15
        elif size_mb > 100:
            score -= 5
        
        return max(0.0, min(100.0, score))
    
    def _get_performance_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _detect_bottlenecks(self, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect performance bottlenecks"""
        bottlenecks = []
        
        if profile.get("build_time_seconds", 0) > 180:
            bottlenecks.append({
                "type": "slow_build",
                "severity": "high",
                "message": "Build time exceeds 3 minutes",
                "value": profile["build_time_seconds"]
            })
        
        if profile.get("install_time_seconds", 0) > 120:
            bottlenecks.append({
                "type": "slow_install",
                "severity": "medium",
                "message": "Dependency installation is slow",
                "value": profile["install_time_seconds"]
            })
        
        if profile.get("total_dependencies", 0) > 100:
            bottlenecks.append({
                "type": "too_many_dependencies",
                "severity": "medium",
                "message": "High number of dependencies",
                "value": profile["total_dependencies"]
            })
        
        if profile.get("repository_size_mb", 0) > 500:
            bottlenecks.append({
                "type": "large_repository",
                "severity": "low",
                "message": "Repository size is large",
                "value": profile["repository_size_mb"]
            })
        
        return bottlenecks
    
    def _suggest_optimizations(
        self,
        profile: Dict[str, Any],
        repo_data: Dict[str, Any]
    ) -> List[str]:
        """Suggest performance optimizations"""
        optimizations = []
        
        if profile.get("build_time_seconds", 0) > 120:
            optimizations.append("Enable build caching to reduce build time")
            optimizations.append("Consider using incremental builds")
        
        if profile.get("install_time_seconds", 0) > 60:
            optimizations.append("Use lock files for faster dependency resolution")
            optimizations.append("Consider removing unused dependencies")
        
        if profile.get("total_dependencies", 0) > 50:
            optimizations.append("Audit dependencies and remove unused packages")
            optimizations.append("Consider using lighter alternatives for heavy dependencies")
        
        if profile.get("repository_size_mb", 0) > 100:
            optimizations.append("Use Git LFS for large binary files")
            optimizations.append("Add build artifacts to .gitignore")
        
        return optimizations


# Global instance
_performance_profiler: Optional[PerformanceProfiler] = None


def get_performance_profiler() -> PerformanceProfiler:
    """Get or create global performance profiler instance"""
    global _performance_profiler
    if _performance_profiler is None:
        _performance_profiler = PerformanceProfiler()
    return _performance_profiler
