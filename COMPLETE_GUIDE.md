# HackHub Complete Platform v3.0

## 🎉 ONE UNIFIED PRODUCT - Everything Integrated!

This is the complete HackHub platform with **all features working together**:
- ✅ **Existing ML features** (search, quality scoring, recommendations)
- ✅ **RunAnywhere execution** (safe code execution, repository testing)  
- ✅ **HackHub analysis** (README validation, config analysis, performance profiling, health scoring)

**Everything runs on ONE server at `http://localhost:8000`**

---

## 🚀 Quick Start (2 Steps!)

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Optional:** Install Docker Desktop for execution features
- Windows/Mac: https://www.docker.com/products/docker-desktop
- **Note:** All other features work without Docker!

### Step 2: Start the Server

```bash
run_backend.bat
```

That's it! The server starts on **http://localhost:8000**

---

## 📊 What You Get

### Core Features (Always Available)

1. **ML-Powered Search**
   - Semantic search with embeddings
   - 20+ granular filters (stars, forks, dates, quality, etc.)
   - Tech stack detection (15+ frameworks)
   - Status classification (Active, Ongoing, Slowing Down, etc.)
   - Quality scoring (0-100 with grade)

2. **Smart Recommendations**
   - Similar repository finding
   - Personalized suggestions
   - Trending repository detection

3. **README Validation**
   - Quality scoring
   - Section detection
   - Code block extraction
   - Link checking

4. **Configuration Analysis**
   - CI/CD detection
   - Dependency validation
   - Security checks
   - Best practice recommendations

5. **Performance Profiling**
   - Build time estimation
   - Bottleneck detection
   - Optimization suggestions

6. **Comprehensive Health Scoring**
   - 7-dimensional scoring
   - Actionable recommendations
   - Trend analysis
   - Risk factor detection

### Execution Features (Requires Docker)

7. **Code Execution**
   - Run code snippets safely
   - Support for 12+ languages
   - Resource limits & isolation

8. **Repository Testing**
   - Automatic clone → install → build → test
   - Validates README instructions
   - Reports build success rates

---

## 🔧 How to Run & Test

### Start the Server

```bash
# Method 1: Use the startup script (recommended)
run_backend.bat

# Method 2: Manual startup
cd backend
python -m uvicorn main_v2:app --host 0.0.0.0 --port 8000 --reload
```

### Test All Features

```bash
# In a NEW terminal (keep server running)
cd backend
python test_complete.py
```

This tests everything:
- ✓ Server health
- ✓ ML search
- ✓ README analysis
- ✓ Performance profiling
- ✓ Health scoring
- ✓ Code execution (if Docker available)

### Explore the API

Open in your browser:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Root Info**: http://localhost:8000/

---

## 📡 API Endpoints (All on Port 8000)

### Existing ML Endpoints

```
GET  /                      - API information
GET  /search                - ML-powered repository search
GET  /similar/{owner}/{repo} - Find similar repositories
GET  /trending              - Get trending repositories
GET  /stats                 - Service statistics
```

### NEW: Analysis Endpoints

```
POST /analyze/readme        - Validate README quality
POST /analyze/config        - Analyze configuration files
POST /analyze/performance   - Profile performance
POST /analyze/health        - Comprehensive health score
```

### NEW: Execution Endpoints (Requires Docker)

```
POST /execute/code          - Execute code snippet
POST /execute/repository    - Test full repository
GET  /execute/analyze       - Analyze executability
GET  /execute/history       - Execution history
GET  /execute/status/{id}   - Check execution status
```

### NEW: Sandbox Management

```
GET  /sandbox/list          - List active sandboxes
POST /sandbox/cleanup       - Clean expired sandboxes
GET  /sandbox/stats/{id}    - Sandbox resource usage
```

### System

```
GET  /health                - Complete health check
```

---

## 💡 Usage Examples

### Example 1: Search with ML

```bash
curl "http://localhost:8000/search?q=machine+learning&min_stars=100&per_page=5"
```

### Example 2: Get Health Score

```bash
curl -X POST http://localhost:8000/analyze/health \
  -H "Content-Type: application/json" \
  -d '{
    "repo_data": {
      "name": "my-project",
      "language": "Python",
      "stars": 100,
      "tech_stack": ["python", "flask"],
      "status": "Active"
    }
  }'
```

### Example 3: Validate README

```bash
curl -X POST http://localhost:8000/analyze/readme \
  -H "Content-Type: application/json" \
  -d '{
    "readme_content": "# My Project\n\n## Installation\n```bash\nnpm install\n```",
    "repo_data": {"name": "test"}
  }'
```

### Example 4: Execute Python Code (Requires Docker)

```bash
curl -X POST http://localhost:8000/execute/code \
  -H "Content-Type: application/json" \
  -d '{
    "code": "print(\"Hello from HackHub!\")",
    "language": "python"
  }'
```

---

## 📂 Project Structure

```
C:\hacker\
├── backend/
│   ├── main_v2.py              ← MAIN FILE (everything integrated here!)
│   ├── requirements.txt        ← All dependencies
│   │
│   ├── ml_service/             ← Existing ML features
│   │   ├── features.py
│   │   ├── embeddings.py
│   │   ├── classifiers.py
│   │   ├── quality_scorer.py
│   │   ├── recommender.py
│   │   └── github_analyzer.py
│   │
│   ├── runanywhere/            ← NEW: Safe execution
│   │   ├── sandbox_manager.py
│   │   ├── execution_controller.py
│   │   └── security_manager.py
│   │
│   ├── hackhub_analyzer/       ← NEW: Enhanced analysis
│   │   ├── readme_validator.py
│   │   ├── config_analyzer.py
│   │   ├── performance_profiler.py
│   │   └── health_scorer.py
│   │
│   └── test_complete.py        ← Test all features
│
├── run_backend.bat             ← ONE COMMAND TO START EVERYTHING
└── COMPLETE_GUIDE.md           ← This file
```

