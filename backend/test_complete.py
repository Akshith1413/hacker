"""
Complete Integration Test for HackHub v3.0

Tests all features: ML search, RunAnywhere execution, and HackHub analysis.
Works even if Docker is not available (gracefully skips execution tests).
"""

import asyncio
import httpx
import sys

BASE_URL = "http://localhost:8000"


async def test_server_health():
    """Test 0: Check if server is running and healthy"""
    print("\n" + "="*70)
    print("TEST 0: Server Health Check")
    print("="*70)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Server is healthy (v{data.get('version', 'unknown')})")
                print(f"\nServices Status:")
                for service, status in data.get('services', {}).items():
                    icon = "✓" if status else "✗"
                    print(f"  {icon} {service}: {status}")
                
                print(f"\nFeatures Available:")
                for feature, available in data.get('features', {}).items():
                    icon = "✓" if available else "✗"
                    print(f"  {icon} {feature.replace('_', ' ').title()}: {available}")
                
                print(f"\nActive Sandboxes: {data.get('active_sandboxes', 0)}")
                return True, data
            else:
                print(f"✗ Server returned status {response.status_code}")
                return False, None
                
    except httpx.ConnectError:
        print("✗ Cannot connect to server at http://localhost:8000")
        print("\nPlease start the server first:")
        print("  cd backend")
        print("  python -m uvicorn main_v2:app --host 0.0.0.0 --port 8000")
        print("\nOr use the startup script:")
        print("  run_backend.bat")
        return False, None
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False, None


async def test_root_endpoint():
    """Test 1: Check root endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Root Endpoint")
    print("="*70)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ {data.get('message', 'Success')}")
                print(f"\nFeatures:")
                for feature in data.get('features', []):
                    if feature:  # Skip None values
                        print(f"  • {feature}")
                
                print(f"\nRunAnywhere Enabled: {data.get('runanywhere_enabled', False)}")
                print(f"Docker Available: {data.get('docker_available', False)}")
                print(f"Analyzer Enabled: {data.get('analyzer_enabled', False)}")
                return True
            else:
                print(f"✗ Failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_ml_search():
    """Test 2: ML-powered search"""
    print("\n" + "="*70)
    print("TEST 2: ML-Powered Repository Search")
    print("="*70)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/search",
                params={
                    "q": "machine learning",
                    "min_stars": 100,
                    "per_page": 5
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                repos = response.json()
                print(f"✓ Found {len(repos)} repositories")
                
                if repos:
                    print(f"\nTop Result:")
                    repo = repos[0]
                    print(f"  Name: {repo['name']}")
                    print(f"  Stars: {repo['stars']}")
                    print(f"  Language: {repo.get('language', 'N/A')}")
                    print(f"  Status: {repo.get('status', 'N/A')}")
                    print(f"  Quality Score: {repo.get('quality_score', 'N/A')}")
                    print(f"  Tech Stack: {', '.join(repo.get('tech_stack', []))}")
                
                return True
            else:
                print(f"✗ Search failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_code_execution(health_data):
    """Test 3: Code execution (requires Docker)"""
    print("\n" + "="*70)
    print("TEST 3: Code Execution")
    print("="*70)
    
    # Check if feature is available
    features = health_data.get('features', {})
    if not features.get('code_execution', False):
        print("⊘ Skipped - Code execution not available")
        print("  Reason: Docker not available or RunAnywhere not installed")
        print("  Install Docker Desktop to enable this feature")
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/execute/code",
                json={
                    "code": "for i in range(5): print(f'Number {i}')",
                    "language": "python",
                    "timeout": 30
                },
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"Status: {result.get('status', 'unknown')}")
                print(f"Execution Time: {result.get('execution_time', 0):.3f}s")
                
                if result.get('stdout'):
                    print(f"\nOutput:\n{result['stdout']}")
                
                if result.get('stderr'):
                    print(f"\nErrors:\n{result['stderr']}")
                
                return result.get('status') == 'success'
            else:
                print(f"✗ Execution failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_readme_analysis():
    """Test 4: README analysis"""
    print("\n" + "="*70)
    print("TEST 4: README Quality Analysis")
    print("="*70)
    
    readme_content = """
# Awesome Project

A comprehensive guide to building great software.

## Installation

```bash
npm install awesome-project
```

## Usage

```javascript
const awesome = require('awesome-project');
awesome.doSomething();
```

## Features

- Easy to use
- Well documented
- Active development

## License

