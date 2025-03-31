import urllib3
from typing import Any

from .query import parse, transform
from .request import fetch

def search(client: urllib3.PoolManager, config: dict[str, Any]) -> set[str]:
    """
    Executes an RCSB search query based on the configuration provided in a JSON file.

    Args:
        client (urllib3.PoolManager): HTTP client used to execute the search query.
        config (dict[str, Any]): Configuration containing the search parameters and expression.

    Returns:
        set[str]: Set of unique PDB identifiers extracted from the search results.
    """
    # Extract the query parameters and expression
    parameters = {
        item["label"]: item["parameters"]
        for item in config["query"]
    }
    expression = config["expression"]

    # Generate the query
    query = {
        "query": transform(parse(expression), parameters),
        "request_options": {
            "results_verbosity": "compact",
            "return_all_hits": True,
            "group_by": {
                "aggregation_method": "matching_uniprot_accession",
                "ranking_criteria_type": {
                    "sort_by": "coverage"
                },
            },
            "group_by_return_type": "representatives"
        },
        "return_type": "polymer_entity"
    }

    # Execute the search
    output = fetch(client, query)
    result = {item[:4] for item in output["result_set"]}

    return result
