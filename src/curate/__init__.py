import os
import logging
from typing import Any

from curate.rcsb import rcsb
from curate.pdbe import pdbe
from curate.memprotmd import memprotmd
from curate.pdbtm import pdbtm
from curate.opm import opm
from curate.structure import structure


LOG = logging.getLogger(__name__)


def curate(client, entries: set[str], options: dict[str, Any]) -> dict[str, Any]:
    """
    Curates biological structure data in a staged pipeline:
      1. Queries RCSB for entry data.
      2. Downloads experimental PDB structure files.
      3. Queries PDBe-KB for entry data.
      4. Fetches membrane annotation data from MemProtMD, PDBTM, or OPM and downloads simulated structures.

    Args:
        client (urllib3.PoolManager): HTTP client used to execute the data queries.
        entries (set[str]): Set of unique PDB identifiers to be curated.

    Returns:
        dict[str, Any]: Curated data including RCSB, PDBe-KB, membrane data, as well as the final entry list.
    """
    data: dict[str, Any] = {"entries": [], "rcsb": {}, "pdbe": {}, "membrane": {}}
    LOG.info(f"Starting data curation process for {len(entries)} entries...")
    LOG.debug(f"Initial entries: {entries}")

    # 1. RCSB entry data
    result = rcsb(client, entries, options["rcsb"])
    data["rcsb"] = {entry["entry"]["id"].lower(): entry for entry in result}
    entries = set(data["rcsb"].keys())
    LOG.info(f"RCSB: {len(entries)} entries retained")
    LOG.debug(f"Remaining entries: {entries}")

    # 2. PDB experimental structure
    structure(client, "rcsb", list(entries), options["pdb"])
    entries = {
        file.removesuffix(".cif").lower()
        for file in os.listdir(options["pdb"])
        if file.endswith(".cif")
    }
    LOG.info(f"Structure: {len(entries)} entries retained")
    LOG.debug(f"Remaining entries: {entries}")

    # 3. PDBe-KB entry data
    data["pdbe"] = pdbe(client, entries, options["pdbe"])
    entries = set.intersection(
        *(set(data["pdbe"][feature].keys()) for feature in options["pdbe"])
    )
    LOG.info(f"PDBe-KB: {len(entries)} entries retained")
    LOG.debug(f"Remaining entries: {entries}")

    # 4. Membrane data preference order: MemProtMD → PDBTM → OPM
    processed = set()
    for label, fetch in {"pdbtm": pdbtm, "opm": opm, "memprotmd": memprotmd}.items():
        entries -= processed
        if not entries:
            break

        result = fetch(client, entries)
        data["membrane"].update(
            {entry: value | {"_source": label} for entry, value in result.items()}
        )

        match label:
            case "pdbtm" | "opm":
                structure(client, label, list(result.keys()), options["tm"])
            case "memprotmd":
                structure(
                    client,
                    label,
                    [
                        entry["simulations"][-1]
                        for entry in result.values()
                        if "simulations" in entry and entry["simulations"]
                    ],
                    options["tm"],
                )

        processed = set(result.keys()) & {
            file.removesuffix(".pdb").lower()
            for file in os.listdir(options["tm"])
            if file.endswith(".pdb")
        }
        data["entries"] += list(processed)

        LOG.info(f"{label.upper()}: {len(processed)} entries processed")
        LOG.debug(f"Processed entries: {processed}")

    # Final retained set
    LOG.info(f"Final curated set: {len(data["entries"])} entries")
    LOG.debug(f"Final entries: {data["entries"]}")

    return data
