# RunAnywhere + HackHub Integration

## Overview

This integration brings **RunAnywhere** safe execution environment capabilities to **HackHub**, enabling automated repository testing, README validation, configuration analysis, and comprehensive health scoring.

## Architecture

```
┌──────────────────────────────────────────────────────┐
│         Flutter Frontend (Multi-Platform)            │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ Dashboard  │  │  Execution   │  │  Analysis   │ │
│  │   View     │  │    Panel     │  │    View     │ │
│  └────────────┘  └──────────────┘  └─────────────┘ │
└──────────────────┬───────────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────────┐
│          FastAPI Backend (Enhanced)                  │
│  ┌────────────────────────────────────────────────┐ │
│  │  Existing: Search, Quality, ML (Port 8000)    │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │  NEW: RunAnywhere Integration (Port 8001)     │ │
│  │  - Sandbox Manager                            │ │
│  │  - Execution Controller                       │ │
│  │  - Security Manager                           │ │
│  └────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────┐ │
│  │  NEW: HackHub Analyzer (Port 8001)            │ │
│  │  - README Validator                           │ │
│  │  - Config Analyzer                            │ │
│  │  - Performance Profiler                       │ │
│  │  - Health Scorer                              │ │
│  └────────────────────────────────────────────────┘ │
└──────────┬──────────────────────────┬────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────────┐   ┌─────────────────────────┐
│  Docker Sandboxes    │   │  Enhanced ML Pipeline   │
│  - Isolated Env      │   │  - README Analysis      │
│  - Resource Limits   │   │  - Config Validation    │
│  - Network Control   │   │  - Performance Scoring  │
└──────────────────────┘   └─────────────────────────┘
```

## Features

### RunAnywhere Execution Service

#### 1. **Sandbox Manager** (`backend/runanywhere/sandbox_manager.py`)
- Creates isolated Docker containers for safe execution
- Supports multiple languages: Python, Node.js, Java, Go, Rust, Flutter, etc.
- Resource limits (CPU, memory, disk, network)
- Automatic cleanup and timeout handling
- File upload/download to/from sandboxes

#### 2. **Execution Controller** (`backend/runanywhere/execution_controller.py`)
- Analyzes repository executability
- Extracts setup instructions automatically
- Executes repositories (clone → install → build → test)
- Executes code snippets
- Tracks execution history

#### 3. **Security Manager** (`backend/runanywhere/security_manager.py`)
- Code pattern validation
- Malicious code detection
- Resource limit enforcement
- Network policy management
- Rate limiting (placeholder for Redis integration)

### HackHub Analysis Enhancement

#### 1. **README Validator** (`backend/hackhub_analyzer/readme_validator.py`)
- Extracts code blocks and setup instructions
- Validates instruction accuracy (can test in sandbox)
- Detects broken links
- Analyzes README quality (sections, examples, badges)
- Provides improvement recommendations

#### 2. **Config Analyzer** (`backend/hackhub_analyzer/config_analyzer.py`)
- Analyzes CI/CD configurations
- Validates dependency management files
- Detects security issues (committed secrets, missing .gitignore)
- Checks for best practices (LICENSE, CONTRIBUTING, tests)

#### 3. **Performance Profiler** (`backend/hackhub_analyzer/performance_profiler.py`)
- Profiles build and install times
- Estimates complexity
- Detects performance bottlenecks
- Suggests optimizations (caching, dependency reduction)

#### 4. **Health Scorer** (`backend/hackhub_analyzer/health_scorer.py`)
- Calculates comprehensive health scores (0-100)
- Multi-dimensional scoring:
  - Code Quality (20%)
  - Documentation (15%)
  - Community (15%)
  - Maintenance (15%)
  - Configuration (10%)
  - Performance (15%)
  - Executability (10%)
- Identifies strengths and improvement areas
- Generates actionable recommendations
- Assesses contributor health

## API Endpoints

### Integration API (Port 8001)

Base URL: `http://localhost:8001`

#### Execution Endpoints

##### `POST /execute/code`
Execute code snippet in a sandbox.

