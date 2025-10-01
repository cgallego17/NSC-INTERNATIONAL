#!/usr/bin/env python3
"""
Complete security setup script for NSC International.
This script sets up everything needed for GitHub Security.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_command(command, description=""):
    """Run a command and return success status."""
    print(f"Running: {description or command}")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"SUCCESS: {description or command}")
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {description or command}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False, e.stderr.strip()


def check_prerequisites():
    """Check all prerequisites."""
    print("Checking prerequisites...")

    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("ERROR: manage.py not found. Please run from project root.")
        return False

    # Check Python
    success, output = run_command("python --version", "Python version check")
    if not success:
        print("ERROR: Python not found")
        return False

    # Check Git
    success, output = run_command("git --version", "Git version check")
    if not success:
        print("ERROR: Git not found")
        return False

    # Check if this is a GitHub repository
    success, output = run_command("git remote get-url origin", "Git remote check")
    if not success or "github.com" not in output:
        print("ERROR: Not a GitHub repository")
        print("Please ensure your repository is hosted on GitHub")
        return False

    print("SUCCESS: All prerequisites met")
    return True


def install_security_tools():
    """Install security tools."""
    print("\nInstalling security tools...")

    tools = [
        ("pip install --upgrade pip", "Upgrade pip"),
        ("pip install -r requirements.txt", "Install project dependencies"),
        ("pip install -r requirements-security.txt", "Install security tools"),
        (
            "pip install black isort flake8 mypy pre-commit",
            "Install code quality tools",
        ),
    ]

    success_count = 0
    for command, description in tools:
        success, output = run_command(command, description)
        if success:
            success_count += 1

    print(f"SUCCESS: {success_count}/{len(tools)} tools installed")
    return success_count == len(tools)


def setup_code_formatting():
    """Setup code formatting."""
    print("\nSetting up code formatting...")

    # Apply formatting
    success1, _ = run_command("python -m black .", "Apply Black formatting")
    success2, _ = run_command("python -m isort .", "Apply import sorting")

    if success1 and success2:
        print("SUCCESS: Code formatting applied")
        return True
    else:
        print("ERROR: Code formatting failed")
        return False


def test_security_pipeline():
    """Test the security pipeline."""
    print("\nTesting security pipeline...")

    tests = [
        ("python -m safety check --short-report", "Safety vulnerability check"),
        (
            "python -m bandit -r . -f json -o test-bandit.json --skip B101,B601",
            "Bandit security scan",
        ),
        (
            "python scripts/bandit_to_sarif.py test-bandit.json test-sarif.json",
            "SARIF conversion",
        ),
        ("python scripts/validate_sarif_strict.py test-sarif.json", "SARIF validation"),
        ("python -m black --check .", "Black formatting check"),
        ("python -m isort --check-only .", "Import sorting check"),
        ("python -m flake8 . --count --select=E9,F63,F7,F82", "Critical linting check"),
    ]

    success_count = 0
    for command, description in tests:
        success, output = run_command(command, description)
        if success:
            success_count += 1
        elif "bandit" in command.lower() and "Working..." in output:
            # Bandit returns exit code 1 but still works
            print(f"SUCCESS: {description} (Bandit completed with findings)")
            success_count += 1

    # Cleanup test files
    cleanup_files = ["test-bandit.json", "test-sarif.json"]
    for file in cleanup_files:
        try:
            Path(file).unlink(missing_ok=True)
        except Exception:
            pass

    print(f"SUCCESS: {success_count}/{len(tests)} security tests passed")
    return success_count == len(tests)


def check_github_security():
    """Check GitHub Security status."""
    print("\nChecking GitHub Security status...")

    # Check GitHub CLI
    success, output = run_command("gh --version", "GitHub CLI check")
    if not success:
        print("ERROR: GitHub CLI not found")
        print("Please install GitHub CLI:")
        print("Windows: winget install GitHub.cli")
        print("macOS: brew install gh")
        print(
            "Linux: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
        )
        return False

    # Check authentication
    success, output = run_command("gh auth status", "GitHub authentication check")
    if not success or "Logged in" not in output:
        print("ERROR: GitHub authentication failed")
        print("Please run: gh auth login")
        return False

    # Check code scanning
    success, output = run_command(
        "gh api repos/:owner/:repo/code-scanning/alerts --method GET",
        "Code scanning check",
    )
    if success:
        print("SUCCESS: Code scanning is enabled")
        return True
    elif "404" in output or "not found" in output.lower():
        print("ERROR: Code scanning is not enabled")
        print("This is required for SARIF uploads to work.")
        return False
    else:
        print(f"WARNING: Code scanning status unclear: {output}")
        return False


def show_final_instructions():
    """Show final setup instructions."""
    print("\n" + "=" * 60)
    print("SETUP COMPLETE - NEXT STEPS")
    print("=" * 60)

    print("\n1. ENABLE GITHUB SECURITY:")
    print("   - Go to your repository on GitHub")
    print("   - Click Settings -> Security")
    print("   - Enable 'Code scanning'")
    print("   - Enable 'Dependency graph'")
    print("   - Enable 'Secret scanning'")

    print("\n2. CONFIGURE ACTIONS PERMISSIONS:")
    print("   - Go to Settings -> Actions -> General")
    print("   - Under 'Workflow permissions':")
    print("     - Select 'Read and write permissions'")
    print("     - Check 'Allow GitHub Actions to create and approve pull requests'")

    print("\n3. TEST THE SETUP:")
    print("   - Push your changes to GitHub")
    print("   - Check Actions tab for workflow runs")
    print("   - Check Security tab for results")

    print("\n4. AVAILABLE SCRIPTS:")
    print("   - python scripts/enable_github_security.py")
    print("   - python scripts/check_github_security.py")
    print("   - python scripts/test_security_pipeline.py")

    print("\n5. DOCUMENTATION:")
    print("   - GITHUB_SECURITY_SETUP.md")
    print("   - GITHUB_SECURITY_SOLUTION.md")
    print("   - DEVELOPMENT_SETUP.md")


def main():
    """Main setup function."""
    print("NSC International - Complete Security Setup")
    print("=" * 50)

    # Check prerequisites
    if not check_prerequisites():
        sys.exit(1)

    # Install security tools
    if not install_security_tools():
        print("WARNING: Some security tools failed to install")

    # Setup code formatting
    if not setup_code_formatting():
        print("WARNING: Code formatting setup failed")

    # Test security pipeline
    if not test_security_pipeline():
        print("WARNING: Some security tests failed")

    # Check GitHub Security
    github_ready = check_github_security()

    # Show final instructions
    show_final_instructions()

    if github_ready:
        print("\nSUCCESS: Complete security setup finished!")
        print("Your repository is ready for security scanning.")
    else:
        print("\nWARNING: GitHub Security features need to be enabled manually.")
        print("Follow the instructions above to complete the setup.")

    print("\nSetup completed successfully!")


if __name__ == "__main__":
    main()
