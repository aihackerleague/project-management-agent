"""
GitHub CLI wrapper module for project and issue management.
"""
import subprocess
import shutil
import json
import os
from typing import Dict, Any, Optional

class GitHubCLIError(Exception):
    """Custom exception for GitHub CLI errors"""
    def __init__(self, message: str, stderr: str):
        self.stderr = stderr
        super().__init__(message)

class GitHubCLI:
    """GitHub CLI wrapper for project and issue management"""
    
    def __init__(self, gh_path: str = None, gh_token: Optional[str] = None):
        """Initialize GitHub CLI wrapper"""
        gh_path = os.getenv("GITHUB_CLI_PATH", gh_path)
        if not gh_path:
            gh_path = shutil.which("gh")
        
        self.gh_path = gh_path  
        self.env = {
            **os.environ,
            "GITHUB_TOKEN": gh_token or os.getenv("GITHUB_TOKEN", "")
        }
        self._validate_cli()
        self.username = self._get_username()
        
    def _validate_cli(self):
        """Validate GitHub CLI is available and authenticated"""
        try:
            # Check version
            version = subprocess.run(
                [self.gh_path, "--version"],
                capture_output=True,
                text=True,
                env=self.env
            )
            if version.returncode != 0:
                raise GitHubCLIError("GitHub CLI not available", version.stderr)
                
            # Check auth status
            auth = subprocess.run(
                [self.gh_path, "auth", "status"],
                capture_output=True,
                text=True,
                env=self.env
            )
            if auth.returncode != 0:
                raise GitHubCLIError("GitHub CLI not authenticated", auth.stderr)
                
        except FileNotFoundError:
            raise GitHubCLIError(
                f"GitHub CLI not found at: {self.gh_path}",
                "FileNotFoundError"
            )

    def _get_username(self) -> str:
        """Get current GitHub username"""
        result = subprocess.run(
            [self.gh_path, "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            env=self.env
        )
        if result.returncode != 0:
            raise GitHubCLIError("Failed to get username", result.stderr)
        return result.stdout.strip()

    def run_command(self, command: list[str], debug: bool = True) -> Dict[str, Any]:
        """Run a GitHub CLI command"""
        try:
            full_command = [self.gh_path] + command
            if debug:
                print(f"Running command: {' '.join(full_command)}")
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                env=self.env
            )
            
            if result.returncode != 0:
                if debug:
                    print(f"Command failed with stderr: {result.stderr}")
                raise GitHubCLIError(
                    "GitHub CLI command failed",
                    result.stderr
                )
            
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {"output": result.stdout.strip()}
            
        except Exception as e:
            if not isinstance(e, GitHubCLIError):
                raise GitHubCLIError(
                    "Command execution failed",
                    str(e)
                )
            raise

    # Project Operations
    def list_projects(self) -> Dict[str, Any]:
        """List GitHub projects for current user"""
        return self.run_command([
            "project",
            "list",
            "--format", "json"
        ])

    def create_project(self, title: str) -> Dict[str, Any]:
        """Create a new GitHub project"""
        return self.run_command([
            "project",
            "create",
            "--owner", self.username,  # Required for non-interactive mode
            "--title", title,
            "--format", "json"
        ])

    def view_project(self, number: str) -> Dict[str, Any]:
        """View a GitHub project by number"""
        return self.run_command([
            "project",
            "view",
            number,
            "--owner", self.username,  # Be explicit about owner
            "--format", "json"
        ])

    def edit_project(self, number: str, title: str) -> Dict[str, Any]:
        """Edit a GitHub project"""
        return self.run_command([
            "project",
            "edit",
            number,
            "--owner", self.username,  # Be explicit about owner
            "--title", title,
            "--format", "json"
        ])

    def delete_project(self, number: str) -> Dict[str, Any]:
        """Delete a GitHub project"""
        return self.run_command([
            "project",
            "delete",
            number,
            "--owner", self.username,
            "--format", "json"
        ])

    # Issue Operations remain the same as they use different command structure
    def list_issues(self) -> Dict[str, Any]:
        """List issues for current repo"""
        return self.run_command([
            "issue",
            "list",
            "--format", "json"
        ])

    def create_issue(self, title: str, body: str) -> Dict[str, Any]:
        """Create a new issue"""
        return self.run_command([
            "issue",
            "create",
            "--title", title,
            "--body", body,
            "--format", "json"
        ])

    def edit_issue(self, number: str, title: Optional[str] = None, 
                  body: Optional[str] = None) -> Dict[str, Any]:
        """Edit an issue"""
        command = ["issue", "edit", number, "--format", "json"]
        if title:
            command.extend(["--title", title])
        if body:
            command.extend(["--body", body])
        return self.run_command(command)

    def close_issue(self, number: str) -> Dict[str, Any]:
        """Close an issue"""
        return self.run_command([
            "issue",
            "close",
            number,
            "--format", "json"
        ])