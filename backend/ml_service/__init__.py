"""
ML Service Package - Advanced machine learning capabilities for GitHub repo analysis
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import re

from .features import FeatureExtractor
from .embeddings import EmbeddingService, get_embedding_service
from .classifiers import MLClassifiers, get_ml_classifiers
from .quality_scorer import QualityScorer
from .recommender import RecommendationEngine, get_recommendation_engine
from .github_analyzer import GitHubAnalyzer, get_github_analyzer


# Legacy MLService class for backward compatibility
class MLService:
    """Legacy service - kept for backward compatibility with old main.py"""
    
    @staticmethod
    def classify_status(repo: Dict[str, Any]) -> str:
        """Classify repository status"""
        classifiers = get_ml_classifiers()
        return classifiers.predict_status(repo)
    
    @staticmethod
    def analyze_tech_stack(repo: Dict[str, Any]) -> List[str]:
        """Analyze tech stack using keyword matching"""
        stack = set()
        topics = [t.lower() for t in repo.get("topics", [])]
        desc = (repo.get("description") or "").lower()
        lang = (repo.get("language") or "").lower()
        
        full_text = " ".join(topics) + " " + desc + " " + lang
        
        def score(keywords, weight_topic=2, weight_text=1):
            s = 0
            for k in keywords:
                if k in topics or k == lang:
                    s += weight_topic
                elif k in full_text:
                    s += weight_text
            return s
        
        techs = {
            "MERN Stack": ["mern", "react", "node", "mongo", "express", "mongoose"],
            "MEAN Stack": ["mean", "angular", "node", "mongo", "express"],
            "MEVN Stack": ["mevn", "vue", "node", "mongo", "express"],
            "Flutter": ["flutter", "dart", "bloc", "riverpod"],
            "React Native": ["react native", "expo"],
            "Machine Learning": ["machine learning", "deep learning", "tensorflow", "pytorch", "scikit", "keras", "neural network", "transformer", "llm", "gpt"],
            "Data Science": ["data science", "pandas", "numpy", "matplotlib", "analysis", "jupyter", "visualization"],
            "DevOps": ["docker", "kubernetes", "k8s", "terraform", "ansible", "jenkins", "ci/cd", "aws", "azure", "gcp"],
            "Web3/Blockchain": ["web3", "blockchain", "ethereum", "solidity", "smart contract", "crypto", "nft", "defi"],
            "Modern Frontend": ["next.js", "nextjs", "vue", "svelte", "tailwind", "typescript", "vite"],
            "Backend Strong": ["fastapi", "django", "flask", "spring boot", "ruby on rails", "go", "golang", "rust", "graphql"],
            "Game Dev": ["unity", "unreal", "godot", "pygame", "c#", "c++"]
        }
        
        for name, keywords in techs.items():
            if score(keywords) >= 2:
                stack.add(name)
        
        if "react" in topics and "native" not in full_text and "MERN Stack" not in stack:
            stack.add("React")
        
        if "android" in topics or "ios" in topics or "swift" in topics or "kotlin" in topics:
            if "Flutter" not in stack and "React Native" not in stack:
                stack.add("Mobile Dev")
        
        if not stack and lang:
            stack.add(lang.capitalize())
        
        return list(stack)
    
    @staticmethod
    def construct_github_query(q: str, tech_stack: Optional[str]) -> str:
        """Enhance query with tech stack"""
        query_parts = [q]
        
        if tech_stack:
            ts = tech_stack.lower()
            mapping = {
                "mern": "topic:mern",
                "mean": "topic:mean",
                "mevn": "topic:mevn",
                "full stack": "topic:full-stack",
                "machine learning": "topic:machine-learning",
                "data science": "topic:data-science",
                "mobile dev": "topic:android",
                "flutter": "language:dart topic:flutter",
                "react": "topic:react",
                "react native": "topic:react-native",
                "django": "topic:django",
                "spring": "topic:spring-boot",
                "devops": "topic:devops",
                "web3": "topic:web3",
                "blockchain": "topic:blockchain",
                "game dev": "topic:game-development",
                "modern frontend": "topic:react OR topic:vue OR topic:svelte",
                "backend strong": "topic:backend"
            }
            
            found = False
            for key, val in mapping.items():
                if key in ts:
                    query_parts.append(val)
                    found = True
                    break
            
            if not found:
                query_parts.append(f"language:{ts}")
        
        return " ".join(query_parts)


__all__ = [
    'FeatureExtractor',
    'EmbeddingService',
    'MLClassifiers',
    'QualityScorer',
    'RecommendationEngine',
    'GitHubAnalyzer',
    'MLService',  # Legacy
    'get_embedding_service',
    'get_ml_classifiers',
    'get_recommendation_engine',
    'get_github_analyzer'
]
