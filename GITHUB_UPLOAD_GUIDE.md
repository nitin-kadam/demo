# GitHub Upload Agent - Complete Guide

## 📌 What is the GitHub Upload Agent?

The GitHub Upload Agent is an automated tool that helps you push code changes from your local project to GitHub with just one command. It handles all the git operations (staging, committing, pushing) automatically.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Initialize Git & Add Remote (First Time Only)

```bash
# Initialize git repository
git init

# Add your GitHub repository as remote
# Replace URL with your actual GitHub repo URL
git remote add origin https://github.com/username/my_ai_project.git
# OR if using SSH:
git remote add origin git@github.com:username/my_ai_project.git
```

**How to get GitHub URL?**
- Go to your GitHub repository
- Click **Code** button (green button)
- Copy the HTTPS or SSH URL

### Step 2: Use the Upload Agent

**Option A: Python Agent (Recommended)**
```bash
python github_upload_agent.py --message "Add new features"
```

**Option B: Bash Agent**
```bash
chmod +x github_upload_agent.sh
./github_upload_agent.sh "Add new features"
```

### Step 3: Verify on GitHub

- Go to your GitHub repository
- Refresh the page
- See your new commits and files!

---

## 💻 Available Commands

### Python Agent (Recommended)

**Basic upload:**
```bash
python github_upload_agent.py
```

**Custom commit message:**
```bash
python github_upload_agent.py --message "Fix critical bug"
```

**Push to different branch:**
```bash
python github_upload_agent.py --message "New feature" --branch develop
```

**Preview changes (dry run):**
```bash
python github_upload_agent.py --dry-run
```

**Specify repository path:**
```bash
python github_upload_agent.py --repo /path/to/repo
```

**Combine options:**
```bash
python github_upload_agent.py \
  --message "Update documentation" \
  --branch main \
  --repo /Users/nitinkadam/Documents/projects/my_ai_project
```

### Bash Agent

**Basic upload:**
```bash
./github_upload_agent.sh
```

**Custom commit message:**
```bash
./github_upload_agent.sh "Update API tests"
```

**Push to different branch:**
```bash
./github_upload_agent.sh "Fix bugs" develop
```

---

## 🔧 What It Does (Step by Step)

### Automated Workflow

```
1. Check Repository
   ├─ Verify git is initialized
   └─ Show repository path

2. Check Remote
   ├─ Verify GitHub remote is configured
   └─ Display remote URL

3. Check Status
   ├─ List all changed files
   └─ Show file modifications

4. Stage Changes
   ├─ Run: git add -A
   └─ Prepare all changes

5. Create Commit
   ├─ Run: git commit -m "message"
   └─ Create commit with message

6. Push to GitHub
   ├─ Run: git push origin branch
   └─ Upload to GitHub

7. Summary
   ├─ Show commit hash
   ├─ Display GitHub URL
   └─ Confirm success
```

---

## 📊 Example Output

```
╔══════════════════════════════════════════════════════════╗
║              🚀 GitHub Upload Agent                     ║
╚══════════════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════════════╗
║              Step 1: Check Repository                  ║
╚══════════════════════════════════════════════════════════╝

ℹ️  Running: git init
✅ Git repository already initialized
📊 Repository path: /Users/nitinkadam/Documents/projects/my_ai_project

╔══════════════════════════════════════════════════════════╗
║              Step 2: Check Remote                       ║
╚══════════════════════════════════════════════════════════╝

ℹ️  Running: git config --get remote.origin.url
📊 Remote configured: https://github.com/nitinkadam/my_ai_project.git

╔══════════════════════════════════════════════════════════╗
║              Step 3: Check Git Status                   ║
╚══════════════════════════════════════════════════════════╝

Changed files:
  📝 test_api.py
  ✨ test_error_scenarios.py
  ✨ github_upload_agent.py
  📝 .github/copilot-instructions.md

╔══════════════════════════════════════════════════════════╗
║              Step 4: Stage Changes                      ║
╚══════════════════════════════════════════════════════════╝

📊 Staging all changes...
✅ Changes staged

Staged 4 file(s)

╔══════════════════════════════════════════════════════════╗
║              Step 5: Create Commit                      ║
╚══════════════════════════════════════════════════════════╝

📊 Creating commit: Add error handling and GitHub agent
ℹ️  Running: git commit -m "Add error handling and GitHub agent"
✅ Commit created
ℹ️  Commit hash: a1b2c3d

╔══════════════════════════════════════════════════════════╗
║              Step 6: Push to GitHub                     ║
╚══════════════════════════════════════════════════════════╝

📊 Pushing to GitHub (main branch)...
ℹ️  Running: git push origin main
✅ Code pushed to main branch!

╔══════════════════════════════════════════════════════════╗
║              ✅ Upload Summary                          ║
╚══════════════════════════════════════════════════════════╝

✓ Branch: main
✓ Commit: a1b2c3d
✓ Message: Add error handling and GitHub agent
✓ Timestamp: 2026-05-07 15:30:45

📌 View on GitHub: https://github.com/nitinkadam/my_ai_project

✅ Code successfully uploaded to GitHub!
```

---

## 🎯 Common Workflows

