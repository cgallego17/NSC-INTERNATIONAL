#!/usr/bin/env python3
"""
Automated setup script for GitHub Security features.
This script helps enable code scanning and other security features.
"""

import json
import subprocess
import sys
import time
from pathlib import Path


def run_gh_command(command, retries=3):
    """Run a GitHub CLI command with retries."""
    for attempt in range(retries):
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            return result.stdout.strip(), None
        except subprocess.CalledProcessError as e:
            if attempt == retries - 1:
                return None, e.stderr.strip()
            time.sleep(2)  # Wait before retry
    return None, "Max retries exceeded"


def check_prerequisites():
    """Check if prerequisites are met."""
    print("Checking prerequisites...")

    # Check GitHub CLI
    stdout, stderr = run_gh_command("gh --version")
    if not stdout:
        print(f"ERROR: GitHub CLI not found: {stderr}")
        return False

    print(f"SUCCESS: GitHub CLI: {stdout}")

    # Check authentication
    stdout, stderr = run_gh_command("gh auth status")
    if not stdout or "Logged in" not in stdout:
        print(f"ERROR: GitHub authentication failed: {stderr}")
        print("Please run: gh auth login")
        return False

    print(f"SUCCESS: GitHub authentication: {stdout}")

    # Check repository
    stdout, stderr = run_gh_command("gh repo view --json owner,name")
    if not stdout:
        print(f"ERROR: Not in a GitHub repository: {stderr}")
        return False

    try:
        repo_info = json.loads(stdout)
        print(f"SUCCESS: Repository: {repo_info['owner']['login']}/{repo_info['name']}")
        return repo_info
    except json.JSONDecodeError:
        print(f"ERROR: Could not parse repository info: {stdout}")
        return False


def enable_code_scanning():
    """Enable code scanning for the repository."""
    print("\nEnabling Code Scanning...")

    # Check current status
    stdout, stderr = run_gh_command(
        "gh api repos/:owner/:repo/code-scanning/alerts --method GET"
    )
    if stdout:
        print("SUCCESS: Code scanning is already enabled")
        return True

    print("WARNING: Code scanning is not enabled")
    print("Manual steps required:")
    print("1. Go to https://github.com/:owner/:repo/settings/security")
    print("2. Find 'Code scanning' section")
    print("3. Click 'Set up' or 'Enable'")
    print("4. Choose 'Set up this workflow' (recommended)")
    print("5. Configure Actions permissions if needed")

    return False


def enable_dependency_graph():
    """Enable dependency graph for the repository."""
    print("\nEnabling Dependency Graph...")

    # Check current status
    stdout, stderr = run_gh_command("gh api repos/:owner/:repo/dependency-graph/sbom")
    if stdout:
        print("SUCCESS: Dependency graph is already enabled")
        return True

    print("WARNING: Dependency graph is not enabled")
    print("Manual steps required:")
    print("1. Go to https://github.com/:owner/:repo/settings/security")
    print("2. Find 'Dependency graph' section")
    print("3. Enable 'Dependency graph'")
    print("4. Optionally enable 'Dependabot alerts'")
    print("5. Optionally enable 'Dependabot security updates'")

    return False


def enable_secret_scanning():
    """Enable secret scanning for the repository."""
    print("\nEnabling Secret Scanning...")

    # Check current status
    stdout, stderr = run_gh_command(
        "gh api repos/:owner/:repo/secret-scanning/alerts --method GET"
    )
    if stdout:
        print("SUCCESS: Secret scanning is already enabled")
        return True

    print("WARNING: Secret scanning is not enabled")
    print("Manual steps required:")
    print("1. Go to https://github.com/:owner/:repo/settings/security")
    print("2. Find 'Secret scanning' section")
    print("3. Enable 'Secret scanning'")
    print("4. Optionally enable 'Push protection'")

    return False


