#!/usr/bin/env python3
"""
Strict SARIF validation script for GitHub Security tab compatibility.
This script validates SARIF files against GitHub's specific requirements.
"""

import json
import sys
from pathlib import Path


def validate_github_sarif(data):
    """Validate SARIF data against GitHub's specific requirements."""
    errors = []

    # Check basic structure
    if not isinstance(data, dict):
        errors.append("SARIF data must be a JSON object")
        return errors

    if "$schema" not in data:
        errors.append("Missing required $schema field")

    if "version" not in data:
        errors.append("Missing required version field")
    elif data["version"] != "2.1.0":
        errors.append("Version must be 2.1.0")

    if "runs" not in data:
        errors.append("Missing required runs field")
        return errors

    if not isinstance(data["runs"], list):
        errors.append("runs must be an array")
        return errors

    if len(data["runs"]) == 0:
        errors.append("runs array cannot be empty")
        return errors

    # Validate each run
    for i, run in enumerate(data["runs"]):
        run_errors = validate_run(run, i)
        errors.extend(run_errors)

    return errors


def validate_run(run, run_index):
    """Validate a single SARIF run."""
    errors = []

    if not isinstance(run, dict):
        errors.append(f"runs[{run_index}] must be an object")
        return errors

    # Check required fields
    if "tool" not in run:
        errors.append(f"runs[{run_index}] missing required tool field")
    else:
        tool_errors = validate_tool(run["tool"], run_index)
        errors.extend(tool_errors)

    if "results" not in run:
        errors.append(f"runs[{run_index}] missing required results field")
    else:
        results_errors = validate_results(run["results"], run_index)
        errors.extend(results_errors)

    return errors


def validate_tool(tool, run_index):
    """Validate tool information."""
    errors = []

    if not isinstance(tool, dict):
        errors.append(f"runs[{run_index}].tool must be an object")
        return errors

    if "driver" not in tool:
        errors.append(f"runs[{run_index}].tool missing required driver field")
    else:
        driver = tool["driver"]
        if not isinstance(driver, dict):
            errors.append(f"runs[{run_index}].tool.driver must be an object")
        else:
            if "name" not in driver:
                errors.append(
                    f"runs[{run_index}].tool.driver missing required name field"
                )

    return errors


def validate_results(results, run_index):
    """Validate results array."""
    errors = []

    if not isinstance(results, list):
        errors.append(f"runs[{run_index}].results must be an array")
        return errors

    # Validate each result
    for i, result in enumerate(results):
        result_errors = validate_result(result, run_index, i)
        errors.extend(result_errors)

    return errors


def validate_result(result, run_index, result_index):
    """Validate a single SARIF result."""
    errors = []

    if not isinstance(result, dict):
        errors.append(f"runs[{run_index}].results[{result_index}] must be an object")
        return errors

    # Check required fields
    if "ruleId" not in result:
        errors.append(
            f"runs[{run_index}].results[{result_index}] missing required ruleId field"
        )

    if "level" not in result:
        errors.append(
            f"runs[{run_index}].results[{result_index}] missing required level field"
        )
    else:
        valid_levels = ["error", "warning", "note"]
        if result["level"] not in valid_levels:
            errors.append(
                f"runs[{run_index}].results[{result_index}].level must be one of {valid_levels}"
            )

    if "message" not in result:
        errors.append(
            f"runs[{run_index}].results[{result_index}] missing required message field"
        )
    else:
        message_errors = validate_message(result["message"], run_index, result_index)
        errors.extend(message_errors)

    if "locations" not in result:
        errors.append(
            f"runs[{run_index}].results[{result_index}] missing required locations field"
        )
    else:
        location_errors = validate_locations(
            result["locations"], run_index, result_index
        )
        errors.extend(location_errors)

    # Check for invalid properties
    invalid_properties = ["helpUri"]  # GitHub doesn't support this
    for prop in invalid_properties:
        if prop in result:
            errors.append(
                f"runs[{run_index}].results[{result_index}] contains invalid property '{prop}'"
            )

    return errors


