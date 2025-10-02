#!/usr/bin/env python3
"""
Secure command runner utility to avoid shell injection vulnerabilities.
"""

import subprocess
import shlex
import sys
from typing import Tuple, Optional, List


def run_command_secure(command: str, description: str = "") -> Tuple[bool, str, str]:
    """
    Run a command securely without shell=True to avoid injection vulnerabilities.

    Args:
        command: Command to run
        description: Description for logging

    Returns:
        Tuple of (success, stdout, stderr)
    """
    if description:
        print(f"Running: {description}")

    try:
        # Split command into parts for secure execution
        if isinstance(command, str):
            # Use shlex to properly parse the command
            cmd_parts = shlex.split(command)
        else:
            cmd_parts = command

        # Run command without shell=True
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            check=False,  # Don't raise exception on non-zero exit
        )

        success = result.returncode == 0
        return success, result.stdout.strip(), result.stderr.strip()

    except Exception as e:
        print(f"ERROR: Command failed: {e}")
        return False, "", str(e)


def run_command_with_retry(
    command: str, description: str = "", retries: int = 3
) -> Tuple[bool, str, str]:
    """
    Run a command with retry logic.

    Args:
        command: Command to run
        description: Description for logging
        retries: Number of retries

    Returns:
        Tuple of (success, stdout, stderr)
    """
    for attempt in range(retries):
        success, stdout, stderr = run_command_secure(command, description)

        if success:
            return True, stdout, stderr

        if attempt < retries - 1:
            print(f"Attempt {attempt + 1} failed, retrying...")
            import time

            time.sleep(2)

    return False, stdout, stderr


def run_gh_command(command: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Run a GitHub CLI command securely.

    Args:
        command: GitHub CLI command

    Returns:
        Tuple of (stdout, stderr)
    """
    success, stdout, stderr = run_command_secure(f"gh {command}")

    if success:
        return stdout, None
    else:
        return None, stderr


def run_python_command(command: str) -> Tuple[bool, str, str]:
    """
    Run a Python command securely.

    Args:
        command: Python command

    Returns:
        Tuple of (success, stdout, stderr)
    """
    return run_command_secure(f"python {command}")


def run_pip_command(command: str) -> Tuple[bool, str, str]:
    """
    Run a pip command securely.

    Args:
        command: pip command

    Returns:
        Tuple of (success, stdout, stderr)
    """
    return run_command_secure(f"pip {command}")


def check_file_exists(file_path: str) -> bool:
    """
    Check if a file exists.

    Args:
        file_path: Path to file

    Returns:
        True if file exists, False otherwise
    """
    import os

    return os.path.exists(file_path)


def get_file_content(file_path: str) -> Optional[str]:
    """
    Get file content safely.

    Args:
        file_path: Path to file

    Returns:
        File content or None if error
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def write_file_content(file_path: str, content: str) -> bool:
    """
    Write content to file safely.

    Args:
        file_path: Path to file
        content: Content to write

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    except Exception:
        return False


def main():
    """Test the secure command runner."""
    print("Secure Command Runner Test")
    print("=" * 40)

    # Test basic command
    success, stdout, stderr = run_command_secure(
        "python --version", "Python version check"
    )
    if success:
        print(f"SUCCESS: {stdout}")
    else:
        print(f"ERROR: {stderr}")

    # Test GitHub CLI
    stdout, stderr = run_gh_command("--version")
    if stdout:
        print(f"SUCCESS: GitHub CLI: {stdout}")
    else:
        print(f"ERROR: GitHub CLI not found: {stderr}")


if __name__ == "__main__":
    main()
