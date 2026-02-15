"""
Recommendation Engine - Smart repository recommendations
"""

from typing import Dict, Any, List
from .embeddings import get_embedding_service


class RecommendationEngine:
    """
    Generates smart recommendations for repositories.
    Uses embedding similarity and collaborative filtering.
    """
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
    
    def find_similar_repos(
        self,
        target_repo: Dict[str, Any],
        candidate_repos: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find repositories similar to the target repo.
        
        Args:
            target_repo: Reference repository
            candidate_repos: List of repos to compare
            top_k: Number of similar repos to return
            
        Returns:
            List of similar repos with similarity scores
        """
        return self.embedding_service.find_similar_repos(
            target_repo, candidate_repos, top_k
        )
    
    def get_complementary_repos(
        self,
        repo: Dict[str, Any],
        all_repos: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Suggest repos that complement the given repo.
        For example, if repo is a React UI library, suggest state management libs.
        """
        # Get repo's tech stack
        tech_stacks = repo.get("tech_stack", [])
        
        # Find repos with related but different tech
        complementary = []
        
        for candidate in all_repos:
            if candidate.get("id") == repo.get("id"):
                continue
            
            candidate_stacks = candidate.get("tech_stack", [])
            
            # Check for complementary patterns
            if "React" in tech_stacks and "Backend Strong" in candidate_stacks:
                complementary.append(candidate)
            elif "Machine Learning" in tech_stacks and "Data Science" in candidate_stacks:
                complementary.append(candidate)
            elif "Flutter" in tech_stacks and "Backend Strong" in candidate_stacks:
                complementary.append(candidate)
        
        return complementary[:10]
    
    def get_trending_in_category(
        self,
        repos: List[Dict[str, Any]],
        category: str,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get trending repos in a specific category.
        Trending = high stars per month + recent activity
        """
        from .features import FeatureExtractor
        
        trending = []
        
        for repo in repos:
            # Check if repo matches category
            tech_stacks = repo.get("tech_stack", [])
            if category not in tech_stacks:
                continue
            
            # Extract features
            features = FeatureExtractor.extract_all_features(repo)
            
            # Calculate trending score
            stars_per_month = features.get("stars_per_month", 0)
            activity_score = features.get("activity_recency_score", 0)
            
            trending_score = (stars_per_month * 0.7) + (activity_score * 30 * 0.3)
            
            trending.append({
                "repo": repo,
                "trending_score": trending_score
            })
        
        # Sort by trending score
        trending.sort(key=lambda x: x["trending_score"], reverse=True)
        
        return [item["repo"] for item in trending[:20]]
    
    def personalized_recommendations(
        self,
        user_history: List[Dict[str, Any]],
        all_repos: List[Dict[str, Any]],
        top_k: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations based on user's search/view history.
        
        Args:
            user_history: List of repos user has viewed/searched
            all_repos: All available repos
            top_k: Number of recommendations
            
        Returns:
            List of recommended repos
        """
        if not user_history:
            # No history, return trending
            return self.get_trending_repos(all_repos, top_k)
        
        # Aggregate user preferences from history
        user_tech_prefs = {}
        for repo in user_history:
            for tech in repo.get("tech_stack", []):
                user_tech_prefs[tech] = user_tech_prefs.get(tech, 0) + 1
        
        # Score repos based on user preferences
        scored_repos = []
        for repo in all_repos:
            # Skip if already in history
            if any(h.get("id") == repo.get("id") for h in user_history):
                continue
            
            score = 0
            for tech in repo.get("tech_stack", []):
                score += user_tech_prefs.get(tech, 0)
            
            if score > 0:
                scored_repos.append({
                    "repo": repo,
                    "preference_score": score
                })
        
        # Sort and return top K
        scored_repos.sort(key=lambda x: x["preference_score"], reverse=True)
        return [item["repo"] for item in scored_repos[:top_k]]
    
    def get_trending_repos(
        self,
        repos: List[Dict[str, Any]],
        top_k: int = 20
    ) -> List[Dict[str, Any]]:
        """Get overall trending repos across all categories"""
        from .features import FeatureExtractor
        
        trending = []
        
        for repo in repos:
            features = FeatureExtractor.extract_all_features(repo)
            
            # Trending score: stars per month * activity recency
            stars_per_month = features.get("stars_per_month", 0)
            activity_score = features.get("activity_recency_score", 0)
            popularity = features.get("popularity_score", 0)
            
            trending_score = (
                stars_per_month * 0.5 +
                activity_score * 20 * 0.3 +
                popularity * 0.2
            )
            
            trending.append({
                "repo": repo,
                "trending_score": trending_score
            })
        
        trending.sort(key=lambda x: x["trending_score"], reverse=True)
        return [item["repo"] for item in trending[:top_k]]


# Global singleton
_recommendation_engine = None

def get_recommendation_engine() -> RecommendationEngine:
    """Get global recommendation engine instance"""
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine
