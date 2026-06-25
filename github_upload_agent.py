#!/usr/bin/env python3
"""
GitHub Upload Agent - Push code to GitHub with detailed progress
Usage: python github_upload_agent.py [--message "msg"] [--branch main] [--dry-run]
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Tuple, Optional
import argparse
from datetime import datetime

class GitHubUploadAgent:
    """Agent to upload code to GitHub with error handling"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.is_git_repo = (self.repo_path / ".git").exists()
    
    def print_header(self, text: str):
        """Print formatted header"""
        print("\n" + "╔" + "═" * 62 + "╗")
        print("║ " + text.center(60) + " ║")
        print("╚" + "═" * 62 + "╝" + "\n")
    
    def print_success(self, text: str):
        """Print success message"""
        print(f"✅ {text}")
    
    def print_error(self, text: str):
        """Print error message"""
        print(f"❌ {text}")
    
    def print_warning(self, text: str):
        """Print warning message"""
        print(f"⚠️  {text}")
    
    def print_info(self, text: str):
        """Print info message"""
        print(f"ℹ️  {text}")
    
    def print_status(self, text: str):
        """Print status message"""
        print(f"📊 {text}")
    
    def run_command(self, cmd: list, dry_run: bool = False) -> Tuple[int, str, str]:
        """Run shell command and return exit code, stdout, stderr"""
        cmd_str = " ".join(cmd)
        self.print_info(f"Running: {cmd_str}")
        
        if dry_run:
            self.print_warning(f"[DRY RUN] Would execute: {cmd_str}")
            return 0, "", ""
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)
    
    def init_repo(self) -> bool:
        """Initialize git repository if not already initialized"""
        if self.is_git_repo:
            self.print_success("Git repository already initialized")
            return True
        
        self.print_status("Initializing git repository...")
        code, out, err = self.run_command(["git", "init"])
        
        if code != 0:
            self.print_error(f"Failed to initialize git: {err}")
            return False
        
        self.print_success("Git repository initialized")
        return True
    
    def check_remote(self) -> Optional[str]:
        """Check if remote is configured"""
        code, out, err = self.run_command(["git", "config", "--get", "remote.origin.url"])
        
        if code == 0 and out.strip():
            return out.strip()
        return None
    
    def add_remote(self, remote_url: str) -> bool:
        """Add GitHub remote"""
        self.print_status(f"Adding remote: {remote_url}")
        code, out, err = self.run_command(["git", "remote", "add", "origin", remote_url])
        
        if code != 0:
            self.print_error(f"Failed to add remote: {err}")
            return False
        
        self.print_success("Remote added successfully")
        return True
    
    def get_status(self) -> str:
        """Get git status"""
        code, out, err = self.run_command(["git", "status", "--porcelain"])
        return out
    
    def stage_changes(self, dry_run: bool = False) -> bool:
        """Stage all changes"""
        self.print_status("Staging all changes...")
        code, out, err = self.run_command(["git", "add", "-A"], dry_run)
        
        if code != 0:
            self.print_error(f"Failed to stage changes: {err}")
            return False
        
        self.print_success("Changes staged")
        return True
    
    def get_staged_files(self) -> list:
        """Get list of staged files"""
        code, out, err = self.run_command(["git", "diff", "--name-only", "--cached"])
        if code == 0:
            return [f for f in out.strip().split("\n") if f]
        return []
    
    def commit_changes(self, message: str, dry_run: bool = False) -> bool:
        """Commit changes with message"""
        self.print_status(f"Creating commit: {message}")
        code, out, err = self.run_command(["git", "commit", "-m", message], dry_run)
        
        if code != 0:
            if "nothing to commit" in err or "nothing to commit" in out:
                self.print_warning("Nothing to commit")
                return False
            self.print_error(f"Failed to commit: {err}")
            return False
        
        self.print_success("Commit created")
        return True
    
    def get_current_branch(self) -> str:
        """Get current branch name"""
        code, out, err = self.run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        if code == 0:
            return out.strip()
        return "unknown"
    
    def get_commit_hash(self) -> str:
        """Get current commit hash"""
        code, out, err = self.run_command(["git", "rev-parse", "--short", "HEAD"])
        if code == 0:
            return out.strip()
        return "unknown"
    
    def push_to_github(self, branch: str, dry_run: bool = False) -> bool:
        """Push changes to GitHub"""
        self.print_status(f"Pushing to GitHub ({branch} branch)...")
        code, out, err = self.run_command(["git", "push", "origin", branch], dry_run)
        
        if code != 0:
            self.print_error(f"Failed to push: {err}")
            return False
        
        self.print_success(f"Code pushed to {branch} branch!")
        return True
    
    def get_github_url(self, remote_url: str) -> Optional[str]:
        """Extract GitHub URL from git remote"""
        if "github.com" not in remote_url:
            return None
        
        # Convert SSH to HTTPS
        if remote_url.startswith("git@"):
            remote_url = remote_url.replace(":", "/").replace("git@", "https://").replace(".git", "")
        elif remote_url.endswith(".git"):
            remote_url = remote_url[:-4]
        
        return remote_url
    
    def upload(self, commit_message: str, branch: str = "main", dry_run: bool = False) -> bool:
        """Complete upload workflow"""
        
        self.print_header("🚀 GitHub Upload Agent")
        
        # Step 1: Check repository
        self.print_header("Step 1: Check Repository")
        
        if not self.is_git_repo:
            self.print_warning("Not a git repository")
            if not self.init_repo():
                return False
            self.is_git_repo = True
        
        self.print_status(f"Repository path: {self.repo_path}")
        
        # Step 2: Check remote
        self.print_header("Step 2: Check Remote")
        
        remote_url = self.check_remote()
        if remote_url:
            self.print_status(f"Remote configured: {remote_url}")
        else:
            self.print_warning("No remote configured")
            print("\nTo add a remote:")
            print("  git remote add origin <GitHub-URL>")
            print("\nExample:")
            print("  git remote add origin https://github.com/username/my_ai_project.git")
            return False
        
        # Step 3: Check status
        self.print_header("Step 3: Check Git Status")
        
        status = self.get_status()
        if not status.strip():
            self.print_warning("No changes to commit")
            return False
        
        print("\nChanged files:")
        for line in status.strip().split("\n"):
            if line:
                status_code = line[0:2]
                filename = line[3:]
                emoji = "📝" if status_code[0] == "M" else "✨" if status_code[0] == "A" else "🗑️"
                print(f"  {emoji} {filename}")
        
        # Step 4: Stage changes
        self.print_header("Step 4: Stage Changes")
        
        if not self.stage_changes(dry_run):
            return False
        
        # Show staged files
        staged = self.get_staged_files()
        if staged:
            print(f"\nStaged {len(staged)} file(s)")
        
        # Step 5: Commit
        self.print_header("Step 5: Create Commit")
        
        if not self.commit_changes(commit_message, dry_run):
            return False
        
        commit_hash = self.get_commit_hash() if not dry_run else "preview"
        self.print_info(f"Commit hash: {commit_hash}")
        
        # Step 6: Push
        self.print_header("Step 6: Push to GitHub")
        
        if not self.push_to_github(branch, dry_run):
            return False
        
        # Step 7: Summary
        self.print_header("✅ Upload Summary")
        
        print(f"✓ Branch: {branch}")
        print(f"✓ Commit: {commit_hash}")
        print(f"✓ Message: {commit_message}")
        print(f"✓ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if remote_url:
            github_url = self.get_github_url(remote_url)
            if github_url:
                print(f"\n📌 View on GitHub: {github_url}")
        
        if dry_run:
            self.print_warning("This was a DRY RUN - no changes were actually made")
        else:
            self.print_success("Code successfully uploaded to GitHub!")
        
        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="GitHub Upload Agent - Push code to GitHub",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python github_upload_agent.py                    # Use defaults
  python github_upload_agent.py --message "Fix bug"  # Custom message
  python github_upload_agent.py --branch develop   # Push to develop
  python github_upload_agent.py --dry-run          # Preview changes
        """
    )
    
    parser.add_argument(
        "--message", "-m",
        default="Auto-upload from local development",
        help="Commit message (default: Auto-upload from local development)"
    )
    parser.add_argument(
        "--branch", "-b",
        default="main",
        help="Branch name (default: main)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without actually pushing"
    )
    parser.add_argument(
        "--repo",
        default=".",
        help="Repository path (default: current directory)"
    )
    
    args = parser.parse_args()
    
    # Create agent and upload
    agent = GitHubUploadAgent(args.repo)
    success = agent.upload(
        commit_message=args.message,
        branch=args.branch,
        dry_run=args.dry_run
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
