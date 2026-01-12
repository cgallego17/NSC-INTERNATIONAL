#!/usr/bin/env python3
"""
Check GitHub Security features status for the repository.
This script verifies if code scanning and other security features are enabled.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_gh_command(command):
    """Run a GitHub CLI command and return the result."""
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, check=True
        )
        return result.stdout.strip(), None
    except subprocess.CalledProcessError as e:
        return None, e.stderr.strip()


def check_github_cli():
    """Check if GitHub CLI is installed."""
    stdout, stderr = run_gh_command("gh --version")
    if stdout:
        print(f"SUCCESS: GitHub CLI installed: {stdout}")
        return True
    else:
        print(f"ERROR: GitHub CLI not found: {stderr}")
        print("Please install GitHub CLI:")
        print("Windows: winget install GitHub.cli")
        print("macOS: brew install gh")
        print(
            "Linux: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
        )
        return False


def check_github_auth():
    """Check if user is authenticated with GitHub CLI."""
    stdout, stderr = run_gh_command("gh auth status")
    if stdout and "Logged in" in stdout:
        print(f"SUCCESS: GitHub authentication: {stdout}")
        return True
    else:
        print(f"ERROR: GitHub authentication failed: {stderr}")
        print("Please run: gh auth login")
        return False


def get_repository_info():
    """Get repository information."""
    stdout, stderr = run_gh_command("gh repo view --json owner,name,url")
    if stdout:
        try:
            repo_info = json.loads(stdout)
            return repo_info
        except json.JSONDecodeError:
            return None
    return None


def check_code_scanning():
    """Check if code scanning is enabled."""
    stdout, stderr = run_gh_command(
        "gh api repos/:owner/:repo/code-scanning/alerts --method GET"
    )
    if stdout:
        print("SUCCESS: Code scanning appears to be enabled")
        return True
    elif "404" in stderr or "not found" in stderr.lower():
        print("ERROR: Code scanning is not enabled")
        return False
    else:
        print(f"WARNING: Code scanning status unclear: {stderr}")
        return False


def check_dependency_graph():
    """Check if dependency graph is enabled."""
    stdout, stderr = run_gh_command("gh api repos/:owner/:repo/dependency-graph/sbom")
    if stdout:
        print("SUCCESS: Dependency graph appears to be enabled")
        return True
    elif "404" in stderr or "not found" in stderr.lower():
        print("ERROR: Dependency graph is not enabled")
        return False
    else:
        print(f"WARNING: Dependency graph status unclear: {stderr}")
        return False


def check_secret_scanning():
    """Check if secret scanning is enabled."""
    stdout, stderr = run_gh_command(
        "gh api repos/:owner/:repo/secret-scanning/alerts --method GET"
    )
    if stdout:
        print("SUCCESS: Secret scanning appears to be enabled")
        return True
    elif "404" in stderr or "not found" in stderr.lower():
        print("ERROR: Secret scanning is not enabled")
        return False
    else:
        print(f"WARNING: Secret scanning status unclear: {stderr}")
        return False


def check_repository_permissions():
    """Check repository permissions."""
    stdout, stderr = run_gh_command("gh api repos/:owner/:repo --jq '.permissions'")
    if stdout:
        try:
            permissions = json.loads(stdout)
            print("Repository permissions:")
            for perm, value in permissions.items():
                status = "SUCCESS" if value else "ERROR"
                print(f"  {status}: {perm}: {value}")
            return permissions
        except json.JSONDecodeError:
            print(f"ERROR: Could not parse permissions: {stdout}")
            return None
    else:
        print(f"ERROR: Could not get repository permissions: {stderr}")
        return None


def main():
    """Main function to check GitHub Security status."""
    print("Checking GitHub Security Features Status...")
    print("=" * 50)

    # Check prerequisites
    if not check_github_cli():
        sys.exit(1)

    if not check_github_auth():
        sys.exit(1)

    # Get repository info
    repo_info = get_repository_info()
    if repo_info:
        print(f"Repository: {repo_info['owner']['login']}/{repo_info['name']}")
        print(f"URL: {repo_info['url']}")
    else:
        print("ERROR: Could not get repository information")
        print("Make sure you're in a Git repository with GitHub remote")
        sys.exit(1)

    print("\nSecurity Features Status:")
    print("-" * 30)

    # Check security features
    code_scanning = check_code_scanning()
    dependency_graph = check_dependency_graph()
    secret_scanning = check_secret_scanning()

    print("\nRepository Permissions:")
    print("-" * 30)
    permissions = check_repository_permissions()

    print("\nSummary:")
    print("-" * 30)
    features = [
        ("Code Scanning", code_scanning),
        ("Dependency Graph", dependency_graph),
        ("Secret Scanning", secret_scanning),
    ]

    enabled_count = sum(1 for _, enabled in features if enabled)
    total_count = len(features)

    for feature, enabled in features:
        status = "SUCCESS: Enabled" if enabled else "ERROR: Disabled"
        print(f"  {status} {feature}")

    print(f"\nOverall: {enabled_count}/{total_count} features enabled")

    if enabled_count < total_count:
        print("\nTo enable missing features:")
        print(
            "1. Go to https://github.com/{}/settings/security".format(
                f"{repo_info['owner']['login']}/{repo_info['name']}"
            )
        )
        print("2. Enable Code scanning")
        print("3. Enable Dependency graph")
        print("4. Enable Secret scanning")
        print("5. Configure Actions permissions")
        print("\nSee GITHUB_SECURITY_SETUP.md for detailed instructions")
        sys.exit(1)
    else:
        print("\nAll security features are enabled!")
        print("Your repository is ready for security scanning.")


if __name__ == "__main__":
    main()