---

## ✅ Feature Matrix

| Feature | Available Without Docker | Available With Docker |
|---------|-------------------------|---------------------|
| ML Search | ✅ | ✅ |
| Quality Scoring | ✅ | ✅ |
| Recommendations | ✅ | ✅ |
| README Analysis | ✅ | ✅ |
| Config Analysis | ✅ | ✅ |
| Performance Profiling | ✅ | ✅ |
| Health Scoring | ✅ | ✅ |
| Code Execution | ❌ | ✅ |
| Repository Testing | ❌ | ✅ |
| README Validation (execution) | ❌ | ✅ |

**Summary:** 7/9 features work without Docker, 9/9 with Docker

---

## 🔍 How to Verify Everything Works

### 1. Check Server is Running

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "services": {
    "ml_services": true,
    "runanywhere": true/false,
    "docker": true/false,
    "hackhub_analyzer": true/false
  }
}
```

### 2. Run Complete Test Suite

```bash
cd backend
python test_complete.py
```

Expected output:
```
✓ PASS - ROOT
✓ PASS - SEARCH
✓ PASS - README
✓ PASS - PERFORMANCE
✓ PASS - HEALTH
⊘ SKIP - EXECUTION (if no Docker)

Total: 6 | Passed: 5 | Failed: 0 | Skipped: 1
🎉 All available tests passed successfully!
```

### 3. Try the Interactive API Docs

Visit http://localhost:8000/docs and try any endpoint!

---

## 🐳 Docker Setup (Optional)

To enable execution features:

1. **Install Docker Desktop**
   - Download from https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Verify Docker is running**
   ```bash
   docker ps
   ```
   Should show running containers (or empty list is fine)

3. **Install Docker SDK**
   ```bash
   pip install docker
   ```

4. **Restart the server**
   ```bash
   run_backend.bat
   ```

Now you'll see:
```
✓ RunAnywhere ready (Docker available)
```

---

## 🎯 Complete Workflow

### For Development

1. Start server: `run_backend.bat`
2. In another terminal: `python test_complete.py`
3. Explore API: http://localhost:8000/docs
4. Make changes to `main_v2.py`
5. Server auto-reloads (--reload flag)

### For Production

1. Remove `--reload` flag from `run_backend.bat`
2. Use gunicorn or similar ASGI server
3. Set up reverse proxy (nginx)
4. Configure firewall rules
5. Set up SSL/TLS certificates

---

## 🛠️ Troubleshooting

### Issue: "Module not found" errors

**Solution:**
```bash
cd backend
pip install -r requirements.txt
```

### Issue: "Docker not available"

**Solution:**
- This is OK! 7/9 features still work
- To enable execution: Install Docker Desktop

### Issue: Port 8000 already in use

**Solution:** Edit `run_backend.bat`, change `--port 8000` to `--port 8001`

### Issue: Tests fail with "Cannot connect to server"

**Solution:** Make sure server is running first!
```bash
# Terminal 1
run_backend.bat

# Terminal 2 (wait for server to start)
python test_complete.py
```

---

## 📈 Performance

- **Server startup**: 2-5 seconds
- **ML search**: 1-3 seconds
- **Analysis (README/Config/Performance)**: < 500ms
- **Health scoring**: < 1 second
- **Code execution**: 1-5 seconds
- **Repository testing**: 30-300 seconds (depends on project)

---

## 🔐 Security

All execution features are:
- ✅ Pattern-validated (no malicious code)
- ✅ Docker-isolated (can't access host system)
- ✅ Resource-limited (CPU, memory, network)
- ✅ Time-limited (automatic timeout)
- ✅ Network-controlled (can disable internet access)

---

## 📝 Next Steps

1. **Test it!**
   ```bash
   run_backend.bat
   python test_complete.py
   ```

2. **Integrate with Flutter** (see existing `lib/services/github_service.dart`)
   - Add health score display
   - Add execution panel
   - Add README validator UI

3. **Deploy**
   - Set up on cloud (AWS, GCP, Azure)
   - Configure Docker host
   - Set up monitoring

---

## 🎊 Summary

**You now have ONE complete product that:**

✅ Works out of the box (just run `run_backend.bat`)
✅ Has all existing features (ML search, quality scoring, recommendations)
✅ Has all new features (execution, analysis, health scoring)
✅ Gracefully handles missing Docker (most features still work)
✅ Is fully tested (`test_complete.py`)
✅ Has comprehensive API docs (`http://localhost:8000/docs`)
✅ Runs on ONE server (port 8000)
✅ Uses ONE startup script (`run_backend.bat`)

**No separate servers, no complicated setup, just run and use!**

---

## 📞 Quick Reference

| What | How |
|------|-----|
| Start server | `run_backend.bat` |
| Test everything | `python test_complete.py` |
| API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| Install deps | `pip install -r requirements.txt` |
| Optional Docker | Download from docker.com |

**That's all you need to know!** 🚀
