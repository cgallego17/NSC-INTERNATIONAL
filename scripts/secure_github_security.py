#!/usr/bin/env python3
"""
Secure GitHub Security setup script without shell injection vulnerabilities.
"""

import json
import sys
from pathlib import Path
from secure_command_runner import run_gh_command, run_command_secure


def check_github_cli():
    """Check if GitHub CLI is available."""
    stdout, stderr = run_gh_command("--version")
    if stdout:
        print(f"SUCCESS: GitHub CLI found: {stdout}")
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


def check_auth():
    """Check GitHub authentication."""
    stdout, stderr = run_gh_command("auth status")
    if stdout and "Logged in" in stdout:
        print(f"SUCCESS: GitHub authentication: {stdout}")
        return True
    else:
        print(f"ERROR: GitHub authentication failed: {stderr}")
        print("Please run: gh auth login")
        return False


def get_repo_info():
    """Get repository information."""
    stdout, stderr = run_gh_command("repo view --json owner,name,url")
    if stdout:
        try:
            repo_info = json.loads(stdout)
            print(
                f"SUCCESS: Repository: {repo_info['owner']['login']}/{repo_info['name']}"
            )
            return repo_info
        except json.JSONDecodeError:
            print(f"ERROR: Could not parse repository info: {stdout}")
            return None
    else:
        print(f"ERROR: Not in a GitHub repository: {stderr}")
        return None


def check_code_scanning():
    """Check if code scanning is enabled."""
    stdout, stderr = run_gh_command(
        "api repos/:owner/:repo/code-scanning/alerts --method GET"
    )
    if stdout:
        print("SUCCESS: Code scanning is enabled")
        return True
    elif stderr and ("404" in stderr or "not found" in stderr.lower()):
        print("ERROR: Code scanning is not enabled")
        return False
    else:
        print(f"WARNING: Code scanning status unclear: {stderr}")
        return False


def show_setup_instructions(repo_info):
    """Show setup instructions."""
    owner = repo_info["owner"]["login"]
    repo_name = repo_info["name"]

    print("\n" + "=" * 60)
    print("GITHUB SECURITY SETUP INSTRUCTIONS")
    print("=" * 60)

    print(f"\nRepository: {owner}/{repo_name}")

    print("\nDIRECT LINKS:")
    print(
        f"Security Settings: https://github.com/{owner}/{repo_name}/settings/security"
    )
    print(f"Actions Settings: https://github.com/{owner}/{repo_name}/settings/actions")
    print(f"Security Tab: https://github.com/{owner}/{repo_name}/security")

    print("\nSTEP-BY-STEP INSTRUCTIONS:")
    print("1. Go to Security Settings (link above)")
    print("2. Enable Code scanning:")
    print("   - Find 'Code scanning' section")
    print("   - Click 'Set up' or 'Enable'")
    print("   - Choose 'Set up this workflow' (recommended)")
    print("   - Review and commit the workflow")

    print("\n3. Enable Dependency graph:")
    print("   - Enable 'Dependency graph'")
    print("   - Enable 'Dependabot alerts' (recommended)")
    print("   - Enable 'Dependabot security updates' (recommended)")

    print("\n4. Enable Secret scanning:")
    print("   - Enable 'Secret scanning'")
    print("   - Enable 'Push protection' (recommended)")

    print("\n5. Configure Actions permissions:")
    print("   - Go to Actions Settings (link above)")
    print("   - Under 'Workflow permissions':")
    print("     - Select 'Read and write permissions'")
    print("     - Check 'Allow GitHub Actions to create and approve pull requests'")

    print("\n6. Test the setup:")
    print("   - Run a security workflow")
    print("   - Check Security tab for results")
    print("   - Verify no permission errors")


def main():
    """Main function."""
    print("Secure GitHub Security Setup Helper")
    print("=" * 40)

    # Check prerequisites
    if not check_github_cli():
        sys.exit(1)

    if not check_auth():
        sys.exit(1)

    repo_info = get_repo_info()
    if not repo_info:
        sys.exit(1)

    # Check current status
    print("\nChecking security features...")
    code_scanning_enabled = check_code_scanning()

    if code_scanning_enabled:
        print("\nSUCCESS: Code scanning is already enabled!")
        print("Your repository is ready for security scanning.")
        print("\nNext steps:")
        print("1. Run security workflows")
        print("2. Check Security tab for results")
        print("3. Configure alerts and notifications")
    else:
        print("\nERROR: Code scanning is not enabled")
        print("This is required for SARIF uploads to work.")
        show_setup_instructions(repo_info)

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("Code scanning must be enabled in GitHub repository settings.")
        print("Follow the instructions above to complete the setup.")
        print("After setup, your security workflows will work correctly.")
        sys.exit(1)


if __name__ == "__main__":
    main()
