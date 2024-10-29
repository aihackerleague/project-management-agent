"""
Test script for GitHub CLI wrapper
"""
import shutil
import time
from .github_cli_wrapper import GitHubCLI, GitHubCLIError

def verify_project_deleted(gh, project_number: str) -> bool:
    """Verify project was deleted by checking project list"""
    projects = gh.list_projects()
    return not any(
        p['number'] == int(project_number) 
        for p in projects.get('projects', [])
    )

def main():
    """Main test function"""
    try:
        # Setup
        print("Setting up GitHub CLI...")
        gh_path = shutil.which("gh")
        if not gh_path:
            raise Exception("GitHub CLI not found!")
        
        gh = GitHubCLI(gh_path)
        print("GitHub CLI setup complete")
        
        # List existing projects
        print("\nListing existing projects...")
        projects = gh.list_projects()
        initial_count = len(projects.get('projects', []))
        print(f"Found {initial_count} existing projects")
        
        # Create a project
        print("\nCreating test project...")
        project = gh.create_project("Test Project")
        project_number = project.get("number")
        print(f"Created project number: {project_number}")
        
        # View project
        print("\nViewing project...")
        viewed = gh.view_project(str(project_number))
        print(f"Project title: {viewed.get('title')}")
        
        # Edit project
        print("\nEditing project...")
        edited = gh.edit_project(str(project_number), "Updated Test Project")
        print(f"Updated title: {edited.get('title')}")
        
        # Delete project
        print("\nDeleting project...")
        deleted = gh.delete_project(str(project_number))
        print("Project deletion command completed")
        
        # Verify deletion
        time.sleep(2)  # Give GitHub a moment to process
        if verify_project_deleted(gh, str(project_number)):
            print("✅ Project successfully deleted")
        else:
            print("❌ Project may not have been deleted")
        
        print("\nAll operations completed!")
        
    except GitHubCLIError as e:
        print(f"\nGitHub CLI Error: {str(e)}")
        print(f"Error Details: {e.stderr}")
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    main()