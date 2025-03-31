import json
import logging
import urllib3
from logging import Logger
from typing import Any

LOG: Logger = logging.getLogger(__name__)
ENDPOINT: str = "https://memprotmd.bioch.ox.ac.uk/api/references/PDB/{}"


def memprotmd(client: urllib3.PoolManager, entries: set[str]) -> dict[str, Any]:
    """
    Fetches simulation metadata for entries from the MemProtMD API.

    Args:
        client (urllib3.PoolManager): HTTP client.
        entries (set[str]): Set of PDB entry IDs.

    Returns:
        dict[str, Any]: Simulation metadata keyed by PDB ID.
    """
    results: dict[str, Any] = dict()
    LOG.info(f"Fetching MemProtMD data for {len(entries)} entries...")

    for entry in entries:
        try:
            response = client.request(
                method="POST",
                url=ENDPOINT.format(entry),
                headers={"Accept": "application/json"},
            )

            if response.status != 200:
                LOG.error(f"Failed MemProtMD query for {entry}: {response.status}")
                LOG.debug(json.dumps(response.data.decode("utf-8"), indent=2))
                continue

            output = json.loads(response.data.decode("utf-8"))
            if not output:
                LOG.error(f"No MemProtMD data found for {entry}")
                continue

            results[entry] = output
            LOG.info(f"Retrieved MemProtMD simulations for {entry}")

        except Exception as e:
            LOG.exception(f"Exception while querying MemProtMD for {entry}")
            LOG.error(e)

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = memprotmd(urllib3.PoolManager(), {"6kzo"})
    print(json.dumps(result, indent=2))
