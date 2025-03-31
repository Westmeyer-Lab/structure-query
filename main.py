import os
import sys
import json
import urllib3
import logging
from logging import Logger
from typing import Any

CONFIG_FILE: str = "config.json"
CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CLIENT: urllib3.PoolManager = urllib3.PoolManager()

logging.basicConfig(level=logging.INFO)
LOG: Logger = logging.getLogger("main")

scripts = os.path.join(CURRENT_DIR, "src/")
if scripts not in sys.path:
    sys.path.insert(0, scripts)
    LOG.debug(f"Added scripts directory to path: {scripts}")

from search import search
from curate import curate

def setup(config: str) -> dict[str, Any]:
    """
    Loads configuration, adjusts sys.path, creates output directories,
    and loads any file-based entries in the data section.

    Args:
        config (str): Path to the JSON configuration file.

    Returns:
        dict[str, Any]: A dictionary with parsed 'search' and 'data' sections.
    """
    if not os.path.exists(config):
        raise FileNotFoundError(f"Config file '{config}' not found.")
    with open(config, "r", encoding="utf-8") as file:
        settings = json.load(file)

    # Prepare output directory
    outdir = os.path.join(CURRENT_DIR, settings.get("output", "results/"))
    os.makedirs(outdir, exist_ok=True)
    LOG.debug(f"Ensured output directory exists: {outdir}")

    # Adjust and create directories for data
    if "pdb" in settings.get("data", {}):
        settings["data"]["pdb"] = os.path.join(CURRENT_DIR, settings["data"]["pdb"])
        os.makedirs(settings["data"]["pdb"], exist_ok=True)
        LOG.debug(f"Ensured PDB directory exists: {settings['data']['pdb']}")
    if "tm" in settings.get("data", {}):
        settings["data"]["tm"] = os.path.join(CURRENT_DIR, settings["data"]["tm"])
        os.makedirs(settings["data"]["tm"], exist_ok=True)
        LOG.debug(f"Ensured TM directory exists: {settings['data']['tm']}")

    # Load external query file if specified
    query = settings.get("data", {}).get("rcsb", None)
    if query:
        path = os.path.join(CURRENT_DIR, query)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Query file not found: {path}")
        with open(path, "r", encoding="utf-8") as file:
            settings["data"]["rcsb"] = file.read()
            LOG.info(f"Loaded RCSB query from file: {query}")

    return {
        "search": settings.get("search", {}),
        "data": settings.get("data", {}),
        "output": outdir,
    }


if __name__ == "__main__":
    try:
        LOG.info("Setting up...")
        config = setup(os.path.join(CURRENT_DIR, CONFIG_FILE))

        LOG.info("Running search...")
        result = search(client=DEFAULT_CLIENT, config=config["search"])
        LOG.info(f"Search returned {len(result)} entries.")

        LOG.info("Curating data...")
        curated = curate(client=DEFAULT_CLIENT, entries=result, options=config["data"])
        LOG.info(f"Curation complete. Final count: {len(curated['entries'])} entries.")

        # Save curated data to output directory
        output_file = os.path.join(config["output"], "data.json")
        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(curated, file, indent=2)
 
    except Exception:
        LOG.exception("Pipeline failed.")
        sys.exit(1)
