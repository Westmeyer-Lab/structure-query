import json
import logging
from logging import Logger
import urllib3
from typing import Any


LOG: Logger = logging.getLogger(__name__)
ENDPOINT: str = "https://data.rcsb.org/graphql"


def rcsb(
    client: urllib3.PoolManager, entries: set[str], query: str
) -> list[dict[str, Any]]:
    """
    Fetches detailed RCSB data for a list of PDB IDs via GraphQL API.

    Args:
        client (urllib3.PoolManager): The HTTP client to use for making the request.
        entries (set[str]): Set of PDB entry IDs.
        query (str): GraphQL query string to execute.

    Returns:
        list[dict[str, Any]]: List of metadata entries corresponding to input PDB IDs.
    """
    LOG.info(f"Fetching RCSB metadata for {len(entries)} entries...")
    LOG.debug(f"Query payload: {json.dumps(query, indent=2)}")

    payload = {"query": query, "variables": {"ids": list(entries)}}

    try:
        response = client.request(method="POST", url=ENDPOINT, json=payload)

        if response.status == 200:
            LOG.info("Data query successful.")
            result = json.loads(response.data.decode("utf-8"))
            return result.get("data", {}).get("entries", [])
        else:
            LOG.error(f"Failed to query RCSB GraphQL API: {response.status}")
            LOG.error(response.data.decode("utf-8"))
            return []

    except Exception as e:
        LOG.exception("Exception occurred while querying RCSB GraphQL API")
        LOG.error(str(e))
        return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = rcsb(
        client=urllib3.PoolManager(),
        entries={"1cbs", "1crn", "1ubq"},
        query="""
            query($ids: [String!]!) {
                entries(entry_ids: $ids) {
                    rcsb_id
                }
            }
        """,
    )
    for entry in result:
        print(entry["rcsb_id"])