def configure_actions_permissions():
    """Configure GitHub Actions permissions."""
    print("\nConfiguring Actions Permissions...")

    # Check current permissions
    stdout, stderr = run_gh_command("gh api repos/:owner/:repo --jq '.permissions'")
    if stdout:
        try:
            permissions = json.loads(stdout)
            print("Current permissions:")
            for perm, value in permissions.items():
                status = "SUCCESS" if value else "ERROR"
                print(f"  {status}: {perm}: {value}")

            if permissions.get("admin", False):
                print("SUCCESS: Admin permissions available")
                return True
            else:
                print("WARNING: Admin permissions required for full setup")
                return False
        except json.JSONDecodeError:
            print(f"ERROR: Could not parse permissions: {stdout}")
            return False
    else:
        print(f"ERROR: Could not get permissions: {stderr}")
        return False


def generate_setup_instructions(repo_info):
    """Generate detailed setup instructions."""
    owner = repo_info["owner"]["login"]
    repo_name = repo_info["name"]

    print(f"\nSetup Instructions for {owner}/{repo_name}")
    print("=" * 60)

    print("\nDirect Links:")
    print(
        f"Security Settings: https://github.com/{owner}/{repo_name}/settings/security"
    )
    print(f"Actions Settings: https://github.com/{owner}/{repo_name}/settings/actions")
    print(f"Security Tab: https://github.com/{owner}/{repo_name}/security")

    print("\nStep-by-Step Instructions:")
    print("1. Go to Security Settings")
    print("2. Enable Code scanning:")
    print("   - Click 'Set up' in Code scanning section")
    print("   - Choose 'Set up this workflow'")
    print("   - Review and commit the workflow")

    print("\n3. Enable Dependency graph:")
    print("   - Enable 'Dependency graph'")
    print("   - Enable 'Dependabot alerts' (recommended)")
    print("   - Enable 'Dependabot security updates' (recommended)")

    print("\n4. Enable Secret scanning:")
    print("   - Enable 'Secret scanning'")
    print("   - Enable 'Push protection' (recommended)")

    print("\n5. Configure Actions permissions:")
    print("   - Go to Actions → General")
    print("   - Under 'Workflow permissions':")
    print("     - Select 'Read and write permissions'")
    print("     - Check 'Allow GitHub Actions to create and approve pull requests'")

    print("\n6. Test the setup:")
    print("   - Run a security workflow")
    print("   - Check Security tab for results")
    print("   - Verify no permission errors")


def main():
    """Main setup function."""
    print("GitHub Security Setup Assistant")
    print("=" * 40)

    # Check prerequisites
    repo_info = check_prerequisites()
    if not repo_info:
        sys.exit(1)

    # Check current status
    print("\nChecking current security features status...")
    code_scanning = enable_code_scanning()
    dependency_graph = enable_dependency_graph()
    secret_scanning = enable_secret_scanning()
    actions_perms = configure_actions_permissions()

    # Generate instructions
    generate_setup_instructions(repo_info)

    # Summary
    print(f"\nSummary:")
    print("-" * 20)
    features = [
        ("Code Scanning", code_scanning),
        ("Dependency Graph", dependency_graph),
        ("Secret Scanning", secret_scanning),
        ("Actions Permissions", actions_perms),
    ]

    enabled_count = sum(1 for _, enabled in features if enabled)
    total_count = len(features)

    for feature, enabled in features:
        status = "SUCCESS: Enabled" if enabled else "ERROR: Needs Setup"
        print(f"  {status} {feature}")

    print(f"\nOverall: {enabled_count}/{total_count} features ready")

    if enabled_count < total_count:
        print(f"\nWARNING: {total_count - enabled_count} features need manual setup")
        print("Please follow the instructions above to complete the setup.")
        print("\nAfter setup, run: python scripts/check_github_security.py")
        sys.exit(1)
    else:
        print("\nSUCCESS: All security features are enabled!")
        print("Your repository is ready for security scanning.")
        print("\nNext steps:")
        print("1. Run security workflows")
        print("2. Check Security tab for results")
        print("3. Configure alerts and notifications")


if __name__ == "__main__":
    main()
