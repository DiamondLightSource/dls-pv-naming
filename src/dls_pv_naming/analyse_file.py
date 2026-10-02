import copy
import logging
import re

from dls_pv_naming.pv_database_check import (
    empty_database,
    pv_database_check,
    pv_database_report,
)
from dls_pv_naming.pv_format_check import (
    get_device_name,
    pv_format_check,
    pv_format_report,
)

"""Regex for getting what is in between speech marks following the record
keyword at the start of a line
i.e record(ai, "MYPV") -> 'MYPV'
but OUTP("OTHERPV") -> None

Not defined as a verbose regex due to its use in a multiline check but not as a
multiline regex. Could not get this to work putting the flag in the regex
definition.
"""
RECORD_REGEX = '(?<=^record)(?:.*)(?<=")(.*)"'


def record_text_report(
    record_text: str, database_info: dict = empty_database, format_only: bool = False
) -> dict:
    """
    Analyse a .db records file to find the records, extract a list of unique device
    names and then check them against the specified Diamond format and the database
    to produce a useful report.

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

    :param record_text: String of file to analyse (will be analysed directly, not read
        from this address)
    :param database_info: Dictionary containing database information to use when
        analysing
    """
    record_pvs = get_record_pvs(record_text)
    logging.debug(f"Found {len(record_pvs)} pvs")

    unique_record_pvs = set(record_pvs)
    logging.debug(f"Found {len(unique_record_pvs)} unique pvs")

    # Collect a dictionary of device occurrences which splits on a colon to separate
    # device names
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
    # Do not perform this check if format_only is set to True
    if format_only is not True:
        bad_database_device_names = [
            d
            for d in good_format_device_names
            if not pv_database_check(d, database_info)
        ]
    else:
        bad_database_device_names = []

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


def get_record_pvs(record_text: str) -> list[str]:
    """Read record_file and return a list of all PVS which match a more general PV
    format"""
    return list(re.findall(RECORD_REGEX, record_text, flags=re.MULTILINE))


def record_file_report(
    filename: str, database_info: dict, format_only: bool = False
) -> dict:
    """Read the contents of the file, fetch the information from the database and return
    a report"""
    with open(filename) as fp:
        file_text = fp.read()

    return record_text_report(file_text, database_info, format_only)


def record_file_report_many(
    filename_list: list[str],
    database_info: dict,
    verbose: bool = False,
    format_only: bool = False,
) -> dict:
    """Produce a report for each of the files requested"""
    initial_reports = {
        filename: record_file_report(filename, database_info, format_only)
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
