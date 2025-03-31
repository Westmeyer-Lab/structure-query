import os
import logging
import urllib3
from Bio.PDB import PDBList, alphafold_db
from logging import Logger
from typing import Literal, Any


LOG: Logger = logging.getLogger(__name__)
ENDPOINTS: dict[str, str] = {
    "memprotmd": "https://memprotmd.bioch.ox.ac.uk/data/memprotmd/simulations/{}/files/structures/at.pdb",
    "pdbtm": "https://pdbtm.unitmp.org/api/v1/entry/{}.trpdb",
    "opm": "https://biomembhub.org/shared/opm-assets/pdb/{}.pdb",
}


def structure(
    client: urllib3.PoolManager,
    method: Literal["rcsb", "alphafold", "memprotmd", "pdbtm", "opm"],
    entries: list[Any],
    outdir: str,
) -> None:
    """
    Downloads structure files from various sources based on the specified method.

    Args:
        client (urllib3.PoolManager): HTTP client for external requests.
        method (str): One of 'rcsb', 'alphafold', 'memprotmd', 'pdbtm', or 'opm'.
        entries (list[Any]): List of structure identifiers to download.
        outdir (str): Directory to save downloaded files.
    """
    os.makedirs(outdir, exist_ok=True)
    LOG.info(
        f"Downloading {len(entries)} structures using '{method}' method to '{outdir}'..."
    )

    match method:
        case "rcsb":
            pdbl = PDBList(verbose=False)
            pdbl.download_pdb_files(pdb_codes=entries, pdir=outdir, file_format="mmCif")

        case "alphafold":
            for entry in entries:
                alphafold_db.download_cif_for(entry, outdir)

        case "memprotmd" | "pdbtm" | "opm":
            for entry in entries:
                filename = os.path.join(outdir, f"{entry[:4]}.pdb")
                if os.path.exists(filename):
                    LOG.info(f"{filename} already exists, skipping.")
                    continue

                try:
                    response = client.request(
                        method="GET", url=ENDPOINTS[method].format(entry)
                    )
                    if response.status == 200:
                        with open(filename, "w", encoding="utf-8") as file:
                            file.write(response.data.decode("utf-8"))
                        LOG.info(f"Downloaded: {filename}")
                    else:
                        LOG.error(
                            f"Failed to download {method} structure for {entry}: {response.status}"
                        )
                        LOG.debug(response.data.decode("utf-8"))

                except Exception as e:
                    LOG.exception(f"Exception during {method} download for {entry}")
                    LOG.error(str(e))

        case _:
            LOG.error(f"Unknown structure method: '{method}'")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    structure(
        client=urllib3.PoolManager(),
        method="rcsb",
        entries=["1cbs", "1ubq"],
        outdir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "test"),
    )
