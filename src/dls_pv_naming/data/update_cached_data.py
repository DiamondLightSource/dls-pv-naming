#!/usr/bin/env -S uv run --script
#
# /// script
# dependencies = [
#   "requests",
#   "dls_pv_naming",
# ]
# [tool.uv.sources]
# dls_pv_naming = { path = "../../../" }
# ///

# Script to download updated EPICS naming data from the RDB and store it in JSON files

import json
import os

import requests

from dls_pv_naming.fetch_from_rdb import RDB_API_ADDRESS

apis = [
    ("/cs_epigetdomain.php", "domains.json"),
    ("/cs_epigetsubdomain.php", "subdomains.json"),
    ("/cs_epigettecharea.php", "techarea.json"),
    ("/cs_epigetcomponent.php", "component.json"),
]

SCRIPT_DIR = os.path.dirname(__file__) + "/"


for api, file in apis:
    data = requests.get(f"{RDB_API_ADDRESS}{api}")
    data.raise_for_status()

    with open(SCRIPT_DIR + file, mode="w") as f:
        json.dump(data.json(), f)
        f.write("\n")  # Ensures file is newline-terminated to make pre-commit happy
