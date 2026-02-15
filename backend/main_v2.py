from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

# Import new ML services
from ml_service.features import FeatureExtractor
from ml_service.embeddings import get_embedding_service
from ml_service.classifiers import get_ml_classifiers
from ml_service.quality_scorer import QualityScorer
from ml_service.recommender import get_recommendation_engine
from ml_service.github_analyzer import get_github_analyzer
from cache import get_cache_manager

# Import Enhanced ML Classifier
try:
    from ml_service.enhanced_classifier import get_enhanced_classifier
    ENHANCED_ML_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Enhanced ML Classifier not available: {e}")
    ENHANCED_ML_AVAILABLE = False

# Import legacy service for backward compatibility
from ml_service import MLService

# Import RunAnywhere services (graceful failure if Docker not available)
try:
    from runanywhere.sandbox_manager import get_sandbox_manager
    from runanywhere.execution_controller import get_execution_controller
    from runanywhere.security_manager import get_security_manager
    RUNANYWHERE_AVAILABLE = True
except ImportError as e:
    print(f"⚠ RunAnywhere not available (missing docker package): {e}")
    RUNANYWHERE_AVAILABLE = False

# Import HackHub Analyzer services
try:
    from hackhub_analyzer.readme_validator import get_readme_validator
    from hackhub_analyzer.config_analyzer import get_config_analyzer
    from hackhub_analyzer.performance_profiler import get_performance_profiler
    from hackhub_analyzer.health_scorer import get_health_scorer
    HACKHUB_ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠ HackHub Analyzer not available: {e}")
    HACKHUB_ANALYZER_AVAILABLE = False

