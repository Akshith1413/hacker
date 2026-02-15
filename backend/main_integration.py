"""
RunAnywhere + HackHub Integration API

New endpoints for safe execution environment and enhanced repository analysis.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import RunAnywhere services
from runanywhere.sandbox_manager import get_sandbox_manager
from runanywhere.execution_controller import get_execution_controller
from runanywhere.security_manager import get_security_manager

# Import HackHub Analyzer services
from hackhub_analyzer.readme_validator import get_readme_validator
from hackhub_analyzer.config_analyzer import get_config_analyzer
from hackhub_analyzer.performance_profiler import get_performance_profiler
from hackhub_analyzer.health_scorer import get_health_scorer

# Create extension app
app_extension = FastAPI(
    title="RunAnywhere + HackHub Integration API",
    version="1.0.0",
    description="Safe execution environment and enhanced repository analysis"
)

# CORS
app_extension.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
sandbox_manager = get_sandbox_manager()
execution_controller = get_execution_controller()
security_manager = get_security_manager()
readme_validator = get_readme_validator()
config_analyzer = get_config_analyzer()
performance_profiler = get_performance_profiler()
health_scorer = get_health_scorer()


# ============================================================================
# Request/Response Models
# ============================================================================

class CodeExecutionRequest(BaseModel):
    code: str
    language: str
    timeout: Optional[int] = 30


class RepositoryExecutionRequest(BaseModel):
    repo_url: str
    repo_data: Dict[str, Any]
    timeout: Optional[int] = 300


class HealthAnalysisRequest(BaseModel):
    repo_data: Dict[str, Any]
    readme_content: Optional[str] = None
    include_execution: Optional[bool] = False


# ============================================================================
# RunAnywhere Execution Endpoints
# ============================================================================

@app_extension.get("/")
async def root():
    """API information"""
    return {
        "service": "RunAnywhere + HackHub Integration",
        "version": "1.0.0",
        "features": [
            "Safe code execution in sandboxes",
            "Repository build and test automation",
            "README instruction validation",
            "Configuration analysis",
            "Performance profiling",
            "Comprehensive health scoring"
        ],
        "docker_available": sandbox_manager.is_available(),
        "active_sandboxes": len(sandbox_manager.get_active_sandboxes())
    }


@app_extension.post("/execute/code")
async def execute_code(request: CodeExecutionRequest):
    """
    Execute code snippet in a safe sandbox environment.
    
    Args:
        code: Code to execute
        language: Programming language (python, javascript, java, etc.)
        timeout: Execution timeout in seconds
        
    Returns:
        Execution results with stdout, stderr, and status
    """
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


@app_extension.post("/execute/repository")
async def execute_repository(request: RepositoryExecutionRequest, background_tasks: BackgroundTasks):
    """
    Execute a repository in a sandbox (clone, install, build, test).
    
    Args:
        repo_url: GitHub repository URL
        repo_data: Repository metadata
        timeout: Execution timeout in seconds
        
    Returns:
        Execution results with logs and status
    """
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


@app_extension.get("/execute/analyze")
async def analyze_repository_executability(
    owner: str,
    repo: str,
    repo_data: Optional[Dict[str, Any]] = None
):
    """
    Analyze if a repository can be executed and extract setup instructions.
    
    Args:
        owner: Repository owner
        repo: Repository name
        repo_data: Optional repository metadata
        
    Returns:
        Analysis with executability, runtime, commands, etc.
    """
    if not repo_data:
        # Minimal repo data for analysis
        repo_data = {
            "name": repo,
            "owner": owner,
            "full_name": f"{owner}/{repo}"
        }
    
    analysis = await execution_controller.analyze_repository_executability(repo_data)
    
    return analysis


@app_extension.get("/execute/history")
async def get_execution_history(limit: int = 10):
    """Get recent execution history"""
    history = execution_controller.get_execution_history(limit=limit)
    return {"history": history}


@app_extension.get("/execute/status/{execution_id}")
async def get_execution_status(execution_id: str):
    """Get status of a specific execution"""
    result = execution_controller.get_execution_result(execution_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    return result


# ============================================================================
# HackHub Analysis Endpoints
# ============================================================================

@app_extension.post("/analyze/readme")
async def analyze_readme(
    readme_content: str,
    repo_data: Dict[str, Any]
):
    """
    Validate README instructions and analyze quality.
    
    Args:
        readme_content: README markdown content
        repo_data: Repository metadata
        
    Returns:
        Validation results with scores and issues
    """
    # Quality analysis (fast, no execution)
    quality_analysis = readme_validator.analyze_readme_quality(readme_content)
    
    # Full validation (optional, requires execution)
    # validation = await readme_validator.validate_readme(readme_content, repo_data)
    
    return {
        "quality_analysis": quality_analysis,
        "validation_available": False,  # Set to True when Docker is available
        "recommendations": []
    }


@app_extension.post("/analyze/config")
async def analyze_configuration(
    repo_data: Dict[str, Any],
    files: Optional[Dict[str, str]] = None
):
    """
    Analyze project configuration files.
    
    Args:
        repo_data: Repository metadata
        files: Dict of filename -> content
        
    Returns:
        Configuration analysis with scores and issues
    """
    analysis = config_analyzer.analyze_configurations(repo_data, files or {})
    
    return analysis


@app_extension.post("/analyze/performance")
async def analyze_performance(
    repo_data: Dict[str, Any],
    execution_result: Optional[Dict[str, Any]] = None
):
    """
    Profile repository performance.
    
    Args:
        repo_data: Repository metadata
        execution_result: Optional execution results
        
    Returns:
        Performance profile with metrics and optimizations
    """
    profile = performance_profiler.profile_repository(repo_data, execution_result)
    
    return profile


@app_extension.post("/analyze/health")
async def analyze_health(request: HealthAnalysisRequest):
    """
    Calculate comprehensive repository health score.
    
    Args:
        repo_data: Repository metadata
        readme_content: Optional README content
        include_execution: Whether to include execution testing
        
    Returns:
        Comprehensive health score and recommendations
    """
    readme_analysis = None
    config_analysis = None
    performance_profile = None
    execution_result = None
    
    # Analyze README if provided
    if request.readme_content:
        readme_analysis = readme_validator.analyze_readme_quality(request.readme_content)
    
    # Analyze configuration
    config_analysis = config_analyzer.analyze_configurations(request.repo_data, {})
    
    # Profile performance
    performance_profile = performance_profiler.profile_repository(request.repo_data)
    
    # Execute if requested and Docker is available
    if request.include_execution and sandbox_manager.is_available():
        repo_url = request.repo_data.get("html_url", "")
        if repo_url:
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
# Sandbox Management Endpoints
# ============================================================================

@app_extension.get("/sandbox/list")
async def list_sandboxes():
    """List all active sandboxes"""
    sandboxes = sandbox_manager.get_active_sandboxes()
    return {"sandboxes": sandboxes, "count": len(sandboxes)}


@app_extension.post("/sandbox/cleanup")
async def cleanup_sandboxes():
    """Cleanup expired sandboxes"""
    cleaned = await sandbox_manager.cleanup_expired_sandboxes()
    return {"cleaned": cleaned, "message": f"Cleaned up {cleaned} expired sandboxes"}


@app_extension.get("/sandbox/stats/{sandbox_id}")
async def get_sandbox_stats(sandbox_id: str):
    """Get resource usage statistics for a sandbox"""
    stats = await sandbox_manager.get_sandbox_stats(sandbox_id)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    
    return stats


# ============================================================================
# Health Check
# ============================================================================

@app_extension.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "sandbox_manager": sandbox_manager.is_available(),
            "execution_controller": True,
            "security_manager": True,
            "readme_validator": True,
            "config_analyzer": True,
            "performance_profiler": True,
            "health_scorer": True
        },
        "active_sandboxes": len(sandbox_manager.get_active_sandboxes())
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_extension, host="0.0.0.0", port=8001)
