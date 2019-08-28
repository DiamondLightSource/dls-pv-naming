import glob
import logging
from pathlib import Path
from typing import List

from natsort import natsorted


def find_latest_ioc_db_filenames() -> List[str]:
    """Get the latest *expanded.db files from iocs and build up a counter from them for unique PV elements"""
    # Builder directories
    top_level_dirs = [
        dir for dir in Path("/dls_sw/prod/R3.14.12.3/ioc").iterdir() if dir.is_dir()
    ] + [dir for dir in Path("/dls_sw/prod/R3.14.12.7/ioc").iterdir() if dir.is_dir()]
    logging.debug(f"Found {len(top_level_dirs)} directories")

    ioc_dirs = [
        ioc_dir
        for directory in top_level_dirs
        for ioc_dir in Path(directory).iterdir()
        if ioc_dir.is_dir()
    ]
    logging.debug(f"Found {len(ioc_dirs)} ioc directories")

    ioc_latest_version = [
        natsorted([ioc_version for ioc_version in Path(directory).iterdir()])[-1]
        for directory in ioc_dirs
        if [directory for directory in Path(directory).iterdir()]
    ]
    expanded_dbs_list = [glob.glob(str(directory) + "/db/*.db") for directory in ioc_latest_version]
    expanded_db_files = [
        sorted(db_list, reverse=True)[0] for db_list in expanded_dbs_list if db_list
    ]
    logging.debug(f"Found {len(expanded_db_files)} database files for analysis")
    logging.debug(f"Found {len(set(expanded_db_files))} database files for analysis")

    return expanded_db_files


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    print(find_latest_ioc_db_filenames())
