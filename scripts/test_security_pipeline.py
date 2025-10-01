#!/usr/bin/env python3
"""
Test script for the complete security pipeline.
This script tests all security tools and SARIF conversion.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"Testing: {description}")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"SUCCESS: {description}")
        return True
    except subprocess.CalledProcessError as e:
        # Bandit returns exit code 1 but still works (it's just informational)
        if "bandit" in command.lower() and e.returncode == 1:
            print(f"SUCCESS: {description} (Bandit completed with findings)")
            return True
        print(f"FAILED: {description}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def test_security_pipeline():
    """Test the complete security pipeline."""
    print("Testing Security Pipeline...")

    # Test commands
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
        if run_command(command, description):
            success_count += 1

    # Cleanup test files
    cleanup_files = ["test-bandit.json", "test-sarif.json"]
    for file in cleanup_files:
        try:
            Path(file).unlink(missing_ok=True)
        except Exception:
            pass

    print(f"\nTest Results: {success_count}/{len(tests)} tests passed")

    if success_count == len(tests):
        print("All security pipeline tests passed!")
        return True
    else:
        print("Some tests failed. Check the output above.")
        return False


def main():
    """Main function."""
    if not Path("manage.py").exists():
        print("Error: manage.py not found. Please run from project root.")
        sys.exit(1)

    success = test_security_pipeline()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
