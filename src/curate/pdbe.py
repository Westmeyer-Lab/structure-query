import json
import urllib3
import logging
from logging import Logger
from typing import Any


LOG: Logger = logging.getLogger(__name__)
ENDPOINTS: dict[str, str] = {
    "summary": "https://www.ebi.ac.uk/pdbe/api/pdb/entry/summary/{}",
    "residues": "https://www.ebi.ac.uk/pdbe/api/pdb/entry/residue_listing/{}",
    "coverage": "https://www.ebi.ac.uk/pdbe/api/pdb/entry/polymer_coverage/{}",
    "structure": "https://www.ebi.ac.uk/pdbe/api/pdb/entry/secondary_structure/{}",
}


def pdbe(
    client: urllib3.PoolManager, entries: set[str], features: list[str]
) -> dict[str, dict[str, Any]]:
    """
    Fetches selected PDBe data features for a list of PDB entry IDs.

    Args:
        client (urllib3.PoolManager): HTTP client for making requests.
        entries (set[str]): Set of PDB entry IDs.
        features (list[str]): Subset of ["residues", "coverage", "structure"] to fetch.

    Returns:
        dict[str, dict[str, Any]]: Dict of {feature -> {entry -> data}}.
    """
    result = {feature: dict() for feature in features}

    for entry in entries:
        for feature in features:
            if feature not in ENDPOINTS:
                LOG.warning(f"Unsupported PDBe feature: {feature}")
                continue

            try:
                response = client.request(
                    method="GET",
                    url=ENDPOINTS[feature].format(entry),
                    headers={"Accept": "application/json"},
                )
                if response.status == 200:
                    raw = json.loads(response.data.decode("utf-8"))
                    if entry in raw:
                        result[feature][entry] = raw[entry]
                        LOG.debug(f"Fetched {feature} for {entry}")
                    else:
                        LOG.warning(f"No data for {feature} in response for {entry}")
                else:
                    LOG.error(
                        f"Failed to fetch {feature} for {entry}: {response.status}"
                    )
                    LOG.debug(response.data.decode("utf-8"))

            except Exception as e:
                LOG.exception(f"Exception during {feature} fetch for {entry}")
                LOG.error(str(e))

    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    entries = {"1cbs", "1ubq"}
    features = ["summary"]
    client = urllib3.PoolManager()
    data = pdbe(client, entries, features)
    for feature, entries in data.items():
        print(f"Feature: {feature}")
        for entry, details in entries.items():
            print(f"{entry}: {details[-1]['title']}")