def validate_message(message, run_index, result_index):
    """Validate message object."""
    errors = []

    if not isinstance(message, dict):
        errors.append(
            f"runs[{run_index}].results[{result_index}].message must be an object"
        )
        return errors

    if "text" not in message:
        errors.append(
            f"runs[{run_index}].results[{result_index}].message missing required text field"
        )

    return errors


def validate_locations(locations, run_index, result_index):
    """Validate locations array."""
    errors = []

    if not isinstance(locations, list):
        errors.append(
            f"runs[{run_index}].results[{result_index}].locations must be an array"
        )
        return errors

    if len(locations) == 0:
        errors.append(
            f"runs[{run_index}].results[{result_index}].locations cannot be empty"
        )
        return errors

    # Validate each location
    for i, location in enumerate(locations):
        location_errors = validate_location(location, run_index, result_index, i)
        errors.extend(location_errors)

    return errors


def validate_location(location, run_index, result_index, location_index):
    """Validate a single location."""
    errors = []

    if not isinstance(location, dict):
        errors.append(
            f"runs[{run_index}].results[{result_index}].locations[{location_index}] must be an object"
        )
        return errors

    if "physicalLocation" not in location:
        errors.append(
            f"runs[{run_index}].results[{result_index}].locations[{location_index}] missing required physicalLocation field"
        )
    else:
        phys_loc_errors = validate_physical_location(
            location["physicalLocation"], run_index, result_index, location_index
        )
        errors.extend(phys_loc_errors)

    return errors


def validate_physical_location(phys_loc, run_index, result_index, location_index):
    """Validate physical location."""
    errors = []

    if not isinstance(phys_loc, dict):
        errors.append(
            f"runs[{run_index}].results[{result_index}].locations[{location_index}].physicalLocation must be an object"
        )
        return errors

    if "artifactLocation" not in phys_loc:
        errors.append(
            f"runs[{run_index}].results[{result_index}].locations[{location_index}].physicalLocation missing required artifactLocation field"
        )
    else:
        artifact_errors = validate_artifact_location(
            phys_loc["artifactLocation"], run_index, result_index, location_index
        )
        errors.extend(artifact_errors)

    if "region" in phys_loc:
        region_errors = validate_region(
            phys_loc["region"], run_index, result_index, location_index
        )
        errors.extend(region_errors)

    return errors


def validate_artifact_location(artifact_loc, run_index, result_index, location_index):
    """Validate artifact location."""
    errors = []

    if not isinstance(artifact_loc, dict):
        errors.append(
            f"runs[{run_index}].results[{result_index}].locations[{location_index}].physicalLocation.artifactLocation must be an object"
        )
        return errors

    if "uri" not in artifact_loc:
        errors.append(
            f"runs[{run_index}].results[{result_index}].locations[{location_index}].physicalLocation.artifactLocation missing required uri field"
        )

    return errors


def validate_region(region, run_index, result_index, location_index):
    """Validate region."""
    errors = []

    if not isinstance(region, dict):
        errors.append(
            f"runs[{run_index}].results[{result_index}].locations[{location_index}].physicalLocation.region must be an object"
        )
        return errors

    if "startLine" in region:
        start_line = region["startLine"]
        if not isinstance(start_line, int) or start_line < 1:
            errors.append(
                f"runs[{run_index}].results[{result_index}].locations[{location_index}].physicalLocation.region.startLine must be an integer >= 1"
            )

    if "startColumn" in region:
        start_col = region["startColumn"]
        if not isinstance(start_col, int) or start_col < 1:
            errors.append(
                f"runs[{run_index}].results[{result_index}].locations[{location_index}].physicalLocation.region.startColumn must be an integer >= 1"
            )

    return errors


def main():
    """Main validation function."""
    if len(sys.argv) != 2:
        print("Usage: python validate_sarif_strict.py <sarif_file>")
        sys.exit(1)

    sarif_file = sys.argv[1]

    if not Path(sarif_file).exists():
        print(f"SARIF file {sarif_file} not found")
        sys.exit(1)

    try:
        with open(sarif_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    errors = validate_github_sarif(data)

    if errors:
        print("SARIF validation failed:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("SARIF file is valid for GitHub Security tab")
        sys.exit(0)


if __name__ == "__main__":
    main()
