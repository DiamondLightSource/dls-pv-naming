import argparse
import json

from pv_naming.fetch_info import fetch_information, fetch_value_rdb
from pv_naming.pv_format_check import pv_format_check, pv_format_report
from pv_naming.pv_database_check import (
    pv_database_check,
    pv_database_report,
    split_into_elements,
)


def device_check(device_name: str) -> str:
    """Runs format and database check on device name and returns a JSON formatted string"""
    # Initialize result dictionary
    # device holds device name, valid holds whether the name passes all checks
    # comments holds a list of strings which provide feedback
    result = {"device": device_name, "valid": False, "comments": []}

    # Collect all necessary information
    database_dict = fetch_information()

    if pv_format_check(device_name) is False:
        result["comments"] = [
            "Device does not match format:",
            *pv_format_report(device_name),
        ]
    elif pv_database_check(device_name, database_dict) == False:
        result["comments"] = [
            "Device matches format but not all elements could be found in the database:",
            *pv_database_report(device_name, database_dict),
        ]
    else:
        result["valid"] = True
        [domain, subdomain, techarea, component, _] = split_into_elements(device_name)
        result["comments"] = [
            f"Well done! {device_name} matches the formatting convention AND it is in the database! 🎉🎉"
        ]
        domainsearch = f"https://rdb.pri.diamond.ac.uk/php/epics/cs_epigetdomain.php?domainid={domain}"
        result["comments"].append(
            f"Domain: {domain} - {fetch_value_rdb(domainsearch, 'domainname')}"
        )
        if subdomain is not None:
            subdomainsearch = f"https://rdb.pri.diamond.ac.uk/php/epics/cs_epigetsubdomain.php?domainid={domain}&subdomainid={subdomain}"
            result["comments"].append(
                f"Subdomain: {subdomain} - {fetch_value_rdb(subdomainsearch, 'subdomainname')}"
            )
        techsearch = f"https://rdb.pri.diamond.ac.uk/php/epics/cs_epigettecharea.php?techareaid={techarea}"
        result["comments"].append(
            f"Technical Area: {techarea} - {fetch_value_rdb(techsearch, 'techareaname')}"
        )

        compsearch = f"https://rdb.pri.diamond.ac.uk/php/epics/cs_epigetcomponent.php?componentid={component}"
        result["comments"].append(
            f"Component: {component} - {fetch_value_rdb(compsearch, 'componentname')}"
        )

    return json.dumps(result)


def command_line_check():
    """Run a basic check on the PV provided, return with relevant info"""

    argument_parser = argparse.ArgumentParser(
        description="Check that a device name matches the Diamond format and that information about it is in the Diamond database"
    )

    argument_parser.add_argument("device", help="the device to check")

    args = argument_parser.parse_args()

    # Get the device
    device = args.device

    result = json.loads(device_check(device))

    for line in result["comments"]:
        print(line)
