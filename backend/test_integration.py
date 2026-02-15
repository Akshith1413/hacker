"""
Test script for RunAnywhere + HackHub Integration

Demonstrates key features and validates the integration.
"""

import asyncio
import sys
sys.path.append('.')

from runanywhere.execution_controller import get_execution_controller
from runanywhere.sandbox_manager import get_sandbox_manager
from hackhub_analyzer.readme_validator import get_readme_validator
from hackhub_analyzer.config_analyzer import get_config_analyzer
from hackhub_analyzer.performance_profiler import get_performance_profiler
from hackhub_analyzer.health_scorer import get_health_scorer


async def test_code_execution():
    """Test 1: Execute simple Python code"""
    print("\n" + "="*60)
    print("TEST 1: Code Execution")
    print("="*60)
    
    execution_controller = get_execution_controller()
    
    code = """
import math
for i in range(5):
    print(f"Square root of {i}: {math.sqrt(i):.2f}")
"""
    
    print("Executing Python code...")
    result = await execution_controller.execute_code_snippet(
        code=code,
        language="python",
        timeout=30
    )
    
    print(f"Status: {result['status']}")
    print(f"Execution Time: {result.get('execution_time', 0):.3f}s")
    print(f"Output:\n{result['stdout']}")
    
    if result['stderr']:
        print(f"Errors:\n{result['stderr']}")
    
    return result['status'] == 'success'


async def test_executability_analysis():
    """Test 2: Analyze repository executability"""
    print("\n" + "="*60)
    print("TEST 2: Repository Executability Analysis")
    print("="*60)
    
    execution_controller = get_execution_controller()
    
    # Sample Flask repository data
    repo_data = {
        "name": "flask-example",
        "language": "Python",
        "tech_stack": ["python", "flask"],
        "stars": 150,
        "open_issues_count": 5
    }
    
    print("Analyzing Flask repository...")
    analysis = await execution_controller.analyze_repository_executability(repo_data)
    
    print(f"Is Executable: {analysis['is_executable']}")
    print(f"Detected Runtime: {analysis['detected_runtime']}")
    print(f"Setup Commands:")
    for cmd in analysis['setup_commands']:
        print(f"  - {cmd}")
    print(f"Run Command: {analysis['run_command']}")
    print(f"Test Command: {analysis['test_command']}")
    print(f"Confidence: {analysis['confidence']:.0%}")
    
    return analysis['is_executable']


def test_readme_analysis():
    """Test 3: Analyze README quality"""
    print("\n" + "="*60)
    print("TEST 3: README Quality Analysis")
    print("="*60)
    
    readme_validator = get_readme_validator()
    
    readme_content = """
# My Awesome Project

A great project that does amazing things!

## Installation

```bash
npm install my-awesome-project
```

## Usage

```javascript
const myProject = require('my-awesome-project');
myProject.doSomething();
```

## License

MIT
"""
    
    print("Analyzing README content...")
    analysis = readme_validator.analyze_readme_quality(readme_content)
    
    print(f"Quality Score: {analysis['quality_score']:.0f}/100")
    print(f"Word Count: {analysis['word_count']}")
    print(f"Code Blocks: {analysis['code_block_count']}")
    print(f"Has Installation: {analysis['has_installation']}")
    print(f"Has Usage: {analysis['has_usage']}")
    print(f"Has License: {analysis['has_license']}")
    
    return analysis['quality_score'] > 50


def test_config_analysis():
    """Test 4: Analyze project configuration"""
    print("\n" + "="*60)
    print("TEST 4: Configuration Analysis")
    print("="*60)
    
    config_analyzer = get_config_analyzer()
    
    repo_data = {
        "name": "example-project",
        "language": "JavaScript"
    }
    
    files = {
        "package.json": '{"name": "example", "version": "1.0.0", "dependencies": {"express": "^4.18.0"}}',
        ".github/workflows/test.yml": "name: Test\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest",
        "README.md": "# Example",
        "LICENSE": "MIT License",
        ".gitignore": "node_modules\n.env\n*.log"
    }
    
    print("Analyzing project configuration...")
    analysis = config_analyzer.analyze_configurations(repo_data, files)
    
    print(f"Overall Score: {analysis['overall_score']:.0f}/100")
    print(f"CI/CD Score: {analysis['ci_cd_score']:.0f}/100")
    print(f"Dependency Score: {analysis['dependency_score']:.0f}/100")
    print(f"Security Score: {analysis['security_score']:.0f}/100")
    print(f"Best Practices Score: {analysis['best_practices_score']:.0f}/100")
    
    if analysis['issues']:
        print(f"Issues Found: {len(analysis['issues'])}")
    
    if analysis['recommendations']:
        print(f"Recommendations:")
        for rec in analysis['recommendations'][:3]:
            print(f"  - {rec}")
    
    return analysis['overall_score'] > 50


