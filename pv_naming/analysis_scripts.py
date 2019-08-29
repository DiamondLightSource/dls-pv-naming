"""Big analysis scripts which can be expected to run for a reasonably long time.
"""

import json

from analyse_file import record_file_report_many
from fetch_info import fetch_information
from find_files import find_latest_ioc_db_filenames


def report_latest_ioc_dbs():
    """Produce a report for all of the latest IOC files and save it in scratch as a JSON file"""
    database_info = fetch_information()
    latest_ioc_dbs = find_latest_ioc_db_filenames()

    reports = record_file_report_many(latest_ioc_dbs, database_info)

    with open("/scratch/ioc_reports.json", "w") as fp:
        json.dump(reports, fp, indent=2)


if __name__ == "__main__":
    report_latest_ioc_dbs()
