import json
import urllib3
import logging
from logging import Logger
from typing import Any


LOG: Logger = logging.getLogger(__name__)
ENDPOINT: str = "https://search.rcsb.org/rcsbsearch/v2/query"


def fetch(client: urllib3.PoolManager, query: dict[str, Any]) -> dict[str, Any]:
    """
    Searches the RCSB PDB database using the provided search query via the RCSB search API.

    Args:
        client (urllib3.PoolManager): The HTTP client to use for making the request.
        query (dict[str, dict|str]): The search query to send to the RCSB PDB API.
            For more details on how to structure the query, refer to the documentation at:
            https://search.rcsb.org

    Returns:
        dict[str, dict|str]: The search results returned by the RCSB PDB API.
    """
    LOG.info("Sending search query to RCSB Search API...")
    LOG.debug(f"Query payload: {json.dumps(query, indent=2)}")

    try:
        response = client.request(method="POST", url=ENDPOINT, json=query)

        if response.status == 200:
            LOG.info("Search query successful.")
            return json.loads(response.data.decode("utf8"))
        else:
            LOG.error(f"Failed to query RCSB search API: {response.status}")
            LOG.error(response.data.decode("utf8"))
            return dict()

    except Exception as e:
        LOG.exception("Exception occurred while querying RCSB Search API")
        LOG.error(str(e))
        return dict()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = fetch(
        client=urllib3.PoolManager(),
        query={
            "query": {"type": "terminal", "service": "text"},
            "return_type": "entry",
        },
    )
    print(result)