def test_performance_profiling():
    """Test 5: Performance profiling"""
    print("\n" + "="*60)
    print("TEST 5: Performance Profiling")
    print("="*60)
    
    performance_profiler = get_performance_profiler()
    
    repo_data = {
        "name": "medium-project",
        "language": "Python",
        "tech_stack": ["python", "django"],
        "stars": 500,
        "size": 50000  # KB
    }
    
    print("Profiling repository performance...")
    profile = performance_profiler.profile_repository(repo_data)
    
    print(f"Overall Score: {profile['overall_score']:.0f}/100")
    print(f"Performance Grade: {profile['performance_grade']}")
    print(f"Estimated Install Time: {profile['install_time_seconds']:.1f}s")
    print(f"Estimated Build Time: {profile['build_time_seconds']:.1f}s")
    print(f"Estimated Test Time: {profile['test_time_seconds']:.1f}s")
    print(f"Repository Size: {profile['repository_size_mb']:.1f} MB")
    print(f"Code Complexity: {profile['code_complexity']}")
    
    if profile['bottlenecks']:
        print(f"Bottlenecks Found: {len(profile['bottlenecks'])}")
        for bottleneck in profile['bottlenecks']:
            print(f"  - {bottleneck['message']}")
    
    if profile['optimizations']:
        print(f"Suggested Optimizations:")
        for opt in profile['optimizations'][:3]:
            print(f"  - {opt}")
    
    return profile['overall_score'] > 0


def test_health_scoring():
    """Test 6: Comprehensive health scoring"""
    print("\n" + "="*60)
    print("TEST 6: Comprehensive Health Scoring")
    print("="*60)
    
    health_scorer = get_health_scorer()
    
    repo_data = {
        "name": "great-project",
        "language": "Python",
        "tech_stack": ["python", "fastapi"],
        "stars": 2000,
        "forks": 300,
        "open_issues_count": 25,
        "status": "Active",
        "size": 30000
    }
    
    quality_detail = {
        "code_quality_score": 85.0,
        "documentation_score": 80.0,
        "community_score": 90.0,
        "maintenance_score": 95.0
    }
    
    print("Calculating comprehensive health score...")
    health_score = health_scorer.calculate_health_score(
        repo_data=repo_data,
        quality_detail=quality_detail
    )
    
    print(f"\nOverall Health Score: {health_score['overall_score']:.1f}/100")
    print(f"Grade: {health_score['overall_grade']}")
    print(f"Trend: {health_score['trend']}")
    
    print(f"\nDimensional Scores:")
    for dimension, score in health_score['dimensions'].items():
        print(f"  {dimension.replace('_', ' ').title()}: {score:.1f}/100")
    
    if health_score['strengths']:
        print(f"\nStrengths:")
        for strength in health_score['strengths']:
            print(f"  + {strength}")
    
    if health_score['improvement_areas']:
        print(f"\nImprovement Areas:")
        for area in health_score['improvement_areas']:
            print(f"  - {area}")
    
    if health_score['recommendations']:
        print(f"\nTop Recommendations:")
        for rec in health_score['recommendations'][:3]:
            print(f"  {rec['priority'].upper()}: {rec['action']}")
            print(f"    {rec['details']}")
    
    if health_score['risk_factors']:
        print(f"\nRisk Factors: {len(health_score['risk_factors'])}")
    
    return health_score['overall_score'] > 0


async def test_sandbox_availability():
    """Test 0: Check Docker/Sandbox availability"""
    print("\n" + "="*60)
    print("TEST 0: Sandbox Availability Check")
    print("="*60)
    
    sandbox_manager = get_sandbox_manager()
    
    if sandbox_manager.is_available():
        print("✓ Docker is available")
        print("✓ Sandboxes can be created")
        return True
    else:
        print("✗ Docker is not available")
        print("✗ Sandbox features will be limited")
        print("\nNote: Install Docker Desktop to enable full functionality:")
        print("  https://www.docker.com/products/docker-desktop")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(" RunAnywhere + HackHub Integration - Test Suite")
    print("="*60)
    
    results = {}
    
    # Test 0: Docker availability (non-blocking)
    results['docker'] = await test_sandbox_availability()
    
    # Test 1: Code execution (requires Docker)
    if results['docker']:
        try:
            results['execution'] = await test_code_execution()
        except Exception as e:
            print(f"✗ Code execution test failed: {e}")
            results['execution'] = False
    else:
        print("\nSkipping code execution test (Docker not available)")
        results['execution'] = None
    
    # Test 2: Executability analysis (doesn't require Docker)
    try:
        results['analysis'] = await test_executability_analysis()
    except Exception as e:
        print(f"✗ Executability analysis test failed: {e}")
        results['analysis'] = False
    
    # Test 3: README analysis
    try:
        results['readme'] = test_readme_analysis()
    except Exception as e:
        print(f"✗ README analysis test failed: {e}")
        results['readme'] = False
    
    # Test 4: Config analysis
    try:
        results['config'] = test_config_analysis()
    except Exception as e:
        print(f"✗ Config analysis test failed: {e}")
        results['config'] = False
    
    # Test 5: Performance profiling
    try:
        results['performance'] = test_performance_profiling()
    except Exception as e:
        print(f"✗ Performance profiling test failed: {e}")
        results['performance'] = False
    
    # Test 6: Health scoring
    try:
        results['health'] = test_health_scoring()
    except Exception as e:
        print(f"✗ Health scoring test failed: {e}")
        results['health'] = False
    
    # Summary
    print("\n" + "="*60)
    print(" TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result is True else ("✗ FAIL" if result is False else "⊘ SKIP")
        print(f"{status} - {test_name.upper()}")
    
    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}")
    
    if failed == 0:
        print("\n🎉 All tests passed successfully!")
    elif passed > failed:
        print(f"\n⚠ {passed}/{total} tests passed")
    else:
        print(f"\n❌ Multiple tests failed")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
