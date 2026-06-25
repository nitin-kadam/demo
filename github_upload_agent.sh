#!/bin/bash
# GitHub Upload Agent - Push code changes to GitHub automatically
# Usage: ./github_upload_agent.sh [commit-message] [branch]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
COMMIT_MSG="${1:-Auto-upload from local development}"
BRANCH="${2:-main}"
REPO_URL=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[📊]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✅]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠️ ]${NC} $1"
}

print_header() {
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║ $1"
    echo "╚════════════════════════════════════════════════════════════╝"
}

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Main workflow
main() {
    print_header "🚀 GitHub Upload Agent"
    
    # Check if we're in a git repository
    if [ ! -d .git ]; then
        print_error "Not a git repository. Initialize with: git init"
        exit 1
    fi
    
    print_status "Repository: $(pwd)"
    
    # Get current branch
    CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
    print_status "Current Branch: $CURRENT_BRANCH"
    
    # Get remote URL
    if git config --get remote.origin.url > /dev/null 2>&1; then
        REPO_URL=$(git config --get remote.origin.url)
        print_status "Remote: $REPO_URL"
    else
        print_warning "No remote configured. Use: git remote add origin <url>"
    fi
    
    # Step 1: Check git status
    print_header "📋 Step 1: Check Git Status"
    
    if git diff-index --quiet HEAD -- ; then
        print_warning "No changes to commit"
        echo ""
        echo "Current status:"
        git status
        exit 0
    fi
    
    # Show what will be committed
    echo ""
    print_status "Changed files:"
    git diff --name-only --cached
    git diff --name-only
    
    # Step 2: Add all changes
    print_header "📝 Step 2: Stage Changes"
    
    print_status "Staging all changes..."
    git add -A
    print_success "All changes staged"
    
    # Show staged files
    echo ""
    print_status "Staged files:"
    git diff --name-only --cached
    
    # Step 3: Create commit
    print_header "💾 Step 3: Create Commit"
    
    print_status "Commit message: $COMMIT_MSG"
    git commit -m "$COMMIT_MSG"
    print_success "Commit created"
    
    # Step 4: Push to GitHub
    print_header "📤 Step 4: Push to GitHub"
    
    if [ -z "$REPO_URL" ]; then
        print_error "No remote configured. Cannot push."
        print_status "Configure remote with: git remote add origin <GitHub-URL>"
        exit 1
    fi
    
    print_status "Pushing to remote ($BRANCH branch)..."
    git push origin $BRANCH
    print_success "Code pushed to GitHub!"
    
    # Step 5: Summary
    print_header "✅ Upload Complete"
    
    echo ""
    print_status "Summary:"
    echo "  Branch: $BRANCH"
    echo "  Commit: $(git rev-parse --short HEAD)"
    echo "  Message: $COMMIT_MSG"
    echo ""
    
    # Show GitHub link
    if [[ $REPO_URL == *"github.com"* ]]; then
        REPO_LINK=$(echo $REPO_URL | sed 's/.*github.com[/:]\([^/]*\)\/\([^/]*\)\.git/https:\/\/github.com\/\1\/\2/')
        print_status "View on GitHub: $REPO_LINK"
    fi
    
    echo ""
}

# Show help
if [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
    echo "GitHub Upload Agent - Push code to GitHub automatically"
    echo ""
    echo "Usage: $0 [commit-message] [branch]"
    echo ""
    echo "Arguments:"
    echo "  commit-message  - Commit message (default: 'Auto-upload from local development')"
    echo "  branch          - Branch name (default: 'main')"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Use defaults"
    echo "  $0 'Add new features'                 # Custom message"
    echo "  $0 'Bug fix' develop                  # Custom message and branch"
    echo ""
    echo "Setup:"
    echo "  1. Initialize git: git init"
    echo "  2. Add remote: git remote add origin <GitHub-URL>"
    echo "  3. Run: $0"
    echo ""
    exit 0
fi

# Run main function
main
