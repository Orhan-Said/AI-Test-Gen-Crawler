from git import Repo, GitCommandError
import os
import shutil
from dotenv import load_dotenv
import time

load_dotenv()


def integrate_with_repo(repo_url, files_to_add):
    """
    Integrate generated files into the GitHub repository.

    Args:
        repo_url (str): GitHub repository URL.
        files_to_add (dict): Dictionary of file paths and their contents.

    Raises:
        ValueError: If required parameters or environment variables are missing.
        GitCommandError: If git operations fail.
        OSError: If file operations fail.
    """
    if not repo_url or not files_to_add:
        raise ValueError("Repository URL and files to add are required")

    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")

    repo_dir = f"/tmp/repo_{int(time.time())}"  # Unique temp directory

    try:
        # Authenticate URL
        auth_repo_url = repo_url.replace(
            'https://', f'https://{github_token}@')

        # Clone repository
        try:
            repo = Repo.clone_from(auth_repo_url, repo_dir)
        except GitCommandError as e:
            raise GitCommandError(f"Failed to clone repository: {e}")

        # Create new branch
        branch_name = f"auto-generated-tests-{int(time.time())}"
        try:
            new_branch = repo.create_head(branch_name)
            new_branch.checkout()
        except GitCommandError as e:
            raise GitCommandError(f"Failed to create/checkout branch: {e}")

        # Add files
        for file_path, content in files_to_add.items():
            try:
                full_path = os.path.join(repo_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    f.write(content)
                repo.index.add([file_path])
            except OSError as e:
                raise OSError(f"Failed to write file {file_path}: {e}")

        # Commit and push
        try:
            repo.index.commit("Add auto-generated test cases and POMs")
            origin = repo.remote(name='origin')
            origin.push(refspec=f"{branch_name}:{branch_name}")
            print(f"Successfully pushed changes to branch: {branch_name}")
        except GitCommandError as e:
            raise GitCommandError(f"Failed to commit/push changes: {e}")

    except Exception as e:
        print(f"Error during repository integration: {e}")
        raise

    finally:
        # Clean up temporary directory
        try:
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
                print(f"Cleaned up temporary directory: {repo_dir}")
        except OSError as e:
            print(
                f"Warning: Failed to clean up temporary directory {repo_dir}: {e}")