app = FastAPI(
    title="HackHub Complete - ML + RunAnywhere + Enhanced Analysis",
    version="3.0.0",
    description="Complete HackHub platform with ML-powered search, safe execution environment, and comprehensive repository analysis"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_API_URL = "https://api.github.com/search/repositories"

# Initialize ML services
embedding_service = get_embedding_service()
ml_classifiers = get_ml_classifiers()
recommender = get_recommendation_engine()
cache_manager = get_cache_manager()

# Initialize Enhanced ML Classifier (if available)
if ENHANCED_ML_AVAILABLE:
    enhanced_classifier = get_enhanced_classifier()
else:
    enhanced_classifier = None

# Initialize RunAnywhere services (if available)
if RUNANYWHERE_AVAILABLE:
    sandbox_manager = get_sandbox_manager()
    execution_controller = get_execution_controller()
    security_manager = get_security_manager()
else:
    sandbox_manager = None
    execution_controller = None
    security_manager = None

# Initialize HackHub Analyzer services (if available)
if HACKHUB_ANALYZER_AVAILABLE:
    readme_validator = get_readme_validator()
    config_analyzer = get_config_analyzer()
    performance_profiler = get_performance_profiler()
    health_scorer = get_health_scorer()
else:
    readme_validator = None
    config_analyzer = None
    performance_profiler = None
    health_scorer = None


class QualityScoreDetail(BaseModel):
    total_score: float
    documentation_score: float
    code_quality_score: float
    community_score: float
    maintenance_score: float
    grade: str


class TechStackConfidence(BaseModel):
    name: str
    confidence: float


class Repo(BaseModel):
    name: str
    full_name: str
    description: Optional[str]
    html_url: str
    stars: int
    forks: int
    language: Optional[str]
    topics: List[str]
    updated_at: str
    created_at: str
    pushed_at: str
    open_issues_count: int
    owner_avatar_url: Optional[str]
    # New Enhanced Fields
    status: str
    tech_stack: List[str]
    quality_score: Optional[float] = None
    quality_detail: Optional[QualityScoreDetail] = None
    tech_stack_confidence: Optional[List[TechStackConfidence]] = None


@app.get("/")
def read_root():
    return {
        "message": "HackHub Complete Platform v3.0", 
        "features": [
            "Advanced ML classification",
            "Semantic search with embeddings",
            "Quality scoring (0-100)",
            "20+ granular filters",
            "Smart recommendations",
            "Deep tech stack detection",
            "Safe code execution (RunAnywhere)" if RUNANYWHERE_AVAILABLE else None,
            "Repository testing & validation" if RUNANYWHERE_AVAILABLE else None,
            "Comprehensive health scoring" if HACKHUB_ANALYZER_AVAILABLE else None,
            "README validation" if HACKHUB_ANALYZER_AVAILABLE else None,
            "Configuration analysis" if HACKHUB_ANALYZER_AVAILABLE else None,
            "Performance profiling" if HACKHUB_ANALYZER_AVAILABLE else None
        ],
        "runanywhere_enabled": RUNANYWHERE_AVAILABLE,
        "docker_available": sandbox_manager.is_available() if RUNANYWHERE_AVAILABLE else False,
        "analyzer_enabled": HACKHUB_ANALYZER_AVAILABLE
    }


@app.get("/search", response_model=List[Repo])
async def search_repos(
    # Basic search
    q: str = "",
    
    # Star filters
    min_stars: int = 0,
    max_stars: Optional[int] = None,
    
    # Fork filters
    min_forks: int = 0,
    max_forks: Optional[int] = None,
    
    # Issue filters
    min_open_issues: Optional[int] = None,
    max_open_issues: Optional[int] = None,
    
    # Date filters
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    updated_after: Optional[str] = None,
    updated_before: Optional[str] = None,
    
    # Classification filters
    status: Optional[str] = None,
    tech_stack: Optional[str] = None,
    
    # Quality filter
    min_quality_score: int = 0,
    
    # License filter
    license: Optional[str] = None,
    
    # Boolean flags
    exclude_forks: bool = False,
    exclude_archived: bool = False,
    has_wiki: Optional[bool] = None,
    has_pages: Optional[bool] = None,
    
    # Multi-language filter (comma-separated)
    languages: Optional[str] = None,
    
    # Exclude patterns (comma-separated keywords)
    exclude_keywords: Optional[str] = None,
    
    # Sort options
    sort_by: str = "updated",  # updated, stars, forks, created, quality
    
    # Pagination
    per_page: int = 50,
    page: int = 1,
    
    # Use embeddings for semantic search
    use_embeddings: bool = False
):
    """
    Advanced GitHub repository search with ML-powered classification.
    
    NEW FEATURES:
    - 20+ granular filters (stars, forks, dates, quality, etc.)
    - Quality scoring (0-100)
    - Embedding-based semantic search
    - Multi-language filtering
    - Exclude patterns
    - Multiple sort options
    """
    
    # Check cache first
    cache_key = cache_manager._make_key(
        "search", q, min_stars, max_stars, status, tech_stack, 
        min_quality_score, sort_by, per_page, page
    )
    cached_result = cache_manager.get(cache_key)
    if cached_result:
        print(f"[Cache HIT] Returning cached results for query: {q}")
        return cached_result
    
    # Build GitHub query
    base_query = q.strip() if q.strip() else "stars:>0"
    
    # Use ML Service to enhance query with tech stack
    final_query = MLService.construct_github_query(base_query, tech_stack)
    
    # Add filters to GitHub API query
    if min_stars > 0:
        final_query += f" stars:>{min_stars}"
    if max_stars:
        final_query += f" stars:<{max_stars}"
    
    if min_forks > 0:
        final_query += f" forks:>{min_forks}"
    if max_forks:
        final_query += f" forks:<{max_forks}"
    
    if created_after:
        final_query += f" created:>={created_after}"
    if created_before:
        final_query += f" created:<={created_before}"
    
    if updated_after:
        final_query += f" pushed:>={updated_after}"
    if updated_before:
        final_query += f" pushed:<={updated_before}"
    
    if license:
        final_query += f" license:{license}"
    
    if exclude_forks:
        final_query += " fork:false"
    
    if exclude_archived:
        final_query += " archived:false"
    
    # Multi-language support
    if languages:
        lang_list = [l.strip() for l in languages.split(",")]
        lang_query = " OR ".join([f"language:{lang}" for lang in lang_list])
        final_query += f" ({lang_query})"
    
    print(f"[Search] GitHub Query: {final_query}")
    
    # Fetch from GitHub API
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                GITHUB_API_URL,
                params={
                    "q": final_query,
                    "sort": "updated" if sort_by == "updated" else sort_by,
                    "per_page": min(per_page, 100),
                    "page": page
                }
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="GitHub API timed out")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error contacting GitHub: {str(e)}")
    
    if response.status_code != 200:
        print(f"[Error] GitHub API: {response.status_code} - {response.text[:200]}")
        raise HTTPException(status_code=response.status_code, detail=f"GitHub API Error")
    
    data = response.json()
    items = data.get("items", [])
    
    print(f"[Search] Retrieved {len(items)} repos from GitHub")
    
    # Process and enhance each repository with ML
    results = []
    for item in items:
        try:
            # Extract features
            features = FeatureExtractor.extract_all_features(item)
            
            # Classify status using ML
            repo_status = ml_classifiers.predict_status(item)
            
            # Detect tech stack (keyword + embeddings hybrid)
            repo_stack = MLService.analyze_tech_stack(item)
            
            # Get embedding-based tech stack with confidence scores
            if use_embeddings:
                tech_conf = embedding_service.classify_tech_stack_by_embedding(item, threshold=0.25, top_k=3)
                # Merge with keyword-based detection
                for tc in tech_conf:
                    if tc["name"] not in repo_stack:
                        repo_stack.append(tc["name"])
            else:
                tech_conf = [{"name": ts, "confidence": 0.9} for ts in repo_stack]
            
            # Calculate quality score
            quality_result = QualityScorer.calculate_quality_score(item)
            quality_score = quality_result["total_score"]
            
            # Apply post-filters
            
            # Status filter
            if status and status.lower() != repo_status.lower():
                continue
            
            # Quality score filter
            if quality_score < min_quality_score:
                continue
            
            # Issue count filters
            if min_open_issues and item.get("open_issues_count", 0) < min_open_issues:
                continue
            if max_open_issues and item.get("open_issues_count", 0) > max_open_issues:
                continue
            
            # Wiki/Pages filters
            if has_wiki is not None and item.get("has_wiki") != has_wiki:
                continue
            if has_pages is not None and item.get("has_pages") != has_pages:
                continue
            
            # Exclude keywords filter
            if exclude_keywords:
                keywords = [k.strip().lower() for k in exclude_keywords.split(",")]
                desc = (item.get("description") or "").lower()
                name = item.get("name", "").lower()
                if any(kw in desc or kw in name for kw in keywords):
                    continue
            
            # Build repo response
            repo = Repo(
                name=item["name"],
                full_name=item["full_name"],
                description=item.get("description"),
                html_url=item["html_url"],
                stars=item["stargazers_count"],
                forks=item.get("forks_count", 0),
                language=item.get("language"),
                topics=item.get("topics", []),
                updated_at=item["updated_at"],
                created_at=item["created_at"],
                pushed_at=item["pushed_at"],
                open_issues_count=item.get("open_issues_count", 0),
                owner_avatar_url=item["owner"]["avatar_url"] if "owner" in item else None,
                status=repo_status,
                tech_stack=repo_stack,
                quality_score=round(quality_score, 2),
                quality_detail=QualityScoreDetail(**quality_result),
                tech_stack_confidence=[TechStackConfidence(**tc) for tc in tech_conf[:5]]
            )
            results.append(repo)
            
        except Exception as e:
            print(f"[Error] Processing repo {item.get('full_name', 'unknown')}: {e}")
            continue
    
    print(f"[Search] Returning {len(results)} repos after ML processing")
    
    # Sort results if needed
    if sort_by == "quality":
        results.sort(key=lambda r: r.quality_score or 0, reverse=True)
    elif sort_by == "stars":
        results.sort(key=lambda r: r.stars, reverse=True)
    elif sort_by == "forks":
        results.sort(key=lambda r: r.forks, reverse=True)
    
    # Limit to 30 results
    final_results = results[:30]
    
    # Cache results for 30 minutes
    cache_manager.set(cache_key, final_results, ttl_seconds=1800)
    
    return final_results


