"""
fda drug api tool.py

Description:
    Queries the FDA OpenFDA Drug Adverse Events API (api.fda.gov/drug/event.json)
    for reported adverse events associated with a given drug name.
    Returns a summary of the top adverse reactions and their reported frequencies.
    No API key required — the FDA OpenFDA API is free and publicly available.
"""

import json
import argparse
import requests
from pydantic import BaseModel, Field
from typing import Optional


class UserParameters(BaseModel):
    """
    Parameters used to configure a tool. This may include API keys,
    database connections, environment variables, etc.
    """
    pass  # OpenFDA API is free and requires no API key.


class ToolParameters(BaseModel):
    """
    Arguments of a tool call. These arguments are passed to this tool whenever
    an Agent calls this tool. The descriptions below are also provided to agents
    to help them make informed decisions of what to pass to the tool.
    """
    drug_name: str = Field(
        description=(
            "Name of the drug to look up. Can be a generic name (e.g. 'metformin') "
            "or brand name (e.g. 'Glucophage'). Separate multiple drugs with a comma."
        )
    )
    limit: Optional[int] = Field(
        default=10,
        description="Maximum number of adverse event reaction terms to return (default 10, max 100)."
    )


FDA_BASE_URL = "https://api.fda.gov/drug/event.json"


def query_fda(drug_name: str, limit: int):
    """
    Query the OpenFDA drug adverse event endpoint.
    Uses count endpoint to get top reaction terms by frequency.
    """
    params = {
        "search": f'patient.drug.medicinalproduct:"{drug_name}"',
        "count": "patient.reaction.reactionmeddrapt.exact",
        "limit": min(limit, 100),
    }
    try:
        resp = requests.get(FDA_BASE_URL, params=params, timeout=15)
        if resp.status_code == 404:
            return None, f"No adverse event data found for drug: {drug_name}"
        resp.raise_for_status()
        return resp.json(), None
    except requests.exceptions.Timeout:
        return None, "FDA API request timed out (15 s). Try again."
    except requests.exceptions.HTTPError as e:
        return None, f"FDA API HTTP error {resp.status_code}: {resp.text[:300]}"
    except Exception as e:
        return None, str(e)


def run_tool(config: UserParameters, args: ToolParameters):
    drug_name = args.drug_name.strip()
    limit = args.limit or 10

    data, err = query_fda(drug_name, limit)
    if err:
        return {
            "drug_name": drug_name,
            "error": err,
            "source": "FDA OpenFDA Drug Adverse Event API (api.fda.gov/drug/event.json)",
        }

    results = data.get("results", [])
    if not results:
        return {
            "drug_name": drug_name,
            "adverse_reactions": [],
            "total_reactions_found": 0,
            "message": "No adverse reaction data returned for this drug.",
            "source": "FDA OpenFDA Drug Adverse Event API",
        }

    top_reactions = [
        {"reaction": r["term"], "reported_cases": r["count"]}
        for r in results
    ]

    return {
        "drug_name": drug_name,
        "top_adverse_reactions": top_reactions,
        "total_reactions_in_response": len(top_reactions),
        "note": (
            "Reaction counts reflect the number of adverse event reports mentioning "
            "this drug and reaction term in the FDA FAERS database. They are not "
            "clinical incidence rates."
        ),
        "source": "FDA OpenFDA Drug Adverse Event API (api.fda.gov/drug/event.json)",
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
