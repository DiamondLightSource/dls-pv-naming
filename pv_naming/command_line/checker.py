from pv_naming.fetch_info import fetch_information, fetch_value_rdb
from pv_naming.pv_format_check import pv_format_check, pv_format_report
from pv_naming.pv_database_check import pv_database_check, pv_database_report, split_into_elements

import argparse

def command_line_check():
    """Run a basic check on the PV provided, return with relevant info"""

    argument_parser = argparse.ArgumentParser(
        description="Check that a device name matches the Diamond format and that information about it is in the Diamond database"
    )

    argument_parser.add_argument("device", help="the device to check")

    args = argument_parser.parse_args()

    # Get the device
    device = args.device

    if pv_format_check(device) == False:
        print("Device does not match format:")
        for line in pv_format_report(device):
            print(line)
        return
    
    database_dict = fetch_information()
    if pv_database_check(device, database_dict) == False:
        print("Device matches format but not all elements could be found in the database:")
        for line in pv_database_report(device, database_dict):
            print(line)
        return

    [domain, subdomain, techarea, component, _] = split_into_elements(device)
    print(f"Well done! {device} matches the formatting convention AND it is in the database! 🎉🎉")

    domainsearch= f"https://rdb.pri.diamond.ac.uk/php/epics/cs_epigetdomain.php?domainid={domain}"
    print(f"Domain: {domain} - {fetch_value_rdb(domainsearch, 'domainname')}")

    if subdomain is not None:
        subdomainsearch= f"https://rdb.pri.diamond.ac.uk/php/epics/cs_epigetsubdomain.php?domainid={domain}&subdomainid={subdomain}"
        print(f"Subdomain: {subdomain} - {fetch_value_rdb(subdomainsearch, 'subdomainname')}")

    techsearch= f"https://rdb.pri.diamond.ac.uk/php/epics/cs_epigettecharea.php?techareaid={techarea}"
    print(f"Technical Area: {techarea} - {fetch_value_rdb(techsearch, 'techareaname')}")

    compsearch= f"https://rdb.pri.diamond.ac.uk/php/epics/cs_epigetcomponent.php?componentid={component}"
    print(f"Component: {component} - {fetch_value_rdb(compsearch, 'componentname')}")