@app.get("/similar/{owner}/{repo}")
async def get_similar_repos(owner: str, repo: str, limit: int = 10):
    """
    Find repositories similar to the given repo using embeddings.
    """
    # Fetch target repo info
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"https://api.github.com/repos/{owner}/{repo}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Repository not found")
        
        target_repo = response.json()
        
        # Search for candidate repos in same language/topic
        language = target_repo.get("language", "")
        search_query = f"language:{language} stars:>10" if language else "stars:>100"
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                GITHUB_API_URL,
                params={"q": search_query, "per_page": 100}
            )
        
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Error searching GitHub")
        
        candidates = response.json().get("items", [])
        
        # Use recommender to find similar
        similar = recommender.find_similar_repos(target_repo, candidates, top_k=limit)
        
        return {
            "target": {"name": target_repo["full_name"], "description": target_repo.get("description")},
            "similar_repos": [
                {
                    "name": s["repo"]["full_name"],
                    "description": s["repo"].get("description"),
                    "stars": s["repo"]["stargazers_count"],
                    "similarity": round(s["similarity"], 3),
                    "html_url": s["repo"]["html_url"]
                }
                for s in similar
            ]
        }
        
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Request timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/trending")
async def get_trending(category: Optional[str] = None, limit: int = 20):
    """
    Get trending repositories (overall or by category).
    """
    # Fetch recent active repos
    query = f"pushed:>{datetime.now().strftime('%Y-%m-%d')} stars:>50"
    
    if category:
        # Map category to search query
        category_mapping = {
            "ml": "topic:machine-learning",
            "web": "topic:web OR topic:frontend",
            "mobile": "topic:mobile OR topic:android OR topic:ios",
            "data": "topic:data-science",
        }
        if category.lower() in category_mapping:
            query += f" {category_mapping[category.lower()]}"
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                GITHUB_API_URL,
                params={"q": query, "sort": "stars", "per_page": 50}
            )
        
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Error fetching trending repos")
        
        items = response.json().get("items", [])
        
        # Use recommender to calculate trending scores
        trending = recommender.get_trending_repos(items, top_k=limit)
        
        return {
            "category": category or "all",
            "count": len(trending),
            "repos": [
                {
                    "name": r["full_name"],
                    "description": r.get("description"),
                    "stars": r["stargazers_count"],
                    "language": r.get("language"),
                    "html_url": r["html_url"]
                }
                for r in trending
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/stats")
def get_stats():
    """Get service statistics"""
    return {
        "version": "3.0.0",
        "ml_models_loaded": ml_classifiers._models_trained,
        "embeddings_initialized": len(embedding_service._tech_stack_embeddings) > 0,
        "cache_size": len(cache_manager.cache),
        "enhanced_ml_available": ENHANCED_ML_AVAILABLE,
        "runanywhere_available": RUNANYWHERE_AVAILABLE,
        "analyzer_available": HACKHUB_ANALYZER_AVAILABLE,
        "features": {
            "filters": 20,
            "ml_algorithms": ["Random Forest", "Gradient Boosting", "MLP", "Embeddings", "Rule-Based"] if ENHANCED_ML_AVAILABLE else ["Random Forest", "Embeddings", "Rule-Based"],
            "quality_scoring": True,
            "recommendations": True,
            "semantic_search": True,
            "contribution_readiness": ENHANCED_ML_AVAILABLE,
            "tech_stack_verification": ENHANCED_ML_AVAILABLE
        }
    }


# ============================================================================
# ENHANCED ML ENDPOINTS (NEW in v3.0) - Advanced Filtering & Analysis
# ============================================================================

@app.get("/analyze/contribution-readiness")
async def analyze_contribution_readiness(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name")
):
    """
    Analyze how ready a repository is for contributions.
    
    Returns:
    - Contribution readiness score (0-100)
    - Grade (Excellent/Very Good/Good/Fair/Poor)
    - Factor breakdown
    - Actionable recommendations
    """
    if not ENHANCED_ML_AVAILABLE or not enhanced_classifier:
        raise HTTPException(
            status_code=503,
            detail="Enhanced ML features not available"
        )
    
    # Fetch repository data from GitHub
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                timeout=10.0
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Repository not found")
            
            repo_data = response.json()
            
            # Calculate contribution readiness
            readiness = enhanced_classifier.calculate_contribution_readiness(repo_data)
            
            return {
                "repository": f"{owner}/{repo}",
                "contribution_readiness": readiness,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"GitHub API error: {str(e)}")


@app.post("/analyze/bulk-contribution-readiness")
async def bulk_analyze_contribution_readiness(repos: List[Dict[str, Any]]):
    """
    Analyze contribution readiness for multiple repositories at once.
    
    Input: List of repository data objects
    Returns: List of contribution readiness scores
    """
    if not ENHANCED_ML_AVAILABLE or not enhanced_classifier:
        raise HTTPException(
            status_code=503,
            detail="Enhanced ML features not available"
        )
    
    results = []
    
    for repo_data in repos:
        try:
            readiness = enhanced_classifier.calculate_contribution_readiness(repo_data)
            results.append({
                "repository": repo_data.get('full_name', 'unknown'),
                "contribution_readiness": readiness
            })
        except Exception as e:
            results.append({
                "repository": repo_data.get('full_name', 'unknown'),
                "error": str(e)
            })
    
    return {
        "total_analyzed": len(results),
        "results": results
    }


@app.get("/verify/tech-stack")
async def verify_tech_stack(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
    tech_stack: str = Query(..., description="Comma-separated tech stack to verify")
):
    """
    Verify if detected tech stack actually matches the repository.
    
    Returns accuracy score and confidence level.
    """
    if not ENHANCED_ML_AVAILABLE or not enhanced_classifier:
        raise HTTPException(
            status_code=503,
            detail="Enhanced ML features not available"
        )
    
    # Fetch repository data
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://api.github.com/repos/{owner}/{repo}",
                timeout=10.0
            )
            
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="Repository not found")
            
            repo_data = response.json()
            detected_stack = [t.strip() for t in tech_stack.split(',')]
            
            # Verify tech stack
            verification = enhanced_classifier.verify_tech_stack_accuracy(
                repo_data, 
                detected_stack
            )
            
            return {
                "repository": f"{owner}/{repo}",
                "verification": verification,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"GitHub API error: {str(e)}")