### Workflow 1: Daily Code Sync

```bash
# At end of day, push all changes
python github_upload_agent.py --message "Daily update: $(date +%Y-%m-%d)"
```

### Workflow 2: Feature Development

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes, then upload
python github_upload_agent.py \
  --message "Feature: Add new capability" \
  --branch feature/my-feature
```

### Workflow 3: Bug Fixes

```bash
# Make bug fix on main
python github_upload_agent.py --message "Fix: Critical bug in app.py"
```

### Workflow 4: Automated Testing Pipeline

Create a script (`auto_commit.sh`):
```bash
#!/bin/bash
# Run tests
pytest tests/

# If tests pass, upload
if [ $? -eq 0 ]; then
    python github_upload_agent.py --message "Tests passed: $(date)"
else
    echo "Tests failed - not uploading"
    exit 1
fi
```

Then run: `bash auto_commit.sh`

### Workflow 5: Dry Run Preview

```bash
# Preview what will be uploaded
python github_upload_agent.py --dry-run

# If preview looks good, actually upload
python github_upload_agent.py
```

---

## 🔐 First-Time GitHub Setup

### 1. Create GitHub Account (if needed)
- Go to https://github.com/join
- Sign up and create account

### 2. Create Repository on GitHub
- Log in to GitHub
- Click **+** → **New repository**
- Name: `my_ai_project`
- Description: Your project description
- Choose Public/Private
- Click **Create repository**

### 3. Configure Git (First Time)

```bash
# Set your GitHub username
git config --global user.name "Your Name"

# Set your GitHub email (use same as GitHub account)
git config --global user.email "your-email@example.com"

# Verify configuration
git config --global --list
```

### 4. Add Remote to Local Repository

```bash
cd /Users/nitinkadam/Documents/projects/my_ai_project

# Initialize git
git init

# Add GitHub remote (copy URL from GitHub repository page)
git remote add origin https://github.com/YOUR-USERNAME/my_ai_project.git

# Verify remote
git remote -v
```

### 5. Upload Initial Code

```bash
python github_upload_agent.py --message "Initial commit"
```

---

## 🆘 Troubleshooting

### Problem: "No remote configured"

**Solution:**
```bash
git remote add origin https://github.com/username/my_ai_project.git
```

### Problem: "Permission denied (publickey)"

**Solution:** Set up SSH keys
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Add key to GitHub
# 1. Go to GitHub Settings → SSH and GPG keys
# 2. New SSH key → Paste public key content

# Or use HTTPS instead of SSH
git remote set-url origin https://github.com/username/my_ai_project.git
```

### Problem: "Branch 'main' set up to track remote 'origin/main'"

**Solution:** First push requires `--set-upstream`
```bash
git push -u origin main
```

### Problem: "Everything up-to-date"

**Solution:** No changes to commit
```bash
# Make some changes to files, then try again
python github_upload_agent.py
```

### Problem: "fatal: not a git repository"

**Solution:** Initialize git first
```bash
git init
git remote add origin <GitHub-URL>
```

---

## 📋 Commit Message Best Practices

**Good commit messages:**
```
"Fix critical bug in API error handling"
"Add new test suite for validation"
"Update documentation"
"Refactor database queries"
"Add authentication to endpoints"
```

**Avoid:**
```
"fix"
"update"
"changes"
"asdf"
```

**Format:**
```
[Type]: [Brief description]

[Type] can be:
- Fix: Bug fixes
- Add: New features
- Update: Documentation or config
- Refactor: Code improvements
- Test: Test suite changes
```

Example:
```bash
python github_upload_agent.py --message "Fix: Handle API timeout gracefully"
```

---

## 🔄 Integrating with Your Workflow

### Option 1: Git Alias

Add to `.bashrc` or `.zshrc`:
```bash
alias upload='python github_upload_agent.py'
```

Then use:
```bash
upload --message "My changes"
```

### Option 2: Git Hook

Create `.git/hooks/post-commit`:
```bash
#!/bin/bash
echo "Commit created. Push with: python github_upload_agent.py"
```

### Option 3: VS Code Integration

Create `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Upload to GitHub",
      "type": "shell",
      "command": "python",
      "args": ["github_upload_agent.py"],
      "group": {
        "kind": "build",
        "isDefault": true
      }
    }
  ]
}
```

Then press `Ctrl+Shift+B` to run.

---

## 📚 Related Files

- `github_upload_agent.py` - Python implementation (recommended)
- `github_upload_agent.sh` - Bash implementation
- `.github/copilot-instructions.md` - AI agent instructions
- `API_TESTING_GUIDE.md` - Testing workflows
- `API_ERROR_HANDLING.md` - Error handling guide

---

## ✅ Summary

| Task | Command |
|------|---------|
| First time setup | `git init && git remote add origin <URL>` |
| Upload code | `python github_upload_agent.py` |
| Custom message | `python github_upload_agent.py --message "msg"` |
| Push to branch | `python github_upload_agent.py --branch develop` |
| Preview changes | `python github_upload_agent.py --dry-run` |
| Check status | `git status` |
| View logs | `git log` |
| View GitHub | Browser to your repo URL |

---

**Need help?** Run: `python github_upload_agent.py --help`
