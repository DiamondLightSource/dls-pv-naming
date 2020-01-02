import copy
import logging
import re
from typing import List

from pv_naming.fetch_info import fetch_information
from pv_naming.pv_database_check import (
    empty_database,
    pv_database_check,
    pv_database_report,
)
from pv_naming.pv_format_check import get_device_name, pv_format_check, pv_format_report

record_regex = '(?<=^record)(?:.*)(?<=")(.*)"'


def record_text_report(record_text: str, database_info: dict = empty_database) -> dict:
    """
    Analyse a .db records file to find the records, extract a list of unique device names and then
    check them against the specified Diamond format and the database to produce a useful report.

    Ouptut expected to look like this for an example *bad_device_name*:

    {
        bad_device_name: {
            occurences: [
                list of subdevice names found with this device name
            ],
            errors: [
                list of errors associated with the bad device name
            ],
            suggestions: [
                lsit of spelling suggestions for device name
            ]
        }
    }

    :param record_text: String of file to analyse (will be analysed directly, not read from this address)
    :param database_info: Dictionary containing database information to use when analysing
    """
    record_pvs = get_record_pvs(record_text)
    logging.debug(f"Found {len(record_pvs)} pvs")

    unique_record_pvs = set(record_pvs)
    logging.debug(f"Found {len(unique_record_pvs)} unique pvs")

    # Collect a dictionary of device occurrences which splits on a colon to separate device names
    device_occurences: dict = {}
    for pv in unique_record_pvs:
        device_name = pv.split(":")[0] if "::" not in pv else pv
        if device_name not in device_occurences:
            device_occurences[device_name] = [pv]
        else:
            device_occurences[device_name].append(pv)
    logging.debug(f"Found {len(device_occurences)} device names")

    # Check basic pv formatting
    good_format_device_names = [d for d in device_occurences if pv_format_check(d)]
    bad_format_device_names = [d for d in device_occurences if not pv_format_check(d)]

    # Produce report for PVs which failed basic formatting tests
    format_report = {
        device: {
            "errors": pv_format_report(device),
            "occurences": device_occurences[device],
        }
        for device in bad_format_device_names
    }

    # Clear the report of duplicated near misses on missing colons
    curated_format_report: dict = {}
    for device in format_report:
        if get_device_name(device) not in curated_format_report:
            curated_format_report[get_device_name(device)] = {
                "errors": copy.deepcopy(format_report[device]["errors"]),
                "occurences": copy.deepcopy(format_report[device]["occurences"]),
            }
        else:
            # Maintain set of unique errors / warnings per device name
            try:
                curated_format_report[get_device_name(device)]["errors"] = list(
                    set(
                        curated_format_report[get_device_name(device)]["errors"]
                        + format_report[device]["errors"]
                    )
                )

                # Occurences should be unique anyway
                curated_format_report[get_device_name(device)]["occurences"].append(
                    *format_report[device]["occurences"]
                )
            except TypeError:
                logging.error(f"Device: {device}")
                existing_errors = format_report[device]["errors"]
                logging.error(f"Errors: {existing_errors}")
                new_errors = curated_format_report[get_device_name(device)]["errors"]
                logging.error(f"Existing errors: {new_errors}")
                raise

    # Find PVs which passed the formatting tests but cannot be located in the database
    bad_database_device_names = [
        d for d in good_format_device_names if not pv_database_check(d, database_info)
    ]

    # Produce report for PVs which failed database check
    database_report = {
        device: {
            "errors": pv_database_report(device, database_info),
            "occurences": device_occurences[device],
        }
        for device in bad_database_device_names
    }

    output_report = {}

    if format_report:
        output_report.update({"Format errors": curated_format_report})
    if database_report:
        output_report.update({"Database errors": database_report})

    return output_report


def get_record_pvs(record_text: str) -> List[str]:
    """Read record_file and return a list of all PVS which match a more general PV format"""
    return [pv for pv in re.findall(record_regex, record_text, flags=re.MULTILINE)]


def record_file_report(filename: str, database_info: dict) -> dict:
    """Read the contents of the file, fetch the information from the database and return a report"""
    with open(filename, "r") as fp:
        file_text = fp.read()

    return record_text_report(file_text, database_info)


def record_file_report_many(
    filename_list: List[str], database_info: dict, verbose: bool = False
) -> dict:
    """Produce a report for each of the files requested"""
    initial_reports = {
        filename: record_file_report(filename, database_info)
        for filename in filename_list
    }

    # Only return names of files which returned a report
    report = {
        filename: report for filename, report in initial_reports.items() if report
    }

    # Summarise errors
    if verbose is False:
        for filename in report:
            for error_type in report[filename]:
                for device in report[filename][error_type]:
                    if len(report[filename][error_type][device]["occurences"]) > 3:
                        # Add elipses after the third value
                        report[filename][error_type][device]["occurences"] = report[
                            filename
                        ][error_type][device]["occurences"][:3] + ["..."]

    return report


if __name__ == "__main__":

    database_info = fetch_information()

    record_text_report(
        """record(ai, "BL6I-EA-IOC-01")
record(ai, "ME16I-EA-IOC-01"
record(ai, "BL02I-EA-IOC-04SR_5_Status")
record(ai, "BL02I-EA-IOC-04SR_deadIfZero")
record(ai, "BL02I-EA-IOC-04:CORRECT:FORMAT")
record(ai, "BL14I-VA-VLVCC-03B")
record(ai, "BL14I-VA-VLVCC-03B:Some:Other:Things")
record(ai, "BL14I-VA-VLCCC-03:ALSO:CORRECT")
record(ai, "BL16I-EA-K65-01Int")
record(ai, "BL16I-EA-K65-01KeyDispNext")
record(ai, "BL16I-EA-K65-01KeyLeftArrow")
record(ai, "BL02I-EA-IOC-04SR_7_Name")
record(ai, "BL02I-EA-IOC-04::SR_7_Name")  """,
        database_info,
    )

    print(
        record_file_report(
            "/dls_sw/prod/R3.14.12.7/ioc/BL18B/BL18B-EA-IOC-14/2-0/db/BL18B-EA-IOC-14_expanded.db",
            database_info,
        )
    )

    print(
        record_file_report(
            "/dls_sw/prod/R3.14.12.3/ioc/BL14I/BL14I-VA-IOC-03/2-0/db/BL14I-VA-IOC-03_expanded.db",
            database_info,
        )
    )

    # print(
    #     record_file_report_many(
    #         [
    #             "/dls_sw/prod/R3.14.12.7/ioc/BL18B/BL18B-EA-IOC-14/2-0/db/BL18B-EA-IOC-14_expanded.db",
    #             "/dls_sw/prod/R3.14.12.7/ioc/BL18B/BL18B-EA-IOC-14/2-0/db/BL18B-EA-IOC-14_expanded.db",
    #             "/dls_sw/prod/R3.14.12.7/ioc/BL18B/BL18B-EA-IOC-14/2-0/db/BL18B-EA-IOC-14_expanded.db",
    #         ],
    #         database_info,
    #     )
    # )
