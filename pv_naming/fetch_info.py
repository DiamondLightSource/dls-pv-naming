"""
Fetch information from the database
"""

import logging
import requests
import time
from typing import List


def fetch_from_rdb(request_address: str, key: str, value: str) -> dict:
    """Get list of all the components"""
    resp = requests.get(request_address)
    if resp.status_code != 200:
        # This means something went wrong.
        raise Exception(f"GET /tasks/ {resp.status_code}")
    data = resp.json()
    if "Error" not in data:
        first_key = list(data[0].keys())[0]
        return {element[key]: element[value] for element in data[0][first_key]}
    else:
        return False


def fetch_value_rdb(request_address: str, key: str) -> dict:
    """Get list of all the components"""
    resp = requests.get(request_address)
    if resp.status_code != 200:
        # This means something went wrong.
        raise Exception(f"GET /tasks/ {resp.status_code}")
    data = resp.json()
    if "Error" not in data:
        first_key = list(data[0].keys())[0]
        return data[0][first_key][0][key]
    else:
        return None


def fetch_all_from_rdb(request_address: str, key: str, value: str) -> dict:
    """Get all component information from the database"""
    logging.debug(f"Reading information from {request_address}")
    component_data = {}
    comps = {}
    page_num = 1
    while (comps is not False) and (comps.keys() is not component_data.keys()):
        component_data.update(comps)
        comps = fetch_from_rdb(
            f"{request_address}?page={page_num}&recordsperpage=500", key, value
        )
        page_num += 1
    return component_data


def fetch_pairs(request_address: str, key: str, value: str) -> dict:
    """
    Special function to extract lists of values which are paired together
    Prime example is getting lists of all subdomains which match a particular domain,
    and the inverse, all of the domains which match a particular subdomain.
    """
    resp = requests.get(request_address)
    if resp.status_code != 200:
        # This means something went wrong.
        raise Exception(f"GET /tasks/ {resp.status_code}")
    data = resp.json()
    if "Error" not in data:
        first_key = list(data[0].keys())[0]
        # Generate list of matching balues from key to value
        # return {key: [value, value, value], ...}
        pairs = {}
        for element in data[0][first_key]:
            if element[key] not in pairs:
                # Start a list
                pairs[element[key]] = [element[value]]
            else:
                # Add to the list
                pairs[element[key]].append(element[value])
        return pairs
    else:
        return False


def fetch_information() -> dict:
    """Collect all useful information from the database"""
    return {
        "domain": fetch_from_rdb(
            "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigetdomain.php",
            "domainid",
            "domainname",
        ),
        "subdomain": fetch_from_rdb(
            "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigetsubdomain.php",
            "subdomainid",
            "subdomainname",
        ),
        "domain_pair": fetch_pairs(
            "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigetsubdomain.php",
            "domainid",
            "subdomainid",
        ),
        "subdomain_pair": fetch_pairs(
            "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigetsubdomain.php",
            "subdomainid",
            "domainid",
        ),
        "technical_area": fetch_from_rdb(
            "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigettecharea.php",
            "techareaid",
            "techareaname",
        ),
        "component": fetch_all_from_rdb(
            "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigetcomponent.php",
            "componentid",
            "componentname",
        ),
    }


if __name__ == "__main__":
    t = time.time()
    domains = fetch_from_rdb(
        "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigetdomain.php",
        "domainid",
        "domainname",
    )

    subdomains = fetch_from_rdb(
        "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigetsubdomain.php",
        "subdomainid",
        "subdomainname",
    )

    domain_pairs = fetch_pairs(
        "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigetsubdomain.php",
        "domainid",
        "subdomainid",
    )

    subdomain_pairs = fetch_pairs(
        "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigetsubdomain.php",
        "subdomainid",
        "domainid",
    )

    techareas = fetch_from_rdb(
        "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigettecharea.php",
        "techareaid",
        "techareaname",
    )

    comps = fetch_all_from_rdb(
        "http://rdb.pri.diamond.ac.uk/php/epics/cs_epigetcomponent.php",
        "componentid",
        "componentname",
    )
    print(f"Took {time.time() - t}")

    print(len(domains))
    print(len(techareas))
    print(len(comps))
