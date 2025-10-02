#!/usr/bin/env python3
"""
Check Bandit report summary.
"""

import json
from pathlib import Path


def check_report(report_file):
    """Check Bandit report and show summary."""
    if not Path(report_file).exists():
        print(f"ERROR: Report file {report_file} not found")
        return False

    try:
        with open(report_file, "r") as f:
            data = json.load(f)

        total_issues = len(data.get("results", []))
        print(f"Total security issues found: {total_issues}")

        if total_issues > 0:
            print("\nSecurity Issues Summary:")
            severity_counts = {}
            for issue in data.get("results", []):
                severity = issue.get("issue_severity", "Unknown")
                severity_counts[severity] = severity_counts.get(severity, 0) + 1

            for severity, count in severity_counts.items():
                print(f"  {severity}: {count}")

        return True

    except Exception as e:
        print(f"ERROR: Could not read report: {e}")
        return False


def main():
    """Main function."""
    print("Bandit Report Checker")
    print("=" * 30)

    # Check both reports
    reports = ["bandit-report.json", "bandit-report-final.json"]

    for report in reports:
        if Path(report).exists():
            print(f"\nChecking {report}:")
            check_report(report)
        else:
            print(f"\n{report} not found")


if __name__ == "__main__":
    main()