@app.get("/filter/needs-contributors")
async def filter_repositories_needing_contributors(
    min_quality_score: int = Query(50, ge=0, le=100),
    min_contribution_readiness: int = Query(60, ge=0, le=100),
    tech_stack: Optional[str] = Query(None, description="Filter by tech stack"),
    per_page: int = Query(10, ge=1, le=50)
):
    """
    Find repositories that genuinely need contributors.
    
    Filters based on:
    - Good quality (maintained, documented)
    - High contribution readiness
    - Active but not too popular
    - Has manageable number of issues
    """
    if not ENHANCED_ML_AVAILABLE or not enhanced_classifier:
        raise HTTPException(
            status_code=503,
            detail="Enhanced ML features not available"
        )
    
    # Build GitHub search query
    query_parts = []
    
    # Active repositories
    query_parts.append("pushed:>2024-01-01")
    
    # Has issues (shows activity and contribution opportunities)
    query_parts.append("good-first-issues:>0")
    
    # Not too popular (easier for new contributors)
    query_parts.append("stars:10..1000")
    
    # Has license
    query_parts.append("license:mit OR license:apache-2.0")
    
    # Tech stack filter
    if tech_stack:
        for tech in tech_stack.split(','):
            query_parts.append(f"language:{tech.strip()}")
    
    search_query = " ".join(query_parts)
    
    # Search GitHub
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                GITHUB_API_URL,
                params={
                    'q': search_query,
                    'sort': 'updated',
                    'order': 'desc',
                    'per_page': per_page * 2  # Get more to filter
                },
                timeout=30.0
            )
            
            repos_data = response.json().get('items', [])
            
            # Filter by contribution readiness
            filtered_repos = []
            
            for repo_data in repos_data:
                # Calculate contribution readiness
                readiness = enhanced_classifier.calculate_contribution_readiness(repo_data)
                
                if readiness['score'] >= min_contribution_readiness:
                    filtered_repos.append({
                        "name": repo_data.get('name'),
                        "full_name": repo_data.get('full_name'),
                        "description": repo_data.get('description'),
                        "html_url": repo_data.get('html_url'),
                        "stars": repo_data.get('stargazers_count', 0),
                        "language": repo_data.get('language'),
                        "open_issues": repo_data.get('open_issues_count', 0),
                        "contribution_readiness": readiness
                    })
                
                if len(filtered_repos) >= per_page:
                    break
            
            return {
                "total_found": len(filtered_repos),
                "repositories": filtered_repos
            }
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"GitHub API error: {str(e)}")


