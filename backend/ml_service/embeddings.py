"""
Embedding Service - Semantic text embeddings using sentence-transformers
"""

from typing import List, Dict, Any, Optional
import numpy as np
from functools import lru_cache
import hashlib


class EmbeddingService:
    """
    Manages text embeddings for semantic similarity and classification.
    Uses sentence-transformers for high-quality embeddings.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service with a pre-trained model.
        
        Args:
            model_name: Name of the sentence-transformers model
                       'all-MiniLM-L6-v2' is lightweight (80MB) and fast
        """
        self.model_name = model_name
        self._model = None
        self._tech_stack_embeddings = {}
        
    def _load_model(self):
        """Lazy load the model only when needed"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                print(f"[EmbeddingService] Loaded model: {self.model_name}")
            except ImportError:
                print("[EmbeddingService] WARNING: sentence-transformers not installed. Using fallback keyword matching.")
                self._model = "fallback"
            except Exception as e:
                print(f"[EmbeddingService] Error loading model: {e}. Using fallback.")
                self._model = "fallback"
    
    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text to embedding vector.
        
        Args:
            text: Input text string
            
        Returns:
            numpy array of embedding vector
        """
        self._load_model()
        
        if self._model == "fallback":
            # Simple fallback: use TF-IDF-like approach
            return self._simple_embedding(text)
        
        try:
            return self._model.encode(text, convert_to_numpy=True)
        except Exception as e:
            print(f"[EmbeddingService] Encoding error: {e}")
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str, dim: int = 384) -> np.ndarray:
        """
        Fallback simple embedding using hash-based features.
        Not as good as transformers but better than nothing.
        """
        # Use hash of words to create a pseudo-embedding
        words = text.lower().split()
        embedding = np.zeros(dim)
        
        for word in words:
            # Hash word to multiple indices
            h = hashlib.md5(word.encode()).hexdigest()
            for i in range(0, len(h), 8):
                idx = int(h[i:i+8], 16) % dim
                embedding[idx] += 1.0
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding
    
    def encode_repo(self, repo: Dict[str, Any]) -> np.ndarray:
        """
        Create embedding for a repository using its metadata.
        
        Args:
            repo: Repository dict from GitHub API
            
        Returns:
            Embedding vector representing the repo
        """
        # Combine relevant text fields
        text_parts = []
        
        if repo.get("name"):
            text_parts.append(repo["name"])
        
        if repo.get("description"):
            text_parts.append(repo["description"])
        
        if repo.get("topics"):
            text_parts.extend(repo["topics"])
        
        if repo.get("language"):
            text_parts.append(repo["language"])
        
        combined_text = " ".join(text_parts)
        return self.encode_text(combined_text)
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Returns:
            Similarity score between 0 and 1
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def initialize_tech_stack_embeddings(self):
        """
        Pre-compute embeddings for tech stack categories.
        This speeds up classification.
        """
        tech_stack_descriptions = {
            "MERN Stack": "MERN MongoDB Express React Node.js JavaScript fullstack web development",
            "MEAN Stack": "MEAN MongoDB Express Angular Node.js TypeScript fullstack framework",
            "MEVN Stack": "MEVN MongoDB Express Vue.js Node.js JavaScript frontend backend",
            "Flutter": "Flutter Dart mobile app development iOS Android cross-platform Bloc Riverpod",
            "React Native": "React Native mobile development JavaScript iOS Android Expo React",
            "Machine Learning": "Machine Learning AI deep learning neural network TensorFlow PyTorch scikit-learn Keras transformer LLM GPT model training",
            "Data Science": "Data Science analytics pandas numpy matplotlib visualization Jupyter notebook analysis statistics",
            "DevOps": "DevOps CI/CD Docker Kubernetes container orchestration AWS Azure GCP cloud infrastructure Terraform Ansible Jenkins automation",
            "Web3/Blockchain": "Web3 Blockchain Ethereum Solidity smart contract cryptocurrency NFT DeFi decentralized",
            "Modern Frontend": "Modern Frontend Next.js Vue.js Svelte Tailwind TypeScript React Vite SPA",
            "Backend Strong": "Backend API FastAPI Django Flask Spring Boot Node.js GraphQL REST microservices server",
            "Game Dev": "Game Development Unity Unreal Engine Godot pygame C++ C# graphics rendering",
            "Mobile Dev": "Mobile Development Android iOS Swift Kotlin native apps smartphone",
            "Full Stack": "Full Stack web development frontend backend database REST API responsive",
            "Cloud": "Cloud computing AWS Azure Google Cloud serverless lambda functions hosting deployment",
            "Security": "Security cybersecurity encryption authentication authorization vulnerability penetration testing",
            "IoT": "IoT Internet of Things embedded systems Arduino Raspberry Pi sensors hardware",
        }
        
        print("[EmbeddingService] Computing tech stack embeddings...")
        for name, description in tech_stack_descriptions.items():
            self._tech_stack_embeddings[name] = self.encode_text(description)
        print(f"[EmbeddingService] Initialized {len(self._tech_stack_embeddings)} tech stack embeddings")
    
    def classify_tech_stack_by_embedding(self, repo: Dict[str, Any], threshold: float = 0.3, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Classify repository tech stack using embedding similarity.
        
        Args:
            repo: Repository dict
            threshold: Minimum similarity score to include (0-1)
            top_k: Return top K most similar stacks
            
        Returns:
            List of dicts with 'name' and 'confidence' keys
        """
        if not self._tech_stack_embeddings:
            self.initialize_tech_stack_embeddings()
        
        repo_embedding = self.encode_repo(repo)
        
        similarities = []
        for stack_name, stack_embedding in self._tech_stack_embeddings.items():
            similarity = self.cosine_similarity(repo_embedding, stack_embedding)
            if similarity >= threshold:
                similarities.append({
                    "name": stack_name,
                    "confidence": float(similarity)
                })
        
        # Sort by confidence descending
        similarities.sort(key=lambda x: x["confidence"], reverse=True)
        
        return similarities[:top_k]
    
    def find_similar_repos(self, target_repo: Dict[str, Any], candidate_repos: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Find repositories similar to target repo.
        
        Args:
            target_repo: The reference repository
            candidate_repos: List of repositories to compare against
            top_k: Number of similar repos to return
            
        Returns:
            List of similar repos with similarity scores
        """
        target_embedding = self.encode_repo(target_repo)
        
        similarities = []
        for candidate in candidate_repos:
            # Skip if it's the same repo
            if candidate.get("id") == target_repo.get("id"):
                continue
            
            candidate_embedding = self.encode_repo(candidate)
            similarity = self.cosine_similarity(target_embedding, candidate_embedding)
            
            similarities.append({
                "repo": candidate,
                "similarity": float(similarity)
            })
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similarities[:top_k]
    
    @lru_cache(maxsize=1000)
    def get_cached_embedding(self, text: str) -> tuple:
        """
        Get embedding with caching (for frequently used texts).
        Returns tuple because numpy arrays aren't hashable for lru_cache.
        """
        embedding = self.encode_text(text)
        return tuple(embedding.tolist())
    
    def batch_encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode multiple texts at once (more efficient).
        
        Args:
            texts: List of text strings
            
        Returns:
            2D numpy array of embeddings
        """
        self._load_model()
        
        if self._model == "fallback":
            return np.array([self._simple_embedding(t) for t in texts])
        
        try:
            return self._model.encode(texts, convert_to_numpy=True)
        except Exception as e:
            print(f"[EmbeddingService] Batch encoding error: {e}")
            return np.array([self._simple_embedding(t) for t in texts])


# Global singleton instance
_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get global embedding service instance (singleton pattern)"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
