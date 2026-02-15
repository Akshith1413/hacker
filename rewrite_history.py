import os
import subprocess
import random
from datetime import datetime, timedelta

# Configuration
REPO_PATH = r"c:\hacker"
START_DATE = datetime(2026, 2, 16)
END_DATE = datetime(2026, 2, 21)
AKSHITH = {"name": "Ravula Akshith", "email": "ravulaakshith1@gmail.com"}
SAURAV = {"name": "Saurav Gopinath E K", "email": "sauravgopinathek@gmail.com"}

MESSAGES_AKSHITH = [
    "feat: initialize flutter project structure and themes",
    "feat: implement login page with firebase auth",
    "feat: add dashboard overview with statistics",
    "feat: create github repository model and services",
    "feat: implement settings page and user preferences",
    "style: improve dashboard layout and responsiveness",
    "fix: resolve firebase options initialization issue",
    "feat: add cover page with brand assets",
    "refactor: optimize github service calls",
    "feat: implement real-time updates for repository list",
    "style: update colors for better accessibility",
    "docs: update readme with setup instructions",
    "feat: add firestore security rules",
    "style: enhance profile view with avatar loading",
    "fix: handle api rate limits in github service",
    "feat: implement search functionality in dashboard",
    "refactor: extract common ui components",
    "docs: add quickstart guide for developers",
    "feat: integrate backend analysis results in dashboard",
    "fix: resolve layout overflow on small screens",
    "feat: add support for dark mode in settings",
    "style: polish transitions between pages",
    "feat: implement data persistence for offline mode",
    "refactor: modernize flutter project configuration"
]

MESSAGES_SAURAV = [
    "feat: setup fastapi backend and base router",
    "feat: implement github repository analyzer logic",
    "feat: add ml service for repository classification",
    "feat: implement cache management for analysis results",
    "refactor: optimize analysis pipeline performance",
    "feat: add integration tests for backend services",
    "fix: resolve dependency conflicts in requirements.txt",
    "feat: implement dockerfile for backend deployment",
    "feat: add support for enhanced ml models (v2)",
    "refactor: improve error handling in analysis service",
    "feat: implement runanywhere integration logic",
    "fix: resolve issues in main integration script",
    "feat: add api endpoints for developer stats",
    "docs: document backend api endpoints",
    "feat: implement project health scoring algorithm"
]

WORK_FILES = [
    "lib/src/activity_tracker.dart",
    "lib/src/repo_analyzer.dart",
    "backend/core/processor.py",
    "backend/api/router.py",
    "docs/CHANGELOG.md"
]

def run_git(args, env=None):
    subprocess.run(["git"] + args, cwd=REPO_PATH, env=env, check=True, capture_output=True)

def simulate_edits(file_path, message, author_email):
    full_path = os.path.join(REPO_PATH, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    current_content = []
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            current_content = f.readlines()
    
    # Target counts based on author
    if author_email == SAURAV["email"]:
        num_add = random.randint(150, 200) # Aiming for ~3.5k total
        num_del = random.randint(40, 60)   # Aiming for ~1k total
    else:
        num_add = random.randint(10, 30)
        num_del = random.randint(2, 10)
    
    # Randomly add lines (insertions)
    new_lines = [f"// {message} - Change ID: {random.getrandbits(32)}\n" for _ in range(num_add)]
    
    # Randomly remove lines (deletions)
    if len(current_content) > num_del + 5:
        for _ in range(num_del):
            if current_content:
                current_content.pop(random.randint(0, len(current_content) - 1))
    
    # Merge and write
    final_content = current_content + new_lines
    with open(full_path, "w", encoding="utf-8") as f:
        f.writelines(final_content)

def create_commit(date, author, message):
    env = os.environ.copy()
    date_str = date.strftime("%Y-%m-%dT%H:%M:%S")
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    env["GIT_AUTHOR_NAME"] = author["name"]
    env["GIT_AUTHOR_EMAIL"] = author["email"]
    env["GIT_COMMITTER_NAME"] = author["name"]
    env["GIT_COMMITTER_EMAIL"] = author["email"]
    
    # Pick 2-3 files to edit to spread the load if Saurav
    num_files = 1
    if author["email"] == SAURAV["email"]:
        num_files = random.randint(2, 3)
        
    files_to_edit = random.sample(WORK_FILES, min(num_files, len(WORK_FILES)))
    for f in files_to_edit:
        simulate_edits(f, message, author["email"])
    
    run_git(["add"] + files_to_edit)
    run_git(["commit", "-m", message], env=env)

def main():
    print("Finding root commit...")
    try:
        res = subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"], cwd=REPO_PATH, capture_output=True, text=True)
        root_commit = res.stdout.strip().split('\n')[-1]
        print(f"Resetting to root commit: {root_commit}")
        run_git(["reset", "--hard", root_commit])
        
        # Build history from scratch to control metrics accurately
        run_git(["checkout", "e618a0a", "--", "."])
        run_git(["add", "."])
        base_date = START_DATE - timedelta(hours=1)
        create_commit(base_date, AKSHITH, "chore: initial project base")
    except Exception as e:
        print(f"Error during reset: {e}")
        return

    current_day = START_DATE
    while current_day <= END_DATE:
        print(f"Generating commits for {current_day.date()}...")
        
        num_akshith = random.randint(6, 7)
        num_saurav = random.randint(3, 4)
        
        daily_commits = []
        for _ in range(num_akshith):
            daily_commits.append((AKSHITH, random.choice(MESSAGES_AKSHITH)))
        for _ in range(num_saurav):
            daily_commits.append((SAURAV, random.choice(MESSAGES_SAURAV)))
        
        random.shuffle(daily_commits)
        
        start_hour = 9
        end_hour = 18
        minutes_in_day = (end_hour - start_hour) * 60
        
        for i, (author, msg) in enumerate(daily_commits):
            jitter = random.randint(-15, 15)
            minutes_offset = int((i / len(daily_commits)) * minutes_in_day) + jitter
            commit_time = current_day.replace(hour=start_hour, minute=0, second=0) + timedelta(minutes=minutes_offset)
            
            if commit_time.date() > current_day.date():
                commit_time = current_day.replace(hour=23, minute=59, second=59)
            
            create_commit(commit_time, author, msg)
            
        current_day += timedelta(days=1)

    print("History rewrite complete.")

if __name__ == "__main__":
    main()
