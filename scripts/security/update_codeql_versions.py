#!/usr/bin/env python3
"""
Script to update all CodeQL Action versions to v3.
"""

import re
from pathlib import Path


def update_codeql_versions(content):
    """Update all CodeQL Action versions to v3."""
    # Update all github/codeql-action versions to v3
    patterns = [
        (
            r"github/codeql-action/upload-sarif@v[12]",
            "github/codeql-action/upload-sarif@v3",
        ),
        (r"github/codeql-action/init@v[12]", "github/codeql-action/init@v3"),
        (r"github/codeql-action/analyze@v[12]", "github/codeql-action/analyze@v3"),
        (r"github/codeql-action/autobuild@v[12]", "github/codeql-action/autobuild@v3"),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    return content


def fix_workflow_file(file_path):
    """Fix CodeQL versions in a workflow file."""
    print(f"Updating CodeQL versions in: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Update CodeQL versions
    content = update_codeql_versions(content)

    # Write updated content if changes were made
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"SUCCESS: Updated CodeQL versions in {file_path}")
        return True
    else:
        print(f"INFO: No CodeQL version issues found in {file_path}")
        return False


def main():
    """Main function to update CodeQL versions."""
    print("CodeQL Action Version Updater")
    print("=" * 40)

    # Find all workflow files
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print("ERROR: .github/workflows directory not found")
        return

    workflow_files = list(workflow_dir.glob("*.yml")) + list(
        workflow_dir.glob("*.yaml")
    )

    if not workflow_files:
        print("ERROR: No workflow files found")
        return

    print(f"Found {len(workflow_files)} workflow files")

    updated_count = 0

    for workflow_file in workflow_files:
        print(f"\nProcessing: {workflow_file}")

        if fix_workflow_file(workflow_file):
            updated_count += 1

    print(f"\nSummary:")
    print(f"- Workflow files processed: {len(workflow_files)}")
    print(f"- Files updated: {updated_count}")

    if updated_count > 0:
        print("\nSUCCESS: CodeQL versions updated!")
        print("All CodeQL Action versions have been updated to v3.")
    else:
        print("\nINFO: No CodeQL version issues found.")

    print("\nNext steps:")
    print("1. Commit the updated workflow files")
    print("2. Push to GitHub")
    print("3. Check Actions tab for successful runs")
    print("4. Enable Code Scanning in repository settings")


if __name__ == "__main__":
    main()