@app.get("/recommendations/by-skill-level")
async def recommend_by_skill_level(
    skill_level: str = Query(..., description="beginner, intermediate, or advanced"),
    tech_stack: Optional[str] = Query(None, description="Preferred technologies"),
    per_page: int = Query(10, ge=1, le=30)
):
    """
    Recommend repositories based on user's skill level.
    
    - Beginner: Well-documented, active, simple tech stack, good first issues
    - Intermediate: Moderate complexity, established projects
    - Advanced: Complex projects, cutting-edge tech
    """
    if skill_level.lower() not in ['beginner', 'intermediate', 'advanced']:
        raise HTTPException(
            status_code=400,
            detail="skill_level must be 'beginner', 'intermediate', or 'advanced'"
        )
    
    # Build search query based on skill level
    if skill_level.lower() == 'beginner':
        query = "good-first-issues:>2 stars:50..500 pushed:>2024-06-01"
    elif skill_level.lower() == 'intermediate':
        query = "stars:500..5000 forks:>10 pushed:>2024-01-01"
    else:  # advanced
        query = "stars:>5000 forks:>50 pushed:>2023-01-01"
    
    if tech_stack:
        techs = [t.strip() for t in tech_stack.split(',')]
        query += f" language:{techs[0]}"
    
    # Search GitHub
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                GITHUB_API_URL,
                params={
                    'q': query,
                    'sort': 'updated',
                    'order': 'desc',
                    'per_page': per_page
                },
                timeout=30.0
            )
            
            repos_data = response.json().get('items', [])
            
            recommendations = []
            for repo_data in repos_data:
                # Get enhanced status
                if ENHANCED_ML_AVAILABLE and enhanced_classifier:
                    status, confidence = enhanced_classifier.predict_status_accurate(repo_data)
                else:
                    status = "Unknown"
                    confidence = 0.0
                
                recommendations.append({
                    "name": repo_data.get('name'),
                    "full_name": repo_data.get('full_name'),
                    "description": repo_data.get('description'),
                    "html_url": repo_data.get('html_url'),
                    "stars": repo_data.get('stargazers_count', 0),
                    "language": repo_data.get('language'),
                    "status": status,
                    "status_confidence": confidence,
                    "skill_match": skill_level
                })
            
            return {
                "skill_level": skill_level,
                "total_found": len(recommendations),
                "recommendations": recommendations
            }
            
        except httpx.HTTPError as e:
            raise HTTPException(status_code=500, detail=f"GitHub API error: {str(e)}")


