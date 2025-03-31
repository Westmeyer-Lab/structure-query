import os
import json
import logging
from logging import Logger
from typing import Any, cast

from SPARQLWrapper import SPARQLWrapper, JSON

LOG: Logger = logging.getLogger(__name__)
ENDPOINT: str = "https://sparql.uniprot.org/sparql"


def uniprot(query: str, entries: set[str]) -> list[dict[str, Any]]:
    """
    Fetches UniProt data using the provided SPARQL query and optional entry substitution.

    Args:
        query (str): The SPARQL query to execute, with `$entries` placeholder.
        entries (set[str]): Set of PDB entry IDs for substitution.

    Returns:
        list[dict[str, Any]]: List of results (SPARQL bindings).
    """
    query = query.replace("$entries", " ".join(f"('{entry}')" for entry in entries))
    client = SPARQLWrapper(ENDPOINT)

    LOG.info(f"Fetching UNIPROT SPARQL data for {len(entries)} entries...")
    LOG.debug(f"Query payload:\n{query.strip()}")

    client.setQuery(query)
    client.setReturnFormat(JSON)

    try:
        LOG.info("Data query successful.")
        response = cast(dict, client.query().convert())
        return response.get("results", {}).get("bindings", [])

    except Exception as e:
        LOG.exception("Failed to fetch data from UniProt SPARQL API.")
        LOG.error(str(e))
        return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    query = """
        PREFIX up: <http://purl.uniprot.org/core/> 
        SELECT ?protein
        WHERE {
            ?protein a up:Protein .
        }
        LIMIT 3
    """
    result = uniprot(query=query, entries=set())
    print(json.dumps(result, indent=2))
