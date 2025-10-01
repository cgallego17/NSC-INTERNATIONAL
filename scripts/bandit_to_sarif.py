#!/usr/bin/env python3
"""
Convert Bandit JSON output to SARIF format for GitHub Security tab.
"""

import json
import sys
from pathlib import Path


def convert_bandit_to_sarif(bandit_file, sarif_file):
    """Convert Bandit JSON output to SARIF format."""
    try:
        # Read Bandit JSON
        with open(bandit_file, "r", encoding="utf-8") as f:
            bandit_data = json.load(f)

        # Create SARIF structure
        sarif_data = {
            "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
            "version": "2.1.0",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "Bandit",
                            "version": "1.8.6",
                            "informationUri": "https://bandit.readthedocs.io/",
                        }
                    },
                    "results": [],
                }
            ],
        }

        # Convert Bandit results to SARIF results
        converted_count = 0
        for issue in bandit_data.get("results", []):
            # Map severity levels
            severity_map = {
                "LOW": "warning",
                "MEDIUM": "error",
                "HIGH": "error",
                "CRITICAL": "error",
            }

            sarif_result = {
                "ruleId": issue.get("test_id", "unknown"),
                "level": severity_map.get(
                    issue.get("issue_severity", "LOW"), "warning"
                ),
                "message": {"text": issue.get("issue_text", "")},
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {
                                "uri": issue.get("filename", "").replace("\\", "/")
                            },
                            "region": {
                                "startLine": issue.get("line_number", 1),
                                "startColumn": max(issue.get("col_offset", 1), 1),
                            },
                        }
                    }
                ],
            }

            # Add rule information in the correct SARIF format
            if "more_info" in issue:
                sarif_result["help"] = {
                    "text": f"More information: {issue['more_info']}"
                }

            sarif_data["runs"][0]["results"].append(sarif_result)
            converted_count += 1

        # Write SARIF file
        with open(sarif_file, "w", encoding="utf-8") as f:
            json.dump(sarif_data, f, indent=2)

        print(f"Converted {converted_count} Bandit issues to SARIF format")
        return True

    except Exception as e:
        print(f"Error converting Bandit to SARIF: {e}")
        return False


def main():
    """Main function."""
    if len(sys.argv) != 3:
        print(
            "Usage: python bandit_to_sarif.py <bandit_input.json> <sarif_output.json>"
        )
        sys.exit(1)

    bandit_file = sys.argv[1]
    sarif_file = sys.argv[2]

    if not Path(bandit_file).exists():
        print(f"Bandit file {bandit_file} not found")
        sys.exit(1)

    if convert_bandit_to_sarif(bandit_file, sarif_file):
        print(f"SARIF file created: {sarif_file}")
    else:
        print("Conversion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
