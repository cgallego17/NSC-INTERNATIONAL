#!/usr/bin/env python3
"""
Script to clean duplicate permissions in GitHub Actions workflows.
"""

import re
from pathlib import Path


def clean_permissions(content):
    """Clean duplicate permissions in workflow content."""
    # Find all permissions blocks
    permissions_pattern = (
        r"permissions:\s*\n((?:\s+[a-zA-Z-]+:\s*(?:read|write|admin)\s*\n?)*)"
    )

    def clean_permission_block(match):
        permissions_text = match.group(1)

        # Extract individual permissions
        permission_lines = re.findall(
            r"\s+([a-zA-Z-]+):\s*(read|write|admin)", permissions_text
        )

        # Remove duplicates while preserving order
        seen = set()
        unique_permissions = []
        for perm, access in permission_lines:
            if perm not in seen:
                seen.add(perm)
                unique_permissions.append(f"      {perm}: {access}")

        # Return cleaned permissions block
        if unique_permissions:
            return "permissions:\n" + "\n".join(unique_permissions) + "\n"
        else:
            return "permissions:\n      contents: read\n"

    # Apply cleaning to all permissions blocks
    cleaned_content = re.sub(
        permissions_pattern, clean_permission_block, content, flags=re.MULTILINE
    )

    return cleaned_content


def fix_workflow_file(file_path):
    """Fix permissions in a workflow file."""
    print(f"Cleaning permissions in: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Clean permissions
    content = clean_permissions(content)

    # Write cleaned content if changes were made
    if content != original_content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"SUCCESS: Cleaned permissions in {file_path}")
        return True
    else:
        print(f"INFO: No permission issues found in {file_path}")
        return False


def main():
    """Main function to clean workflow permissions."""
    print("GitHub Actions Permissions Cleaner")
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

    cleaned_count = 0

    for workflow_file in workflow_files:
        print(f"\nProcessing: {workflow_file}")

        if fix_workflow_file(workflow_file):
            cleaned_count += 1

    print(f"\nSummary:")
    print(f"- Workflow files processed: {len(workflow_files)}")
    print(f"- Files cleaned: {cleaned_count}")

    if cleaned_count > 0:
        print("\nSUCCESS: Permissions cleaned!")
        print("All duplicate permissions have been removed.")
    else:
        print("\nINFO: No permission issues found.")

    print("\nNext steps:")
    print("1. Commit the cleaned workflow files")
    print("2. Push to GitHub")
    print("3. Check Actions tab for successful runs")


if __name__ == "__main__":
    main()
