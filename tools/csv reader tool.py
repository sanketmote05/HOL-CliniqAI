"""
csv reader tool.py

Description:
    Reads a patient CSV file and returns structured patient records for clinical analysis.
    Each row should contain: patient_id, name, age, gender, diagnosis, medications, lab_results.
"""

import csv
import json
import argparse
from pydantic import BaseModel, Field
from typing import Optional


class UserParameters(BaseModel):
    """
    Parameters used to configure a tool. This may include API keys,
    database connections, environment variables, etc.
    """
    pass  # This tool does not require user-specific parameters.


class ToolParameters(BaseModel):
    """
    Arguments of a tool call. These arguments are passed to this tool whenever
    an Agent calls this tool. The descriptions below are also provided to agents
    to help them make informed decisions of what to pass to the tool.
    """
    file_path: str = Field(
        description=(
            "Absolute or relative path to the patient CSV file to read. "
            "In Cloudera Agent Studio use the {Attachments} variable so the "
            "student can upload the file from the Test screen."
        )
    )
    max_rows: Optional[int] = Field(
        default=None,
        description="Maximum number of patient rows to return. Omit to return all rows."
    )


def run_tool(config: UserParameters, args: ToolParameters):
    patients = []
    try:
        with open(args.file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if args.max_rows is not None and i >= args.max_rows:
                    break
                patients.append(dict(row))
    except FileNotFoundError:
        return {
            "error": f"File not found: {args.file_path}",
            "hint": (
                "In Agent Studio, set this parameter to {Attachments} so the "
                "student uploads the CSV from the Test screen."
            )
        }
    except Exception as e:
        return {"error": str(e)}

    return {
        "total_patients": len(patients),
        "columns": list(patients[0].keys()) if patients else [],
        "patients": patients,
    }


OUTPUT_KEY = "tool_output"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-params", required=True)
    parser.add_argument("--tool-params", required=True)
    cli_args = parser.parse_args()
    config = UserParameters(**json.loads(cli_args.user_params))
    params = ToolParameters(**json.loads(cli_args.tool_params))
    output = run_tool(config, params)
    print(OUTPUT_KEY, json.dumps(output, indent=2))
