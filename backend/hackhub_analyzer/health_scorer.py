"""
Health Scorer - Calculates comprehensive repository health scores
"""

from typing import Dict, List, Optional, Any


class HealthScorer:
    """
    Calculates comprehensive health scores for repositories combining
    multiple analysis dimensions.
    
    Features:
    - Multi-dimensional health scoring
    - Trend analysis
    - Contributor health metrics
    - Actionable recommendations
    """
    
    def __init__(self):
        pass
    
    def calculate_health_score(
        self,
        repo_data: Dict[str, Any],
        quality_detail: Optional[Dict[str, Any]] = None,
        readme_analysis: Optional[Dict[str, Any]] = None,
        config_analysis: Optional[Dict[str, Any]] = None,
        performance_profile: Optional[Dict[str, Any]] = None,
        execution_result: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive health score.
        
        Args:
            repo_data: Repository metadata
            quality_detail: Quality scoring results
            readme_analysis: README validation results
            config_analysis: Configuration analysis results
            performance_profile: Performance profiling results
            execution_result: Execution test results
            
        Returns:
            Comprehensive health score and breakdown
        """
        health_score = {
            "overall_score": 0.0,
            "overall_grade": "unknown",
            "dimensions": {
                "code_quality": 0.0,
                "documentation": 0.0,
                "community": 0.0,
                "maintenance": 0.0,
                "configuration": 0.0,
                "performance": 0.0,
                "executability": 0.0
            },
            "trend": "stable",
            "health_indicators": {},
            "risk_factors": [],
            "strengths": [],
            "improvement_areas": [],
            "recommendations": [],
            "contributor_health": {}
        }
        
        # 1. Code Quality Score (from existing quality scorer)
        if quality_detail:
            health_score["dimensions"]["code_quality"] = quality_detail.get("code_quality_score", 0)
            health_score["dimensions"]["community"] = quality_detail.get("community_score", 0)
            health_score["dimensions"]["maintenance"] = quality_detail.get("maintenance_score", 0)
        
        # 2. Documentation Score (from README analysis)
        if readme_analysis:
            health_score["dimensions"]["documentation"] = readme_analysis.get("overall_score", 0)
        elif quality_detail:
            health_score["dimensions"]["documentation"] = quality_detail.get("documentation_score", 0)
        
        # 3. Configuration Score
        if config_analysis:
            health_score["dimensions"]["configuration"] = config_analysis.get("overall_score", 0)
        
        # 4. Performance Score
        if performance_profile:
            health_score["dimensions"]["performance"] = performance_profile.get("overall_score", 0)
        
        # 5. Executability Score (from execution results)
        if execution_result:
            exec_score = self._calculate_executability_score(execution_result)
            health_score["dimensions"]["executability"] = exec_score
        
        # Calculate overall score (weighted average)
        weights = {
            "code_quality": 0.20,
            "documentation": 0.15,
            "community": 0.15,
            "maintenance": 0.15,
            "configuration": 0.10,
            "performance": 0.15,
            "executability": 0.10
        }
        
        overall = 0.0
        for dimension, weight in weights.items():
            overall += health_score["dimensions"].get(dimension, 0) * weight
        
        health_score["overall_score"] = overall
        health_score["overall_grade"] = self._get_grade(overall)
        
        # Analyze trends
        health_score["trend"] = self._analyze_trend(repo_data)
        
        # Identify health indicators
        health_score["health_indicators"] = self._get_health_indicators(repo_data, health_score)
        
        # Detect risk factors
        health_score["risk_factors"] = self._detect_risk_factors(
            repo_data, health_score, config_analysis, execution_result
        )
        
        # Identify strengths
        health_score["strengths"] = self._identify_strengths(health_score)
        
        # Identify improvement areas
        health_score["improvement_areas"] = self._identify_improvement_areas(health_score)
        
        # Generate recommendations
        health_score["recommendations"] = self._generate_recommendations(
            repo_data, health_score, readme_analysis, config_analysis, performance_profile
        )
        
        # Calculate contributor health
        health_score["contributor_health"] = self._assess_contributor_health(repo_data)
        
        return health_score
    
    def _calculate_executability_score(self, execution_result: Dict[str, Any]) -> float:
        """Calculate executability score from execution results"""
        score = 0.0
        
        status = execution_result.get("status", "failed")
        
        if status == "success":
            score = 100.0
        elif status == "failed":
            # Partial credit based on what succeeded
            logs = execution_result.get("logs", [])
            total_steps = len(logs)
            successful_steps = sum(1 for log in logs if log.get("status") == "success")
            
            if total_steps > 0:
                score = (successful_steps / total_steps) * 70
        
        # Bonus for fast execution
        exec_time = execution_result.get("total_execution_time", 0)
        if exec_time < 60:  # Under 1 minute
            score = min(100.0, score + 10)
        
        return score
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "C+"
        elif score >= 65:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _analyze_trend(self, repo_data: Dict[str, Any]) -> str:
        """Analyze project trend (growing, stable, declining)"""
        # This is a simplified version
        # In production, you'd analyze commit history, star growth, etc.
        
        status = repo_data.get("status", "").lower()
        
        if status == "active":
            return "growing"
        elif status in ["ongoing", "started"]:
            return "stable"
        elif status in ["slowing down", "finished"]:
            return "declining"
        
        return "stable"
    
    def _get_health_indicators(
        self,
        repo_data: Dict[str, Any],
        health_score: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get key health indicators"""
        return {
            "is_actively_maintained": repo_data.get("status") == "Active",
            "has_recent_activity": True,  # Would check last_updated
            "has_tests": health_score["dimensions"]["code_quality"] > 50,
            "has_ci_cd": health_score["dimensions"]["configuration"] > 50,
            "has_good_docs": health_score["dimensions"]["documentation"] > 70,
            "is_executable": health_score["dimensions"]["executability"] > 50,
            "performance_acceptable": health_score["dimensions"]["performance"] > 60
        }
    
    def _detect_risk_factors(
        self,
        repo_data: Dict[str, Any],
        health_score: Dict[str, Any],
        config_analysis: Optional[Dict[str, Any]],
        execution_result: Optional[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Detect potential risk factors"""
        risks = []
        
        # Low quality scores
        if health_score["overall_score"] < 50:
            risks.append({
                "type": "low_quality",
                "severity": "high",
                "message": "Overall project quality is below acceptable standards"
            })
        
        # No CI/CD
        if health_score["dimensions"]["configuration"] < 50:
            risks.append({
                "type": "no_ci_cd",
                "severity": "medium",
                "message": "No continuous integration/deployment configured"
            })
        
        # Security issues
        if config_analysis and config_analysis.get("security_score", 100) < 70:
            risks.append({
                "type": "security_issues",
                "severity": "critical",
                "message": "Security configuration has issues"
            })
        
        # Not executable
        if execution_result and execution_result.get("status") == "failed":
            risks.append({
                "type": "not_executable",
                "severity": "medium",
                "message": "Repository cannot be easily executed or tested"
            })
        
        # Declining trend
        if health_score["trend"] == "declining":
            risks.append({
                "type": "declining_activity",
                "severity": "low",
                "message": "Project activity appears to be declining"
            })
        
        return risks
    
    def _identify_strengths(self, health_score: Dict[str, Any]) -> List[str]:
        """Identify project strengths"""
        strengths = []
        
        for dimension, score in health_score["dimensions"].items():
            if score >= 80:
                strengths.append(f"Excellent {dimension.replace('_', ' ')}")
        
        return strengths
    
    def _identify_improvement_areas(self, health_score: Dict[str, Any]) -> List[str]:
        """Identify areas needing improvement"""
        areas = []
        
        for dimension, score in health_score["dimensions"].items():
            if score < 60:
                areas.append(f"{dimension.replace('_', ' ').title()} needs improvement")
        
        return areas
    
    def _generate_recommendations(
        self,
        repo_data: Dict[str, Any],
        health_score: Dict[str, Any],
        readme_analysis: Optional[Dict[str, Any]],
        config_analysis: Optional[Dict[str, Any]],
        performance_profile: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Documentation recommendations
        if health_score["dimensions"]["documentation"] < 70:
            recommendations.append({
                "priority": "high",
                "category": "documentation",
                "action": "Improve README documentation",
                "details": "Add clear installation instructions, usage examples, and API documentation"
            })
        
        # Configuration recommendations
        if health_score["dimensions"]["configuration"] < 70:
            recommendations.append({
                "priority": "high",
                "category": "configuration",
                "action": "Set up CI/CD pipeline",
                "details": "Add GitHub Actions or similar for automated testing and deployment"
            })
        
        # Performance recommendations
        if performance_profile and performance_profile.get("overall_score", 100) < 70:
            recommendations.append({
                "priority": "medium",
                "category": "performance",
                "action": "Optimize build and installation process",
                "details": "Reduce dependencies and enable caching"
            })
        
        # Code quality recommendations
        if health_score["dimensions"]["code_quality"] < 70:
            recommendations.append({
                "priority": "high",
                "category": "code_quality",
                "action": "Add automated tests",
                "details": "Implement unit tests and integration tests with good coverage"
            })
        
        # Community recommendations
        if health_score["dimensions"]["community"] < 50:
            recommendations.append({
                "priority": "low",
                "category": "community",
                "action": "Grow project visibility",
                "details": "Promote project, add topics/tags, and engage with community"
            })
        
        return recommendations
    
    def _assess_contributor_health(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess contributor and community health"""
        # This would analyze contributor activity, diversity, etc.
        # Simplified version for now
        
        return {
            "is_welcoming": True,  # Would check for CODE_OF_CONDUCT, CONTRIBUTING
            "has_active_maintainers": repo_data.get("status") == "Active",
            "response_time": "unknown",  # Would analyze issue response times
            "contributor_diversity": "unknown"  # Would analyze contributor count
        }


# Global instance
_health_scorer: Optional[HealthScorer] = None


def get_health_scorer() -> HealthScorer:
    """Get or create global health scorer instance"""
    global _health_scorer
    if _health_scorer is None:
        _health_scorer = HealthScorer()
    return _health_scorer