**Request:**
```json
{
  "code": "print('Hello World')",
  "language": "python",
  "timeout": 30
}
```

**Response:**
```json
{
  "execution_id": "uuid",
  "status": "success",
  "stdout": "Hello World\n",
  "stderr": "",
  "exit_code": 0,
  "execution_time": 0.123
}
```

##### `POST /execute/repository`
Execute a repository (clone, install, build, test).

**Request:**
```json
{
  "repo_url": "https://github.com/user/repo",
  "repo_data": {
    "name": "repo",
    "language": "python",
    "tech_stack": ["python", "flask"]
  },
  "timeout": 300
}
```

**Response:**
```json
{
  "execution_id": "uuid",
  "status": "success",
  "logs": [
    {
      "step": "clone",
      "status": "success",
      "timestamp": "2026-02-21T..."
    },
    ...
  ],
  "total_execution_time": 45.6,
  "resource_stats": { ... }
}
```

##### `GET /execute/analyze?owner={owner}&repo={repo}`
Analyze if a repository can be executed.

**Response:**
```json
{
  "is_executable": true,
  "detected_runtime": "python",
  "setup_commands": ["pip install -r requirements.txt"],
  "run_command": "python main.py",
  "test_command": "pytest",
  "build_command": null,
  "estimated_complexity": "simple",
  "confidence": 0.85
}
```

##### `GET /execute/history?limit=10`
Get recent execution history.

##### `GET /execute/status/{execution_id}`
Get status of specific execution.

#### Analysis Endpoints

##### `POST /analyze/readme`
Analyze README quality and validate instructions.

**Request:**
```json
{
  "readme_content": "# My Project\n...",
  "repo_data": { ... }
}
```

**Response:**
```json
{
  "quality_analysis": {
    "overall_score": 85.0,
    "has_title": true,
    "has_installation": true,
    "code_block_count": 5,
    ...
  }
}
```

##### `POST /analyze/config`
Analyze project configurations.

**Request:**
```json
{
  "repo_data": { ... },
  "files": {
    "package.json": "{ ... }",
    ".github/workflows/test.yml": "..."
  }
}
```

**Response:**
```json
{
  "overall_score": 75.0,
  "ci_cd_score": 80.0,
  "dependency_score": 70.0,
  "security_score": 90.0,
  "issues": [ ... ],
  "recommendations": [ ... ]
}
```

##### `POST /analyze/performance`
Profile repository performance.

**Response:**
```json
{
  "overall_score": 85.0,
  "build_time_seconds": 45.0,
  "install_time_seconds": 30.0,
  "performance_grade": "A",
  "bottlenecks": [ ... ],
  "optimizations": [ ... ]
}
```

##### `POST /analyze/health`
Calculate comprehensive health score.

**Request:**
```json
{
  "repo_data": { ... },
  "readme_content": "...",
  "include_execution": true
}
```

**Response:**
```json
{
  "overall_score": 82.0,
  "overall_grade": "B+",
  "dimensions": {
    "code_quality": 85.0,
    "documentation": 80.0,
    "community": 75.0,
    "maintenance": 90.0,
    "configuration": 70.0,
    "performance": 85.0,
    "executability": 90.0
  },
  "trend": "growing",
  "risk_factors": [ ... ],
  "strengths": [ ... ],
  "improvement_areas": [ ... ],
  "recommendations": [ ... ]
}
```

#### Sandbox Management

##### `GET /sandbox/list`
List all active sandboxes.

##### `POST /sandbox/cleanup`
Clean up expired sandboxes.

##### `GET /sandbox/stats/{sandbox_id}`
Get resource usage statistics.

#### Health Check

##### `GET /health`
Service health check.

## Installation

### Prerequisites

1. **Docker** (required for sandbox execution)
   ```bash
   # Install Docker Desktop
   # Windows: https://docs.docker.com/desktop/install/windows-install/
   # Mac: https://docs.docker.com/desktop/install/mac-install/
   # Linux: https://docs.docker.com/engine/install/
   ```

2. **Python 3.9+**

3. **Existing HackHub dependencies**

