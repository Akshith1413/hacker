from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import re

class MLService:
    @staticmethod
    def classify_status(repo: Dict[str, Any]) -> str:
        """
        Classifies the repo status based on activity patterns.
        """
        now = datetime.now(timezone.utc)
        
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            except ValueError:
                return None

        # Parse dates
        pushed_at = parse_date(repo.get("pushed_at") or repo.get("updated_at"))
        created_at = parse_date(repo.get("created_at"))
        
        if not pushed_at or not created_at:
            return "Unknown"
        
        days_since_push = (now - pushed_at).days
        days_since_creation = (now - created_at).days
        
        # Finished: Inactive for > 6 months OR explicitly archived
        if repo.get("archived") or days_since_push > 180:
            return "Finished"
        
        # Active: Pushed within last 7 days
        if days_since_push < 7:
            return "Active"
            
        # Ongoing: Active within last 30 days
        if days_since_push < 30:
            return "Ongoing"
            
        # Slowing Down: Active within last 90 days
        if days_since_push < 90:
            return "Slowing Down"
        
        # Started: Created recently (< 90 days) but not super active recently
        if days_since_creation < 90:
            return "Started"
            
        return "Ongoing" # Default fallback

    @staticmethod
    def analyze_tech_stack(repo: Dict[str, Any]) -> List[str]:
        """
        Detects tech stacks using weighted keyword scoring.
        """
        stack = set()
        topics = [t.lower() for t in repo.get("topics", [])]
        desc = (repo.get("description") or "").lower()
        lang = (repo.get("language") or "").lower()
        
        # Combined text for broad search
        full_text = " ".join(topics) + " " + desc + " " + lang
        
        # Helper to score matches
        def score(keywords, weight_topic=2, weight_text=1):
            s = 0
            for k in keywords:
                if k in topics or k == lang:
                    s += weight_topic
                elif k in full_text:
                    s += weight_text
            return s

        # Tech Definitions
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
                
        # Specific overrides/refinements
        if "react" in topics and "native" not in full_text and "MERN Stack" not in stack:
            stack.add("React")
        
        if "android" in topics or "ios" in topics or "swift" in topics or "kotlin" in topics:
            if "Flutter" not in stack and "React Native" not in stack:
                stack.add("Mobile Dev")

        # Fallback to language if no specific stack detected
        if not stack and lang:
            stack.add(lang.capitalize())
            
        return list(stack)

    @staticmethod
    def construct_github_query(q: str, tech_stack: Optional[str]) -> str:
        """
        Enhances the search query based on 'Smart Search' logic.
        """
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
            
            # Simple fuzzy matching for keys
            found = False
            for key, val in mapping.items():
                if key in ts:
                    query_parts.append(val)
                    found = True
                    break
            
            if not found:
                 query_parts.append(f"language:{ts}")
                 
        return " ".join(query_parts)
