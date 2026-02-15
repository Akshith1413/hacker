"""
Feature Engineering Module - Extract and compute features from GitHub repos
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
import re


class FeatureExtractor:
    """
    Advanced feature extraction for repository analysis.
    Extracts temporal, community, and code quality features.
    """
    
    @staticmethod
    def parse_date(date_str: str) -> datetime:
        """Parse ISO 8601 date string from GitHub API"""
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def extract_temporal_features(repo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract time-based features from repository activity.
        
        Returns:
            Dict with temporal features like days_since_push, activity_score, etc.
        """
        now = datetime.now(timezone.utc)
        
        pushed_at = FeatureExtractor.parse_date(repo.get("pushed_at") or repo.get("updated_at"))
        created_at = FeatureExtractor.parse_date(repo.get("created_at"))
        updated_at = FeatureExtractor.parse_date(repo.get("updated_at"))
        
        if not pushed_at or not created_at:
            return {
                "days_since_push": 9999,
                "days_since_creation": 9999,
                "days_since_update": 9999,
                "project_age_months": 0,
                "activity_recency_score": 0.0,
                "is_archived": repo.get("archived", False)
            }
        
        days_since_push = (now - pushed_at).days
        days_since_creation = (now - created_at).days
        days_since_update = (now - updated_at).days if updated_at else days_since_push
        
        # Calculate activity recency score (0-1, higher = more recent)
        # Exponential decay: score = e^(-days/30)
        import math
        activity_recency_score = math.exp(-days_since_push / 30.0)
        
        return {
            "days_since_push": days_since_push,
            "days_since_creation": days_since_creation,
            "days_since_update": days_since_update,
            "project_age_months": days_since_creation / 30.0,
            "activity_recency_score": activity_recency_score,
            "is_archived": repo.get("archived", False),
            "created_at": created_at,
            "pushed_at": pushed_at,
            "updated_at": updated_at
        }
    
    @staticmethod
    def extract_community_features(repo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract community engagement features.
        
        Returns:
            Dict with stars, forks, watchers, normalized scores, etc.
        """
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)
        watchers = repo.get("watchers_count", stars)  # Often same as stars
        open_issues = repo.get("open_issues_count", 0)
        subscribers = repo.get("subscribers_count", watchers)
        
        # Get project age for normalization
        temporal = FeatureExtractor.extract_temporal_features(repo)
        age_months = max(temporal["project_age_months"], 1)  # Avoid division by zero
        
        # Normalized metrics (per month)
        stars_per_month = stars / age_months
        forks_per_month = forks / age_months
        
        # Engagement ratios
        fork_ratio = forks / max(stars, 1)  # How many people fork vs star
        issue_ratio = open_issues / max(stars, 1)  # Issue density
        
        # Popularity score (log-scaled to handle wide range)
        import math
        popularity_score = math.log10(stars + 1) * 10  # 0-100 scale approx
        
        return {
            "stars": stars,
            "forks": forks,
            "watchers": watchers,
            "open_issues": open_issues,
            "subscribers": subscribers,
            "stars_per_month": stars_per_month,
            "forks_per_month": forks_per_month,
            "fork_ratio": fork_ratio,
            "issue_ratio": issue_ratio,
            "popularity_score": min(popularity_score, 100),
            "has_issues": repo.get("has_issues", True),
            "has_wiki": repo.get("has_wiki", False),
            "has_pages": repo.get("has_pages", False),
            "has_downloads": repo.get("has_downloads", False)
        }
    
    @staticmethod
    def extract_code_quality_indicators(repo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract code quality indicators from repository metadata.
        
        Returns:
            Dict with quality indicators (presence of tests, docs, CI/CD, etc.)
        """
        description = repo.get("description", "") or ""
        topics = repo.get("topics", [])
        
        # Check topics for quality indicators
        has_tests = any(kw in topics for kw in ["testing", "tests", "pytest", "jest", "junit", "unittest"])
        has_ci_cd = any(kw in topics for kw in ["ci", "cd", "github-actions", "travis", "jenkins", "circleci"])
        has_documentation = any(kw in topics for kw in ["documentation", "docs", "sphinx", "mkdocs"])
        
        # Check description for quality keywords
        desc_lower = description.lower()
        mentions_tests = any(kw in desc_lower for kw in ["test", "tested", "testing", "coverage"])
        mentions_docs = any(kw in desc_lower for kw in ["documentation", "documented", "readme"])
        
        # License indicator
        has_license = repo.get("license") is not None
        license_type = repo.get("license", {}).get("spdx_id", "UNKNOWN") if has_license else "UNKNOWN"
        
        # Description quality
        has_description = len(description) > 0
        description_length = len(description)
        description_quality_score = min(description_length / 5, 20)  # Max 20 points for description
        
        # Topic count (more topics often indicates better maintained)
        topic_count = len(topics)
        topic_score = min(topic_count * 5, 15)  # Max 15 points for topics
        
        # Language specified
        has_language = repo.get("language") is not None
        
        return {
            "has_tests": has_tests or mentions_tests,
            "has_ci_cd": has_ci_cd,
            "has_documentation": has_documentation or mentions_docs,
            "has_license": has_license,
            "license_type": license_type,
            "has_description": has_description,
            "description_length": description_length,
            "description_quality_score": description_quality_score,
            "topic_count": topic_count,
            "topic_score": topic_score,
            "has_language": has_language,
            "language": repo.get("language", "Unknown")
        }
    
    @staticmethod
    def extract_all_features(repo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract all features from a repository.
        
        Returns:
            Dict containing all extracted features
        """
        features = {}
        
        # Add basic repo info
        features["repo_id"] = repo.get("id")
        features["full_name"] = repo.get("full_name")
        features["name"] = repo.get("name")
        
        # Extract all feature groups
        features.update(FeatureExtractor.extract_temporal_features(repo))
        features.update(FeatureExtractor.extract_community_features(repo))
        features.update(FeatureExtractor.extract_code_quality_indicators(repo))
        
        return features
    
    @staticmethod
    def get_feature_vector(repo: Dict[str, Any]) -> List[float]:
        """
        Convert repository features to a numerical vector for ML models.
        
        Returns:
            List of numerical features suitable for sklearn models
        """
        features = FeatureExtractor.extract_all_features(repo)
        
        # Create feature vector (only numerical features)
        vector = [
            features.get("days_since_push", 9999),
            features.get("days_since_creation", 9999),
            features.get("project_age_months", 0),
            features.get("activity_recency_score", 0),
            float(features.get("is_archived", False)),
            features.get("stars", 0),
            features.get("forks", 0),
            features.get("watchers", 0),
            features.get("open_issues", 0),
            features.get("stars_per_month", 0),
            features.get("forks_per_month", 0),
            features.get("fork_ratio", 0),
            features.get("issue_ratio", 0),
            features.get("popularity_score", 0),
            float(features.get("has_tests", False)),
            float(features.get("has_ci_cd", False)),
            float(features.get("has_documentation", False)),
            float(features.get("has_license", False)),
            features.get("description_quality_score", 0),
            features.get("topic_score", 0),
            float(features.get("has_language", False)),
        ]
        
        return vector
    
    @staticmethod
    def get_feature_names() -> List[str]:
        """Return list of feature names in the same order as get_feature_vector"""
        return [
            "days_since_push",
            "days_since_creation",
            "project_age_months",
            "activity_recency_score",
            "is_archived",
            "stars",
            "forks",
            "watchers",
            "open_issues",
            "stars_per_month",
            "forks_per_month",
            "fork_ratio",
            "issue_ratio",
            "popularity_score",
            "has_tests",
            "has_ci_cd",
            "has_documentation",
            "has_license",
            "description_quality_score",
            "topic_score",
            "has_language"
        ]