### Setup

1. **Install Docker SDK**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Start Docker** (if not running)

3. **Run the integration API**
   ```bash
   python main_integration.py
   ```

   The API will start on `http://localhost:8001`

4. **Run the existing HackHub API** (in another terminal)
   ```bash
   python main_v2.py
   ```

   The main API will run on `http://localhost:8000`

## Usage Examples

### Execute Python Code

```bash
curl -X POST http://localhost:8001/execute/code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "for i in range(5): print(i)",
    "language": "python",
    "timeout": 30
  }'
```

### Analyze Repository Executability

```bash
curl "http://localhost:8001/execute/analyze?owner=torvalds&repo=linux"
```

### Get Comprehensive Health Score

```bash
curl -X POST http://localhost:8001/analyze/health \
  -H "Content-Type: application/json" \
  -d '{
    "repo_data": {
      "name": "example-repo",
      "stars": 1000,
      "language": "Python",
      "tech_stack": ["python", "flask"],
      "status": "Active"
    },
    "readme_content": "# Example\nA great project...",
    "include_execution": false
  }'
```

## Integration with Flutter Frontend

### Add Execution Service

Create `lib/services/execution_service.dart`:

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ExecutionService {
  final String baseUrl = 'http://localhost:8001';

  Future<Map<String, dynamic>> executeCode(
    String code, 
    String language
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/execute/code'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'code': code,
        'language': language,
        'timeout': 30
      })
    );

    return json.decode(response.body);
  }

  Future<Map<String, dynamic>> analyzeHealth(
    Map<String, dynamic> repoData,
    {String? readmeContent}
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl/analyze/health'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'repo_data': repoData,
        'readme_content': readmeContent,
        'include_execution': false
      })
    );

    return json.decode(response.body);
  }
}
```

### Add Health Score Card

In `dashboard_page.dart`, add health score display:

```dart
// In repository card widget
if (repo.healthScore != null) {
  Container(
    padding: EdgeInsets.all(8),
    decoration: BoxDecoration(
      color: _getHealthColor(repo.healthScore),
      borderRadius: BorderRadius.circular(4)
    ),
    child: Text(
      'Health: ${repo.healthScore.toStringAsFixed(0)}/100',
      style: TextStyle(color: Colors.white, fontSize: 12)
    )
  )
}
```

## Security Considerations

1. **Code Validation**: All code is scanned for dangerous patterns before execution
2. **Resource Limits**: CPU, memory, and network are strictly limited
3. **Isolation**: Each execution runs in a fresh Docker container
4. **Network Policies**: External network access can be disabled for code snippets
5. **Timeout Protection**: All executions have strict timeout limits
6. **Cleanup**: Sandboxes are automatically cleaned up after timeout

## Performance

- **Code Snippet Execution**: < 2 seconds (including container creation)
- **Repository Analysis** (no execution): < 1 second
- **Repository Execution** (clone → build → test): 30-300 seconds depending on project
- **Health Score Calculation**: < 500ms (without execution)

## Future Enhancements

1. **Real-time Execution Streaming**: WebSocket support for live logs
2. **Persistent Sandboxes**: Keep sandboxes alive for multiple executions
3. **Custom Docker Images**: Pre-built images with common dependencies
4. **Execution Caching**: Cache build results for faster re-runs
5. **Distributed Execution**: Scale across multiple Docker hosts
6. **Advanced Security**: Runtime malware detection with eBPF
7. **Cost Tracking**: Monitor resource usage and costs
8. **Execution Scheduling**: Queue management for batch processing

## Troubleshooting

### Docker Not Available

If you see "Docker not available" errors:

1. Ensure Docker Desktop is running
2. Check Docker daemon: `docker ps`
3. Verify Docker socket access

### Permission Issues

On Linux, add user to docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Port Conflicts

If port 8001 is in use, change in `main_integration.py`:
```python
uvicorn.run(app_extension, host="0.0.0.0", port=8002)
```

## Contributing

See the main `CONTRIBUTING.md` for contribution guidelines.

## License

Same license as the parent HackHub project.
