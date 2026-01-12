#!/usr/bin/env python3
"""
Script to install GitHub CLI on different platforms.
"""

import os
import platform
import subprocess
import sys


def run_command(command):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def install_github_cli_windows():
    """Install GitHub CLI on Windows."""
    print("Installing GitHub CLI on Windows...")

    # Try winget first
    success, output = run_command("winget install GitHub.cli")
    if success:
        print(f"SUCCESS: GitHub CLI installed via winget: {output}")
        return True

    # Try chocolatey
    success, output = run_command("choco install gh")
    if success:
        print(f"SUCCESS: GitHub CLI installed via chocolatey: {output}")
        return True

    # Try scoop
    success, output = run_command("scoop install gh")
    if success:
        print(f"SUCCESS: GitHub CLI installed via scoop: {output}")
        return True

    print("ERROR: Could not install GitHub CLI automatically")
    print("Please install manually from: https://cli.github.com/")
    return False


def install_github_cli_macos():
    """Install GitHub CLI on macOS."""
    print("Installing GitHub CLI on macOS...")

    # Try homebrew
    success, output = run_command("brew install gh")
    if success:
        print(f"SUCCESS: GitHub CLI installed via homebrew: {output}")
        return True

    print("ERROR: Could not install GitHub CLI automatically")
    print("Please install manually from: https://cli.github.com/")
    return False


def install_github_cli_linux():
    """Install GitHub CLI on Linux."""
    print("Installing GitHub CLI on Linux...")

    # Try apt (Ubuntu/Debian)
    if os.path.exists("/etc/debian_version"):
        commands = [
            "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg",
            "sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg",
            "echo 'deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main' | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null",
            "sudo apt update",
            "sudo apt install gh",
        ]

        for cmd in commands:
            success, output = run_command(cmd)
            if not success:
                print(f"ERROR: Failed to run: {cmd}")
                print(f"Output: {output}")
                return False

        print("SUCCESS: GitHub CLI installed via apt")
        return True

    # Try yum/dnf (RHEL/CentOS/Fedora)
    elif os.path.exists("/etc/redhat-release"):
        success, output = run_command("sudo dnf install 'dnf-command(config-manager)'")
        if success:
            success, output = run_command(
                "sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo"
            )
            if success:
                success, output = run_command("sudo dnf install gh")
                if success:
                    print("SUCCESS: GitHub CLI installed via dnf")
                    return True

    print("ERROR: Could not install GitHub CLI automatically")
    print("Please install manually from: https://cli.github.com/")
    return False


def check_github_cli():
    """Check if GitHub CLI is already installed."""
    success, output = run_command("gh --version")
    if success:
        print(f"SUCCESS: GitHub CLI already installed: {output}")
        return True
    return False


def main():
    """Main installation function."""
    print("GitHub CLI Installation Helper")
    print("=" * 40)

    # Check if already installed
    if check_github_cli():
        print("GitHub CLI is already installed!")
        return

    # Detect platform and install
    system = platform.system().lower()

    if system == "windows":
        install_github_cli_windows()
    elif system == "darwin":  # macOS
        install_github_cli_macos()
    elif system == "linux":
        install_github_cli_linux()
    else:
        print(f"ERROR: Unsupported platform: {system}")
        print("Please install GitHub CLI manually from: https://cli.github.com/")
        sys.exit(1)

    # Verify installation
    if check_github_cli():
        print("\nSUCCESS: GitHub CLI installation completed!")
        print("Next steps:")
        print("1. Run: gh auth login")
        print("2. Run: python scripts/enable_github_security.py")
    else:
        print("\nERROR: GitHub CLI installation failed")
        print("Please install manually from: https://cli.github.com/")


if __name__ == "__main__":
    main()
