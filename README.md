<p align="center">
  <img src="https://img.icons8.com/fluency/96/github.png" alt="HackHub Logo" width="96" height="96"/>
</p>

<h1 align="center">🚀 HackHub</h1>

<p align="center">
  <b>Intelligent Open-Source Discovery & Collaboration Platform</b>
</p>

<p align="center">
  <i>Discover high-quality GitHub repositories · Evaluate project health · Find your next collaboration</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white" alt="Flutter"/>
  <img src="https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white" alt="Dart"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black" alt="Firebase"/>
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="scikit-learn"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blue?style=flat-square" alt="Version"/>
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License"/>
  <img src="https://img.shields.io/badge/platform-Web%20%7C%20Android%20%7C%20iOS-lightgrey?style=flat-square" alt="Platform"/>
  <img src="https://img.shields.io/badge/status-Active%20Development-orange?style=flat-square" alt="Status"/>
</p>

---

## 📌 Table of Contents

- [Problem Statement](#-problem-statement)
- [Proposed Solution](#-proposed-solution)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [API Endpoints](#-api-endpoints)
- [ML Service Modules](#-ml-service-modules)
- [Screenshots](#-screenshots)
- [Project Progress](#-project-progress)
- [Future Roadmap](#-future-roadmap)
- [Contributing](#-contributing)
- [Team](#-team)
- [License](#-license)

---

## ❗ Problem Statement

Despite the vast number of open-source repositories available on GitHub, identifying **high-quality, actively maintained, and collaboration-ready** projects remains a significant challenge. Developers often struggle to:

| Challenge | Description |
|-----------|-------------|
| 🔍 **Tech Stack Discovery** | Finding repositories with a precise and clearly defined tech stack |
| 📊 **Project Health** | Evaluating activity, issue resolution rate, commit frequency, and maintenance status |
| 🤝 **Collaboration Gaps** | Identifying repositories that genuinely require contributors or enhancements |
| 📄 **Documentation Quality** | Assessing the clarity and completeness of project README files |
| 🎯 **Skill Alignment** | Discovering projects aligned with developer skill level and interests |

> Existing GitHub search mechanisms primarily rely on keyword-based filtering and basic metadata, which **do not provide deeper insights** into repository quality, maintainability, collaboration potential, or documentation standards.

**The Result:** Contributors waste time exploring irrelevant or inactive repositories, and promising projects miss out on potential collaborators due to poor discoverability and documentation.

---

## 💡 Proposed Solution

**HackHub** is a web-based platform designed to **intelligently filter and recommend** GitHub repositories using:

```
┌──────────────────────────────────────────────────────────────────┐
│                        🚀 HackHub Platform                       │
├──────────────┬──────────────┬─────────────────┬─────────────────┤
│  🔧 Advanced  │  📈 Health    │  🤖 ML-Based    │  📝 README      │
│  Tech Stack   │  Metrics     │  Classification │  Quality        │
│  Filtering    │  Analysis    │  & Scoring      │  Analysis       │
└──────────────┴──────────────┴─────────────────┴─────────────────┘
```

- **Advanced Filtering** — Filter by tech stack, project domain, and contribution needs
- **Repository Health Metrics** — Analyze activity, stars, forks, issues, and maintenance
- **ML-Powered Classification** — Identify repos needing optimization or enhancement
- **Collaboration Indicators** — Connect developers with suitable projects
- **README Quality Evaluation** — Automated scoring and improvement suggestions

---

## ✨ Key Features

<table>
  <tr>
    <td align="center" width="33%">
      <h3>🔍 Smart Search</h3>
      <p>Intelligent GitHub repository search with ML-enhanced query construction and multi-parameter filtering</p>
    </td>
    <td align="center" width="33%">
      <h3>🤖 ML Classification</h3>
      <p>Automatic project status detection (Active, Inactive, New, Finished) using heuristic and ML models</p>
    </td>
    <td align="center" width="33%">
      <h3>🏷️ Tech Stack Detection</h3>
      <p>Keyword scoring system to identify MERN, MEAN, Flutter, ML, DevOps, Web3, and 12+ tech stacks</p>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <h3>📊 Quality Scoring</h3>
      <p>Multi-dimensional quality analysis: documentation, code quality, community, and maintenance scores</p>
    </td>
    <td align="center" width="33%">
      <h3>🔥 Trending Repos</h3>
      <p>Discover trending repositories by category with real-time GitHub data</p>
    </td>
    <td align="center" width="33%">
      <h3>🤝 Collaboration</h3>
      <p>One-click collaboration request generation to connect with project maintainers</p>
    </td>
  </tr>
  <tr>
    <td align="center" width="33%">
      <h3>🔐 Secure Auth</h3>
      <p>Firebase Authentication with Google Sign-In and email/password support</p>
    </td>
    <td align="center" width="33%">
      <h3>⚙️ User Settings</h3>
      <p>Personalized user profiles with Firestore-backed preferences and avatar upload</p>
    </td>
    <td align="center" width="33%">
      <h3>📱 Cross-Platform</h3>
      <p>Built with Flutter — runs on Web, Android, iOS, Windows, macOS, and Linux</p>
    </td>
  </tr>
</table>

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT (Flutter)                           │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Cover    │  │  Dashboard   │  │ Login /  │  │   Settings    │  │
│  │ Page     │  │  (Search +   │  │ Register │  │   (Profile)   │  │
│  │          │  │  Results)    │  │          │  │               │  │
│  └──────────┘  └──────┬───────┘  └────┬─────┘  └───────────────┘  │
│                       │               │                            │
│               ┌───────┴───────┐  ┌────┴──────────┐                │
│               │ GithubService │  │ Firebase Auth  │                │
│               │  (HTTP Client)│  │ + Firestore    │                │
│               └───────┬───────┘  └────────────────┘                │
└───────────────────────┼────────────────────────────────────────────┘
                        │ HTTP (REST API)
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI + Python)                      │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      main.py / main_v2.py                   │   │
│  │              (REST Endpoints + GitHub API Proxy)            │   │
│  └─────────────────────────┬───────────────────────────────────┘   │
│                             │                                      │
│  ┌──────────────────────────┴──────────────────────────────────┐   │
│  │                    ML Service Package                        │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │   │
│  │  │ Classifiers  │  │ Embeddings   │  │ Feature Extractor│  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │   │
│  │  │Quality Scorer│  │ Recommender  │  │ GitHub Analyzer  │  │   │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │    GitHub REST API    │
            │   (Repository Data)   │
            └───────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|:----------:|---------|
| ![Flutter](https://img.shields.io/badge/Flutter-02569B?style=flat-square&logo=flutter&logoColor=white) | Cross-platform UI framework |
| ![Dart](https://img.shields.io/badge/Dart-0175C2?style=flat-square&logo=dart&logoColor=white) | Programming language |
| ![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=flat-square&logo=firebase&logoColor=black) | Auth, Firestore, Storage |
| ![Google Fonts](https://img.shields.io/badge/Google%20Fonts-4285F4?style=flat-square&logo=google&logoColor=white) | Typography |

### Backend
| Technology | Purpose |
|:----------:|---------|
| ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) | Backend language |
| ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) | REST API framework |
| ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white) | ML classification |
| ![NLTK](https://img.shields.io/badge/NLTK-154F5B?style=flat-square&logoColor=white) | NLP processing |
| ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) | Data processing |
| ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) | Containerization |

### Services & APIs
| Service | Purpose |
|:-------:|---------|
| ![GitHub](https://img.shields.io/badge/GitHub%20API-181717?style=flat-square&logo=github&logoColor=white) | Repository data source |
| ![Firebase Auth](https://img.shields.io/badge/Firebase%20Auth-FFCA28?style=flat-square&logo=firebase&logoColor=black) | User authentication |
| ![Cloud Firestore](https://img.shields.io/badge/Cloud%20Firestore-FFCA28?style=flat-square&logo=firebase&logoColor=black) | User data storage |

---

## 📁 Project Structure

```
hacker/
├── 📂 backend/                   # Python FastAPI Backend
│   ├── main.py                   # Primary API server
│   ├── main_v2.py                # Enhanced API (v2) with advanced features
│   ├── ml_service.py             # Legacy ML service
│   ├── ml_service/               # 🤖 ML Service Package
│   │   ├── __init__.py           # MLService class (backward compat)
│   │   ├── classifiers.py        # ML classifiers for repo status
│   │   ├── embeddings.py         # Text embedding service
│   │   ├── features.py           # Feature extraction utilities
│   │   ├── github_analyzer.py    # GitHub-specific analysis logic
│   │   ├── quality_scorer.py     # Multi-dimensional quality scoring
│   │   └── recommender.py        # Repository recommendation engine
│   ├── requirements.txt          # Python dependencies
│   ├── Dockerfile                # Docker containerization
│   └── cache/                    # Cached ML model data
│
├── 📂 lib/                       # Flutter Frontend (Dart)
│   ├── main.dart                 # App entry point + routing
│   ├── cover_page.dart           # Landing / cover page
│   ├── login_page.dart           # Auth (Login + Register)
│   ├── dashboard_page.dart       # Main search & results dashboard
│   ├── settings_page.dart        # User profile & settings
│   ├── firebase_options.dart     # Firebase configuration
│   ├── models/
│   │   └── github_repo.dart      # GithubRepo, QualityDetail, TechStackConfidence
│   └── services/
│       └── github_service.dart   # Backend API communication layer
│
├── 📂 assets/                    # App assets & env config
├── 📂 android/                   # Android platform files
├── 📂 ios/                       # iOS platform files
├── 📂 web/                       # Web platform files
├── 📂 windows/                   # Windows platform files
├── 📂 linux/                     # Linux platform files
├── 📂 macos/                     # macOS platform files
├── cors.json                     # CORS configuration
├── firestore.rules               # Firestore security rules
├── pubspec.yaml                  # Flutter dependencies
├── run_backend.bat               # Backend launch script (Windows)
└── README.md                     # 📖 You are here!
```

---

## 🚀 Getting Started

### Prerequisites

| Tool | Version | Download |
|------|---------|----------|
| Flutter SDK | ≥ 3.11.0 | [flutter.dev](https://flutter.dev/docs/get-started/install) |
| Python | ≥ 3.9 | [python.org](https://www.python.org/downloads/) |
| Firebase CLI | Latest | [firebase.google.com](https://firebase.google.com/docs/cli) |
| Git | Latest | [git-scm.com](https://git-scm.com/) |

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Akshith1413/hacker.git
cd hacker
```

### 2️⃣ Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> **💡 Quick Start (Windows):** Run `run_backend.bat` from the project root to auto-start the backend.

### 3️⃣ Frontend Setup

```bash
# From the project root
flutter pub get

# Run on Chrome (Web)
flutter run -d chrome

# Run on connected Android device
flutter run -d android

# Run on Windows desktop
flutter run -d windows
```

### 4️⃣ Docker Setup (Optional)

```bash
cd backend
docker build -t hackhub-backend .
docker run -p 8000:8000 hackhub-backend
```

### 5️⃣ Firebase Configuration

1. Create a Firebase project at [console.firebase.google.com](https://console.firebase.google.com/)
2. Enable **Authentication** (Email/Password + Google Sign-In)
3. Enable **Cloud Firestore**
4. Enable **Firebase Storage**
5. Update `lib/firebase_options.dart` with your project credentials
6. Deploy Firestore rules:
   ```bash
   firebase deploy --only firestore:rules
   ```

---

## 📡 API Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| `GET` | `/` | Health check | — |
| `GET` | `/search` | Search & filter repositories | `q`, `min_stars`, `status`, `tech_stack` |
| `GET` | `/trending` | Get trending repositories | `category`, `limit` |

### Example Request

```bash
# Search for MERN stack repos with 100+ stars
curl "http://localhost:8000/search?q=web+app&tech_stack=mern&min_stars=100"

# Filter by project status
curl "http://localhost:8000/search?q=machine+learning&status=active"

# Get trending repos
curl "http://localhost:8000/trending?category=python&limit=20"
```

### Response Schema

```json
{
  "name": "awesome-project",
  "full_name": "user/awesome-project",
  "description": "A cool project",
  "html_url": "https://github.com/user/awesome-project",
  "stars": 1500,
  "language": "Python",
  "topics": ["machine-learning", "ai"],
  "status": "Active",
  "tech_stack": ["Machine Learning", "Data Science"],
  "open_issues_count": 12,
  "updated_at": "2026-02-20T10:00:00Z"
}
```

---

## 🤖 ML Service Modules

| Module | File | Description |
|--------|------|-------------|
| **Feature Extractor** | `features.py` | Extracts repository features for ML classification |
| **ML Classifiers** | `classifiers.py` | Classifies repo status (Active, Inactive, New, Finished) |
| **Embedding Service** | `embeddings.py` | Generates text embeddings for semantic analysis |
| **Quality Scorer** | `quality_scorer.py` | Multi-dimensional scoring: documentation, code quality, community, maintenance |
| **Recommendation Engine** | `recommender.py` | Personalized repository recommendations |
| **GitHub Analyzer** | `github_analyzer.py` | Deep GitHub repository analysis and metrics |

### Supported Tech Stack Detection

```
🟢 MERN Stack      🟢 MEAN Stack       🟢 MEVN Stack
🟢 Flutter          🟢 React Native     🟢 React
🟢 Machine Learning 🟢 Data Science     🟢 DevOps
🟢 Web3/Blockchain  🟢 Modern Frontend  🟢 Backend Strong
🟢 Game Dev         🟢 Mobile Dev       🟢 + Language-based
```

### Quality Scoring Dimensions

```
📄 Documentation Score  ─── README completeness, guides, examples
💻 Code Quality Score   ─── Structure, patterns, best practices
👥 Community Score      ─── Stars, forks, contributors, issues
🔧 Maintenance Score    ─── Commit frequency, issue response, activity
━━━━━━━━━━━━━━━━━━━━━━
📊 Total Quality Score  ─── Weighted aggregate (Grade: A+ to F)
```

---

## 📸 Screenshots

> *Screenshots will be added here as the UI is finalized.*

<!-- 
<p align="center">
  <img src="screenshots/cover_page.png" width="45%" alt="Cover Page"/>
  <img src="screenshots/dashboard.png" width="45%" alt="Dashboard"/>
</p>
<p align="center">
  <img src="screenshots/login.png" width="45%" alt="Login"/>
  <img src="screenshots/settings.png" width="45%" alt="Settings"/>
</p>
-->

---

## 📈 Project Progress

- [x] **Problem Analysis & Requirement Identification**
  - Identified core challenges in open-source discovery
  - Defined system objectives and feature requirements

- [x] **System Design & Architecture Planning**
  - Designed frontend (Flutter), backend (FastAPI), and ML modules
  - Planned tech stack filtering, health analysis, and quality scoring

- [x] **Backend Development (Core)**
  - Implemented FastAPI server with GitHub API integration
  - Developed ML-based classification and tech stack detection
  - Built quality scoring, embeddings, and recommendation modules

- [x] **Filtering System**
  - Multi-parameter filtering (tech stack, status, stars, forks, etc.)
  - Optimized repository ranking logic

- [x] **Authentication & User Management**
  - Firebase Auth with Google Sign-In and Email/Password
  - Firestore-backed user profiles and settings

- [🔄] **UI Integration**
  - Cover page, Dashboard, Login, and Settings pages built
  - Search and results flow connected to backend
  - Polishing and UX improvements in progress

- [🔄] **README Quality Module**
  - Framework designed for structure analysis
  - ML/NLP enhancement planned for documentation scoring

---

## 🗺️ Future Roadmap

| Phase | Feature | Status |
|:-----:|---------|:------:|
| 🔜 | Enhanced README quality analysis with NLP scoring | Planned |
| 🔜 | Skill-based contributor matching system | Planned |
| 🔜 | Repository comparison dashboard | Planned |
| 🔜 | Bookmarks & saved searches | Planned |
| 🔜 | Community-driven repo reviews and ratings | Planned |
| 🔜 | GitHub OAuth for personalized recommendations | Planned |
| 🔜 | Dark/Light theme toggle | Planned |
| 🔜 | Progressive Web App (PWA) support | Planned |

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

> Please make sure to update tests as appropriate and follow the existing code style.

---

## 👥 Team

| Name | Role |
|------|------|
| **Akshith** | Full-Stack Developer & Project Lead |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>⭐ If you found HackHub useful, please give it a star! ⭐</b>
</p>

<p align="center">
  Made with ❤️ using Flutter & FastAPI
</p>