# ============================================================================
# RUNANYWHERE EXECUTION ENDPOINTS (NEW in v3.0)
# ============================================================================

class CodeExecutionRequest(BaseModel):
    code: str
    language: str
    timeout: Optional[int] = 30


class RepositoryExecutionRequest(BaseModel):
    repo_url: str
    repo_data: Dict[str, Any]
    timeout: Optional[int] = 300


@app.post("/execute/code")
async def execute_code(request: CodeExecutionRequest):
    """Execute code snippet in a safe sandbox (requires Docker)"""
    if not RUNANYWHERE_AVAILABLE or not execution_controller:
        raise HTTPException(
            status_code=503,
            detail="RunAnywhere not available. Install: pip install docker"
        )
    
    if not sandbox_manager.is_available():
        raise HTTPException(
            status_code=503,
            detail="Docker not available. Please start Docker Desktop."
        )
    
    # Validate code for security
    validation = security_manager.validate_code(
        code=request.code,
        language=request.language,
        strict_mode=True
    )
    
    if not validation["is_safe"]:
        return {
            "status": "rejected",
            "error": "Code contains potentially dangerous patterns",
            "validation": validation,
            "stdout": "",
            "stderr": ""
        }
    
    # Execute in sandbox
    result = await execution_controller.execute_code_snippet(
        code=request.code,
        language=request.language,
        timeout=request.timeout
    )
    
    return result


@app.post("/execute/repository")
async def execute_repository(request: RepositoryExecutionRequest, background_tasks: BackgroundTasks):
    """Execute a repository (clone, install, build, test) in sandbox"""
    if not RUNANYWHERE_AVAILABLE or not execution_controller:
        raise HTTPException(
            status_code=503,
            detail="RunAnywhere not available. Install: pip install docker"
        )
    
    if not sandbox_manager.is_available():
        raise HTTPException(
            status_code=503,
            detail="Docker not available. Please start Docker Desktop."
        )
    
    # Validate repository URL
    if not security_manager.validate_repository_url(request.repo_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid or unsafe repository URL"
        )
    
    # Execute repository
    result = await execution_controller.execute_repository(
        repo_url=request.repo_url,
        repo_data=request.repo_data,
        timeout=request.timeout
    )
    
    # Schedule cleanup in background
    background_tasks.add_task(sandbox_manager.cleanup_expired_sandboxes)
    
    return result


