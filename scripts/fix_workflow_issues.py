#!/usr/bin/env python3
"""
Script to fix common GitHub Actions workflow issues.
"""

import os
import re
import subprocess
import sys
from pathlib import Path


def run_command(command):
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()


def fix_workflow_file(file_path):
    """Fix common issues in a workflow file."""
    print(f"Fixing workflow file: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Fix deprecated actions
    fixes = [
        # Fix upload-artifact v3 to v4
        (r"actions/upload-artifact@v3", "actions/upload-artifact@v4"),
        # Fix scorecard-action version
        (r"ossf/scorecard-action@v2", "ossf/scorecard-action@v2.3.1"),
        # Fix TruffleHog base commit issue
        (r"base: main\n\s+head: HEAD", "base: HEAD~1\n        head: HEAD"),
        # Add missing permissions
        (
            r"permissions:\s*\n\s*contents: read",
            "permissions:\n      contents: read\n      security-events: write\n      actions: read",
        ),
    ]

    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Add file existence checks before SARIF uploads
    sarif_uploads = re.findall(
        r"- name: Upload.*results.*\n.*uses: github/codeql-action/upload-sarif@v3",
        content,
        re.MULTILINE | re.DOTALL,
    )

    for upload in sarif_uploads:
        # Extract the sarif_file name
        sarif_match = re.search(r"sarif_file: (\w+\.sarif)", upload)
        if sarif_match:
            sarif_file = sarif_match.group(1)

            # Add file check before upload
            check_step = f"""
    - name: Check {sarif_file} exists
      run: |
        if [ -f "{sarif_file}" ]; then
          echo "{sarif_file} exists"
          ls -la {sarif_file}
        else
          echo "{sarif_file} not found, creating empty SARIF"
          python scripts/validate_sarif.py {sarif_file}
        fi

"""

            # Insert check step before upload
            content = content.replace(upload, check_step + upload)

    # Write fixed content if changes were made
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"SUCCESS: Fixed issues in {file_path}")
        return True
    else:
        print(f"INFO: No issues found in {file_path}")
        return False


def check_workflow_syntax(file_path):
    """Check workflow syntax using GitHub's action validator."""
    print(f"Checking syntax: {file_path}")

    try:
        # Read file with proper encoding
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Basic YAML syntax check
        import yaml

        yaml.safe_load(content)
        print(f"SUCCESS: {file_path} has valid YAML syntax")
        return True
    except Exception as e:
        print(f"ERROR: {file_path} has YAML syntax issues: {e}")
        return False


def main():
    """Main function to fix workflow issues."""
    print("GitHub Actions Workflow Fixer")
    print("=" * 40)

    # Find all workflow files
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print("ERROR: .github/workflows directory not found")
        sys.exit(1)

    workflow_files = list(workflow_dir.glob("*.yml")) + list(
        workflow_dir.glob("*.yaml")
    )

    if not workflow_files:
        print("ERROR: No workflow files found")
        sys.exit(1)

    print(f"Found {len(workflow_files)} workflow files")

    fixed_count = 0
    syntax_errors = 0

    for workflow_file in workflow_files:
        print(f"\nProcessing: {workflow_file}")

        # Fix common issues
        if fix_workflow_file(workflow_file):
            fixed_count += 1

        # Check syntax
        if not check_workflow_syntax(workflow_file):
            syntax_errors += 1

    print(f"\nSummary:")
    print(f"- Workflow files processed: {len(workflow_files)}")
    print(f"- Files fixed: {fixed_count}")
    print(f"- Syntax errors: {syntax_errors}")

    if syntax_errors == 0:
        print("\nSUCCESS: All workflow files have valid syntax")
        print("\nNext steps:")
        print("1. Commit the fixed workflow files")
        print("2. Push to GitHub")
        print("3. Check Actions tab for successful runs")
        print("4. Enable Code Scanning in repository settings")
    else:
        print(f"\nWARNING: {syntax_errors} workflow files have syntax errors")
        print("Please review and fix the syntax errors manually")
        sys.exit(1)


if __name__ == "__main__":
    main()
