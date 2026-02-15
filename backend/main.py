from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from typing import List, Optional
from pydantic import BaseModel
from ml_service import MLService

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GITHUB_API_URL = "https://api.github.com/search/repositories"


class Repo(BaseModel):
    name: str
    full_name: str
    description: Optional[str]
    html_url: str
    stars: int
    language: Optional[str]
    topics: List[str]
    updated_at: str
    created_at: str
    pushed_at: str
    open_issues_count: int
    owner_avatar_url: Optional[str]
    # New Fields
    status: str
    tech_stack: List[str]

@app.get("/")
def read_root():
    return {"message": "HackHub Backend is running!"}

@app.get("/search", response_model=List[Repo])
async def search_repos(
    q: str = "", 
    min_stars: int = 0, 
    status: Optional[str] = None, 
    tech_stack: Optional[str] = None
):
    # 1. 'Smart Search' Query Construction
    # If query is empty, use a sensible default so GitHub doesn't reject it
    base_query = q.strip() if q.strip() else "stars:>0"
    
    # We let MLService build the query based on the tech stack
    final_query = MLService.construct_github_query(base_query, tech_stack)
    
    if min_stars > 0:
        final_query += f" stars:>{min_stars}"
        
    # debug print
    print(f"Searching GitHub with: {final_query}")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                GITHUB_API_URL,
                params={
                    "q": final_query,
                    "sort": "updated",
                    "per_page": 50
                }
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="GitHub API timed out")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error contacting GitHub: {str(e)}")
        
    if response.status_code != 200:
        print(f"GitHub API Error: {response.status_code} - {response.text}")
        raise HTTPException(status_code=response.status_code, detail=f"GitHub API Error: {response.text[:200]}")
        
    data = response.json()
    items = data.get("items", [])
    
    # 2. 'ML' Classification & Filtering
    results = []
    for item in items:
        try:
            # Heuristic Classification
            repo_status = MLService.classify_status(item)
            repo_stack = MLService.analyze_tech_stack(item)
            
            # Filter by Status if requested
            if status:
                 # Normalize status string comparison
                 if status.lower() != repo_status.lower():
                     continue

            repo = Repo(
                name=item["name"],
                full_name=item["full_name"],
                description=item.get("description"),
                html_url=item["html_url"],
                stars=item["stargazers_count"],
                language=item.get("language"),
                topics=item.get("topics", []),
                updated_at=item["updated_at"],
                created_at=item["created_at"],
                pushed_at=item["pushed_at"],
                open_issues_count=item.get("open_issues_count", 0),
                owner_avatar_url=item["owner"]["avatar_url"] if "owner" in item else None,
                status=repo_status,
                tech_stack=repo_stack
            )
            results.append(repo)
        except Exception as e:
            print(f"Skipping repo due to error: {e}")
            continue
        
    return results[:30]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