@app.get("/execute/analyze")
async def analyze_repository_executability(
    owner: str = Query(..., description="Repository owner"),
    repo: str = Query(..., description="Repository name"),
):
    """Analyze if a repository can be executed"""
    if not RUNANYWHERE_AVAILABLE or not execution_controller:
        raise HTTPException(
            status_code=503,
            detail="RunAnywhere not available"
        )
    
    repo_data = {
        "name": repo,
        "owner": owner,
        "full_name": f"{owner}/{repo}"
    }
    
    analysis = await execution_controller.analyze_repository_executability(repo_data)
    return analysis


@app.get("/execute/history")
async def get_execution_history(limit: int = Query(10, ge=1, le=100)):
    """Get recent execution history"""
    if not RUNANYWHERE_AVAILABLE or not execution_controller:
        raise HTTPException(status_code=503, detail="RunAnywhere not available")
    
    history = execution_controller.get_execution_history(limit=limit)
    return {"history": history, "count": len(history)}


@app.get("/execute/status/{execution_id}")
async def get_execution_status(execution_id: str):
    """Get status of a specific execution"""
    if not RUNANYWHERE_AVAILABLE or not execution_controller:
        raise HTTPException(status_code=503, detail="RunAnywhere not available")
    
    result = execution_controller.get_execution_result(execution_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return result


# ============================================================================
# HACKHUB ANALYZER ENDPOINTS (NEW in v3.0)
# ============================================================================

@app.post("/analyze/readme")
async def analyze_readme(readme_content: str, repo_data: Dict[str, Any]):
    """Validate README instructions and analyze quality"""
    if not HACKHUB_ANALYZER_AVAILABLE or not readme_validator:
        raise HTTPException(status_code=503, detail="HackHub Analyzer not available")
    
    quality_analysis = readme_validator.analyze_readme_quality(readme_content)
    
    return {
        "quality_analysis": quality_analysis,
        "validation_available": RUNANYWHERE_AVAILABLE and sandbox_manager and sandbox_manager.is_available(),
        "recommendations": []
    }


@app.post("/analyze/config")
async def analyze_configuration(repo_data: Dict[str, Any], files: Optional[Dict[str, str]] = None):
    """Analyze project configuration files"""
    if not HACKHUB_ANALYZER_AVAILABLE or not config_analyzer:
        raise HTTPException(status_code=503, detail="HackHub Analyzer not available")
    
    analysis = config_analyzer.analyze_configurations(repo_data, files or {})
    return analysis


@app.post("/analyze/performance")
async def analyze_performance(repo_data: Dict[str, Any], execution_result: Optional[Dict[str, Any]] = None):
    """Profile repository performance"""
    if not HACKHUB_ANALYZER_AVAILABLE or not performance_profiler:
        raise HTTPException(status_code=503, detail="HackHub Analyzer not available")
    
    profile = performance_profiler.profile_repository(repo_data, execution_result)
    return profile


class HealthAnalysisRequest(BaseModel):
    repo_data: Dict[str, Any]
    readme_content: Optional[str] = None
    include_execution: Optional[bool] = False


@app.post("/analyze/health")
async def analyze_health(request: HealthAnalysisRequest):
    """Calculate comprehensive repository health score"""
    if not HACKHUB_ANALYZER_AVAILABLE or not health_scorer:
        raise HTTPException(status_code=503, detail="HackHub Analyzer not available")
    
    readme_analysis = None
    config_analysis = None
    performance_profile = None
    execution_result = None
    
    # Analyze README if provided
    if request.readme_content and readme_validator:
        readme_analysis = readme_validator.analyze_readme_quality(request.readme_content)
    
    # Analyze configuration
    if config_analyzer:
        config_analysis = config_analyzer.analyze_configurations(request.repo_data, {})
    
    # Profile performance
    if performance_profiler:
        performance_profile = performance_profiler.profile_repository(request.repo_data)
    
    # Execute if requested and Docker is available
    if request.include_execution and RUNANYWHERE_AVAILABLE and sandbox_manager and sandbox_manager.is_available():
        repo_url = request.repo_data.get("html_url", "")
        if repo_url and execution_controller:
            execution_result = await execution_controller.execute_repository(
                repo_url=repo_url,
                repo_data=request.repo_data,
                timeout=300
            )
    
    # Calculate comprehensive health score
    health_score = health_scorer.calculate_health_score(
        repo_data=request.repo_data,
        quality_detail=request.repo_data.get("quality_detail"),
        readme_analysis=readme_analysis,
        config_analysis=config_analysis,
        performance_profile=performance_profile,
        execution_result=execution_result
    )
    
    return health_score


# ============================================================================
# SANDBOX MANAGEMENT ENDPOINTS (NEW in v3.0)
# ============================================================================

@app.get("/sandbox/list")
async def list_sandboxes():
    """List all active sandboxes"""
    if not RUNANYWHERE_AVAILABLE or not sandbox_manager:
        raise HTTPException(status_code=503, detail="RunAnywhere not available")
    
    sandboxes = sandbox_manager.get_active_sandboxes()
    return {"sandboxes": sandboxes, "count": len(sandboxes)}


@app.post("/sandbox/cleanup")
async def cleanup_sandboxes():
    """Cleanup expired sandboxes"""
    if not RUNANYWHERE_AVAILABLE or not sandbox_manager:
        raise HTTPException(status_code=503, detail="RunAnywhere not available")
    
    cleaned = await sandbox_manager.cleanup_expired_sandboxes()
    return {"cleaned": cleaned, "message": f"Cleaned up {cleaned} expired sandboxes"}


@app.get("/sandbox/stats/{sandbox_id}")
async def get_sandbox_stats(sandbox_id: str):
    """Get resource usage statistics for a sandbox"""
    if not RUNANYWHERE_AVAILABLE or not sandbox_manager:
        raise HTTPException(status_code=503, detail="RunAnywhere not available")
    
    stats = await sandbox_manager.get_sandbox_stats(sandbox_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    return stats


@app.get("/health")
async def health_check():
    """Complete system health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "services": {
            "ml_services": True,
            "embedding_service": True,
            "runanywhere": RUNANYWHERE_AVAILABLE,
            "docker": sandbox_manager.is_available() if RUNANYWHERE_AVAILABLE and sandbox_manager else False,
            "hackhub_analyzer": HACKHUB_ANALYZER_AVAILABLE
        },
        "active_sandboxes": len(sandbox_manager.get_active_sandboxes()) if RUNANYWHERE_AVAILABLE and sandbox_manager else 0,
        "features": {
            "search": True,
            "quality_scoring": True,
            "recommendations": True,
            "semantic_search": True,
            "code_execution": RUNANYWHERE_AVAILABLE and (sandbox_manager.is_available() if sandbox_manager else False),
            "repository_testing": RUNANYWHERE_AVAILABLE and (sandbox_manager.is_available() if sandbox_manager else False),
            "health_scoring": HACKHUB_ANALYZER_AVAILABLE,
            "readme_validation": HACKHUB_ANALYZER_AVAILABLE,
            "config_analysis": HACKHUB_ANALYZER_AVAILABLE,
            "performance_profiling": HACKHUB_ANALYZER_AVAILABLE
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("=" * 70)
    print(" HackHub Complete Platform v3.0")
    print(" ML + RunAnywhere + Enhanced Analysis")
    print("=" * 70)
    print("Initializing services...")
    
    # Initialize embedding service in background
    try:
        embedding_service.initialize_tech_stack_embeddings()
        print("✓ ML & Embedding services ready")
    except Exception as e:
        print(f"⚠ Embedding service initialization warning: {e}")
    
    # Check RunAnywhere status
    if RUNANYWHERE_AVAILABLE:
        if sandbox_manager and sandbox_manager.is_available():
            print("✓ RunAnywhere ready (Docker available)")
        else:
            print("⚠ RunAnywhere loaded but Docker not available")
            print("  Install Docker Desktop for execution features")
    else:
        print("⚠ RunAnywhere not available")
        print("  Install: pip install docker")
    
    # Check HackHub Analyzer status
    if HACKHUB_ANALYZER_AVAILABLE:
        print("✓ HackHub Analyzer ready")
    else:
        print("⚠ HackHub Analyzer not available")
    
    print("=" * 70)
    print("✓ All available services ready!")
    print("\nStarting server on http://0.0.0.0:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Health Check: http://localhost:8000/health")
    print("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
