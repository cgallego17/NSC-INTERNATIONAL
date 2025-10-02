#!/usr/bin/env python3
"""
Run Bandit security scan with proper configuration.
"""

import subprocess
import sys
import json
from pathlib import Path


def run_bandit_scan():
    """Run Bandit security scan with proper configuration."""
    print("Running Bandit Security Scan")
    print("=" * 40)

    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("ERROR: manage.py not found. Please run from project root.")
        return False

    # Run Bandit with proper configuration
    cmd = [
        "python",
        "-m",
        "bandit",
        "-r",
        ".",
        "-f",
        "json",
        "-o",
        "bandit-report.json",
        "--skip",
        "B101,B601,B602",  # Skip specific tests
        "--exclude",
        "scripts/check_github_security.py,scripts/enable_github_security.py,scripts/fix_workflow_issues.py,scripts/install_github_cli.py,scripts/setup_complete_security.py,scripts/setup_dev.py,scripts/setup_github_security.py,scripts/test_security_pipeline.py",
        "-x",
        "venv,.venv,staticfiles,media,logs,.git,__pycache__,.pytest_cache,.coverage,htmlcov,.tox,.mypy_cache,.DS_Store",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Bandit returns exit code 1 when issues are found, which is normal
        if result.returncode in [0, 1]:
            print("SUCCESS: Bandit scan completed")

            # Show summary
            if result.stdout:
                print("\nBandit Output:")
                print(result.stdout)

            # Check if report file was created
            if Path("bandit-report.json").exists():
                print("SUCCESS: Bandit report created: bandit-report.json")

                # Try to read and show summary
                try:
                    with open("bandit-report.json", "r") as f:
                        data = json.load(f)

                    total_issues = len(data.get("results", []))
                    print(f"Total security issues found: {total_issues}")

                    if total_issues > 0:
                        print("\nSecurity Issues Summary:")
                        severity_counts = {}
                        for issue in data.get("results", []):
                            severity = issue.get("issue_severity", "Unknown")
                            severity_counts[severity] = (
                                severity_counts.get(severity, 0) + 1
                            )

                        for severity, count in severity_counts.items():
                            print(f"  {severity}: {count}")

                    return True

                except json.JSONDecodeError:
                    print("WARNING: Could not parse Bandit JSON report")
                    return True
            else:
                print("WARNING: Bandit report file not created")
                return False
        else:
            print(f"ERROR: Bandit scan failed with exit code {result.returncode}")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            return False

    except Exception as e:
        print(f"ERROR: Failed to run Bandit: {e}")
        return False


def convert_to_sarif():
    """Convert Bandit JSON to SARIF format."""
    print("\nConverting Bandit results to SARIF...")

    try:
        # Import the conversion script
        from bandit_to_sarif import convert_bandit_to_sarif

        if convert_bandit_to_sarif("bandit-report.json", "bandit-sarif.json"):
            print("SUCCESS: SARIF conversion completed")
            return True
        else:
            print("ERROR: SARIF conversion failed")
            return False

    except ImportError:
        print("ERROR: bandit_to_sarif module not found")
        return False
    except Exception as e:
        print(f"ERROR: SARIF conversion failed: {e}")
        return False


def validate_sarif():
    """Validate SARIF format."""
    print("\nValidating SARIF format...")

    try:
        from validate_sarif_strict import main as validate_main

        # Temporarily modify sys.argv for validation
        original_argv = sys.argv
        sys.argv = ["validate_sarif_strict.py", "bandit-sarif.json"]

        try:
            validate_main()
            print("SUCCESS: SARIF validation passed")
            return True
        except SystemExit as e:
            if e.code == 0:
                print("SUCCESS: SARIF validation passed")
                return True
            else:
                print("ERROR: SARIF validation failed")
                return False
        finally:
            sys.argv = original_argv

    except ImportError:
        print("ERROR: validate_sarif_strict module not found")
        return False
    except Exception as e:
        print(f"ERROR: SARIF validation failed: {e}")
        return False


def main():
    """Main function."""
    print("Secure Bandit Security Scanner")
    print("=" * 40)

    # Run Bandit scan
    if not run_bandit_scan():
        print("ERROR: Bandit scan failed")
        sys.exit(1)

    # Convert to SARIF
    if not convert_to_sarif():
        print("WARNING: SARIF conversion failed")

    # Validate SARIF
    if not validate_sarif():
        print("WARNING: SARIF validation failed")

    print("\nSUCCESS: Security scan completed!")
    print("Check bandit-report.json and bandit-sarif.json for results")


if __name__ == "__main__":
    main()
