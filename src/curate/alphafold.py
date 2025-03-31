import json
import urllib3
import logging
from logging import Logger
from typing import Any

LOG: Logger = logging.getLogger(__name__)
ENDPOINT: str = "https://alphafold.ebi.ac.uk/api/prediction/{}"


def alphafold(client: urllib3.PoolManager, entries: set[str]) -> dict[str, Any]:
    """
    Queries the AlphaFold API for a set of UniProt accessions.

    Args:
        client (urllib3.PoolManager): HTTP client for making requests.
        entries (set[str]): Set of UniProt accession IDs.

    Returns:
        dict[str, Any]: Dictionary of AlphaFold predictions keyed by accession ID.
    """
    results: dict[str, Any] = dict()
    LOG.info(f"Fetching AlphaFold metadata for {len(entries)} UniProt accessions...")

    for entry in entries:
        try:
            response = client.request(
                method="GET",
                url=ENDPOINT.format(entry),
                headers={"Accept": "application/json"},
            )

            if response.status == 200:
                results[entry] = json.loads(response.data.decode("utf-8"))[0]
                LOG.info(f"Retrieved AlphaFold entry for {entry}")
            else:
                LOG.error(
                    f"Failed to fetch AlphaFold data for {entry} (status {response.status})"
                )
                LOG.debug(response.data.decode("utf-8"))

        except Exception as e:
            LOG.exception(f"Exception while fetching AlphaFold data for {entry}")
            LOG.error(str(e))

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = alphafold(client=urllib3.PoolManager(), entries={"P69905", "P68871", "P12345"})
    for accession, data in result.items():
        print(f"{accession}: {data['entryId']}")
