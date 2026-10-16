#!/usr/bin/env -S uv run --script
#
# /// script
# dependencies = [
#   "dls_pv_naming",
# ]
# [tool.uv.sources]
# dls_pv_naming = { path = "../../../" }
# ///

# Script to download updated EPICS naming data from the RDB and store it in JSON files

import json
import os

from dls_pv_naming.fetch_from_rdb import URL_CACHE_MAP, fetch_from_rdb

SCRIPT_DIR = os.path.dirname(__file__) + "/"


for api, file in URL_CACHE_MAP.items():
    data = fetch_from_rdb(api)

    with open(SCRIPT_DIR + file, mode="w") as f:
        json.dump(data, f)
        f.write("\n")  # Ensures file is newline-terminated to make pre-commit happy
