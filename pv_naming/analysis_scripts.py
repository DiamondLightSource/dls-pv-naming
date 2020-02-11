"""Big analysis scripts which can be expected to run for a reasonably long time.
"""

import json
import logging
from pathlib import Path

from pv_naming.analyse_file import record_file_report_many
from pv_naming.fetch_from_rdb import fetch_all_information
from pv_naming.find_files import (
    find_builder_ioc_filenames,
    find_latest_ioc_db_filenames,
)


def report_latest_ioc_dbs():
    """Produce a report for all of the latest IOC files and save it in scratch as a JSON file"""
    database_info = fetch_all_information()
    latest_ioc_dbs = find_latest_ioc_db_filenames()

    logging.info("Analysing files now...")

    reports = record_file_report_many(latest_ioc_dbs, database_info, verbose=False)

    with open("/scratch/ioc_reports.json", "w") as fp:
        json.dump(reports, fp, indent=2)


def report_builder_iocs(
    builder_directory: str, verbose: bool = False, format_only: bool = False
) -> dict:
    """Create a report from all the files in the specified builder directory"""
    database_info = fetch_all_information()
    builder_ioc_dbs = find_builder_ioc_filenames(builder_directory)

    reports = record_file_report_many(
        builder_ioc_dbs, database_info, verbose, format_only
    )

    return reports


def report_db(filename: str, verbose: bool, format_only: bool = False) -> dict:
    try:
        assert Path(filename).is_file()
    except AssertionError:
        print(f"Expected path to a valid .db file, got {filename}")
        raise ValueError("Please provide the path to a valid .db file")

    database_info = fetch_all_information()

    reports = record_file_report_many([filename], database_info, verbose, format_only)

    return reports


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    report_latest_ioc_dbs()
