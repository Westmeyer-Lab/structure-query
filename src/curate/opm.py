import json
import logging
import urllib3
from logging import Logger
from typing import Any

LOG: Logger = logging.getLogger(__name__)
ENDPOINT: str = "https://opm-back.cc.lehigh.edu/opm-backend/primary_structures/pdbid/{}"


def opm(client: urllib3.PoolManager, entries: set[str]) -> dict[str, Any]:
    """
    Fetches membrane thickness data from the OPM API.

    Args:
        client (urllib3.PoolManager): HTTP client.
        entries (set[str]): Set of PDB entry IDs.

    Returns:
        dict[str, Any]: OPM membrane data keyed by PDB ID.
    """
    results: dict[str, Any] = dict()
    LOG.info(f"Fetching OPM data for {len(entries)} entries...")

    for entry in entries:
        try:
            response = client.request(
                method="GET",
                url=ENDPOINT.format(entry),
                headers={"Accept": "application/json"},
            )

            if response.status == 200:
                results[entry] = json.loads(response.data.decode("utf-8"))
                LOG.info(f"Retrieved OPM data for {entry}")
            else:
                LOG.error(f"Failed OPM query for {entry}: {response.status}")
                LOG.debug(json.dumps(response.data.decode("utf-8"), indent=2))

        except Exception as e:
            LOG.exception(f"Exception while querying OPM for {entry}")
            LOG.error(e)

    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = opm(urllib3.PoolManager(), {"6kzo"})
    print(json.dumps(result, indent=2))