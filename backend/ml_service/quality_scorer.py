"""
Quality Scoring System - Evaluate repository quality on a 0-100 scale
"""

from typing import Dict, Any
from .features import FeatureExtractor


class QualityScorer:
    """
    Scores repositories on a 0-100 scale based on multiple quality dimensions:
    - Documentation (25 points)
    - Code Quality (25 points)
    - Community (25 points)
    - Maintenance (25 points)
    """
    
    @staticmethod
    def score_documentation(repo: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, float]:
        """
        Score documentation quality (0-25 points).
        
        Components:
        - Has description (3 points)
        - Description length (5 points max, 1 point per 20 chars up to 100 chars)
        - Has topics (5 points max, 1 point per topic up to 5)
        - Has wiki (4 points)
        - Has pages (GitHub Pages) (4 points)
        - README quality proxy: description_quality_score (4 points)
        """
        score = 0
        breakdown = {}
        
        # Has description
        if features.get("has_description"):
            score += 3
            breakdown["has_description"] = 3
        
        # Description length (quality proxy)
        desc_len = features.get("description_length", 0)
        desc_points = min(desc_len / 20, 5)  # 5 points max
        score += desc_points
        breakdown["description_length"] = desc_points
        
        # Has topics
        topic_count = features.get("topic_count", 0)
        topic_points = min(topic_count, 5)  # 1 point per topic, 5 max
        score += topic_points
        breakdown["topics"] = topic_points
        
        # Has wiki
        if features.get("has_wiki"):
            score += 4
            breakdown["has_wiki"] = 4
        
        # Has GitHub Pages
        if features.get("has_pages"):
            score += 4
            breakdown["has_pages"] = 4
        
        # Documentation mentioned
        if features.get("has_documentation"):
            score += 4
            breakdown["has_documentation"] = 4
        
        return {
            "score": min(score, 25),
            "breakdown": breakdown
        }
    
    @staticmethod
    def score_code_quality(repo: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, float]:
        """
        Score code quality indicators (0-25 points).
        
        Components:
        - Has tests (10 points)
        - Has CI/CD (10 points)
        - Has license (5 points)
        """
        score = 0
        breakdown = {}
        
        # Has tests
        if features.get("has_tests"):
            score += 10
            breakdown["has_tests"] = 10
        
        # Has CI/CD
        if features.get("has_ci_cd"):
            score += 10
            breakdown["has_ci_cd"] = 10
        
        # Has license
        if features.get("has_license"):
            score += 5
            breakdown["has_license"] = 5
        
        return {
            "score": min(score, 25),
            "breakdown": breakdown
        }
    
    @staticmethod
    def score_community(repo: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, float]:
        """
        Score community engagement (0-25 points).
        
        Components:
        - Stars (logarithmic scale, 10 points max)
        - Forks (logarithmic scale, 5 points max)
        - Watchers (3 points max)
        - Activity (stars per month, 7 points max)
        """
        score = 0
        breakdown = {}
        
        import math
        
        # Stars (logarithmic: log10(stars+1) * 2, max 10)
        stars = features.get("stars", 0)
        star_points = min(math.log10(stars + 1) * 2, 10)
        score += star_points
        breakdown["stars"] = star_points
        
        # Forks (logarithmic: log10(forks+1) * 1.5, max 5)
        forks = features.get("forks", 0)
        fork_points = min(math.log10(forks + 1) * 1.5, 5)
        score += fork_points
        breakdown["forks"] = fork_points
        
        # Watchers (logarithmic: log10(watchers+1), max 3)
        watchers = features.get("watchers", 0)
        watcher_points = min(math.log10(watchers + 1), 3)
        score += watcher_points
        breakdown["watchers"] = watcher_points
        
        # Stars per month (activity measure)
        stars_per_month = features.get("stars_per_month", 0)
        activity_points = min(math.log10(stars_per_month + 1) * 3, 7)
        score += activity_points
        breakdown["stars_per_month"] = activity_points
        
        return {
            "score": min(score, 25),
            "breakdown": breakdown
        }
    
    @staticmethod
    def score_maintenance(repo: Dict[str, Any], features: Dict[str, Any]) -> Dict[str, float]:
        """
        Score maintenance and activity (0-25 points).
        
        Components:
        - Recent activity (activity_recency_score * 15, max 15 points)
        - Not archived (5 points)
        - Has language (2 points)
        - Issues enabled (3 points)
        """
        score = 0
        breakdown = {}
        
        # Recent activity (exponential decay based on days since push)
        activity_score = features.get("activity_recency_score", 0)
        activity_points = activity_score * 15  # Scale to 15 points max
        score += activity_points
        breakdown["recent_activity"] = activity_points
        
        # Not archived
        if not features.get("is_archived"):
            score += 5
            breakdown["not_archived"] = 5
        
        # Has language
        if features.get("has_language"):
            score += 2
            breakdown["has_language"] = 2
        
        # Issues enabled
        if features.get("has_issues"):
            score += 3
            breakdown["issues_enabled"] = 3
        
        return {
            "score": min(score, 25),
            "breakdown": breakdown
        }
    
    @staticmethod
    def calculate_quality_score(repo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive quality score for a repository.
        
        Args:
            repo: Repository dict from GitHub API
            
        Returns:
            Dict with:
                - total_score (0-100)
                - documentation_score (0-25)
                - code_quality_score (0-25)
                - community_score (0-25)
                - maintenance_score (0-25)
                - breakdown (detailed scoring)
                - grade (A+, A, B+, B, C+, C, D, F)
        """
        # Extract features
        features = FeatureExtractor.extract_all_features(repo)
        
        # Calculate dimension scores
        doc_result = QualityScorer.score_documentation(repo, features)
        quality_result = QualityScorer.score_code_quality(repo, features)
        community_result = QualityScorer.score_community(repo, features)
        maintenance_result = QualityScorer.score_maintenance(repo, features)
        
        # Calculate total
        total_score = (
            doc_result["score"] +
            quality_result["score"] +
            community_result["score"] +
            maintenance_result["score"]
        )
        
        # Determine grade
        grade = QualityScorer._score_to_grade(total_score)
        
        return {
            "total_score": round(total_score, 2),
            "documentation_score": round(doc_result["score"], 2),
            "code_quality_score": round(quality_result["score"], 2),
            "community_score": round(community_result["score"], 2),
            "maintenance_score": round(maintenance_result["score"], 2),
            "grade": grade,
            "breakdown": {
                "documentation": doc_result["breakdown"],
                "code_quality": quality_result["breakdown"],
                "community": community_result["breakdown"],
                "maintenance": maintenance_result["breakdown"]
            }
        }
    
    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    @staticmethod
    def get_quality_tier(score: float) -> str:
        """
        Get quality tier classification.
        
        Returns:
            One of: "Excellent", "Good", "Fair", "Poor"
        """
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Fair"
        else:
            return "Poor"