MIT
"""
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/analyze/readme",
                json={
                    "readme_content": readme_content,
                    "repo_data": {"name": "test-repo"}
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                qa = result.get('quality_analysis', {})
                
                print(f"✓ README analyzed successfully")
                print(f"\nQuality Score: {qa.get('quality_score', 0):.0f}/100")
                print(f"Word Count: {qa.get('word_count', 0)}")
                print(f"Code Blocks: {qa.get('code_block_count', 0)}")
                print(f"Has Installation: {qa.get('has_installation', False)}")
                print(f"Has Usage: {qa.get('has_usage', False)}")
                print(f"Has License: {qa.get('has_license', False)}")
                
                return qa.get('quality_score', 0) > 50
            elif response.status_code == 503:
                print("⊘ Skipped - HackHub Analyzer not available")
                return None
            else:
                print(f"✗ Analysis failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_performance_profiling():
    """Test 5: Performance profiling"""
    print("\n" + "="*70)
    print("TEST 5: Performance Profiling")
    print("="*70)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/analyze/performance",
                json={
                    "repo_data": {
                        "name": "test-project",
                        "language": "Python",
                        "tech_stack": ["python", "django"],
                        "stars": 500,
                        "size": 50000
                    }
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✓ Performance profiled successfully")
                print(f"\nOverall Score: {result.get('overall_score', 0):.0f}/100")
                print(f"Performance Grade: {result.get('performance_grade', 'N/A')}")
                print(f"Estimated Install Time: {result.get('install_time_seconds', 0):.1f}s")
                print(f"Estimated Build Time: {result.get('build_time_seconds', 0):.1f}s")
                print(f"Code Complexity: {result.get('code_complexity', 'unknown')}")
                
                bottlenecks = result.get('bottlenecks', [])
                if bottlenecks:
                    print(f"\nBottlenecks: {len(bottlenecks)}")
                    for bn in bottlenecks[:2]:
                        print(f"  - {bn.get('message', 'Unknown')}")
                
                return result.get('overall_score', 0) > 0
            elif response.status_code == 503:
                print("⊘ Skipped - HackHub Analyzer not available")
                return None
            else:
                print(f"✗ Profiling failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_health_scoring():
    """Test 6: Comprehensive health scoring"""
    print("\n" + "="*70)
    print("TEST 6: Comprehensive Health Scoring")
    print("="*70)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/analyze/health",
                json={
                    "repo_data": {
                        "name": "great-project",
                        "language": "Python",
                        "tech_stack": ["python", "fastapi"],
                        "stars": 2000,
                        "forks": 300,
                        "open_issues_count": 25,
                        "status": "Active",
                        "size": 30000,
                        "quality_detail": {
                            "code_quality_score": 85.0,
                            "documentation_score": 80.0,
                            "community_score": 90.0,
                            "maintenance_score": 95.0
                        }
                    },
                    "include_execution": False
                },
                timeout=15.0
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"✓ Health score calculated successfully")
                print(f"\nOverall Score: {result.get('overall_score', 0):.1f}/100")
                print(f"Grade: {result.get('overall_grade', 'N/A')}")
                print(f"Trend: {result.get('trend', 'unknown')}")
                
                dimensions = result.get('dimensions', {})
                if dimensions:
                    print(f"\nDimensional Scores:")
                    for dim, score in dimensions.items():
                        print(f"  {dim.replace('_', ' ').title()}: {score:.1f}/100")
                
                strengths = result.get('strengths', [])
                if strengths:
                    print(f"\nStrengths: {len(strengths)}")
                    for strength in strengths[:3]:
                        print(f"  + {strength}")
                
                recommendations = result.get('recommendations', [])
                if recommendations:
                    print(f"\nTop Recommendations:")
                    for rec in recommendations[:2]:
                        print(f"  [{rec.get('priority', 'N/A').upper()}] {rec.get('action', 'N/A')}")
                
                return result.get('overall_score', 0) > 0
            elif response.status_code == 503:
                print("⊘ Skipped - HackHub Analyzer not available")
                return None
            else:
                print(f"✗ Health scoring failed with status {response.status_code}")
                return False
                
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" HackHub Complete Platform v3.0 - Integration Test Suite")
    print("="*70)
    
    results = {}
    
    # Test 0: Server health (critical)
    health_ok, health_data = await test_server_health()
    if not health_ok:
        print("\n" + "="*70)
        print(" CRITICAL: Server is not running or unhealthy")
        print(" Please start the server first using: run_backend.bat")
        print("="*70)
        return
    
    # Test 1: Root endpoint
    results['root'] = await test_root_endpoint()
    
    # Test 2: ML search
    results['search'] = await test_ml_search()
    
    # Test 3: Code execution (optional)
    results['execution'] = await test_code_execution(health_data)
    
    # Test 4: README analysis
    results['readme'] = await test_readme_analysis()
    
    # Test 5: Performance profiling
    results['performance'] = await test_performance_profiling()
    
    # Test 6: Health scoring
    results['health'] = await test_health_scoring()
    
    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for test_name, result in results.items():
        if result is True:
            status = "✓ PASS"
        elif result is False:
            status = "✗ FAIL"
        else:
            status = "⊘ SKIP"
        
        print(f"{status} - {test_name.upper().replace('_', ' ')}")
    
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    
    if failed == 0 and passed > 0:
        print("\n🎉 All available tests passed successfully!")
        if skipped > 0:
            print(f"   ({skipped} tests skipped due to missing dependencies)")
    elif passed > failed:
        print(f"\n✓ Most tests passed ({passed}/{total - skipped})")
    else:
        print(f"\n⚠ Some tests failed")
    
    print("="*70)
    
    # Installation tips
    if skipped > 0:
        print("\nTo enable skipped features:")
        print("  1. Install Docker Desktop: https://www.docker.com/products/docker-desktop")
        print("  2. Install Python dependencies: pip install -r requirements.txt")
        print("  3. Restart the server")
        print("="*70)


if __name__ == "__main__":
    print("\nMake sure the server is running before testing!")
    print("Start with: run_backend.bat")
    print("\nStarting tests in 2 seconds...")
    
    import time
    time.sleep(2)
    
    asyncio.run(main())
