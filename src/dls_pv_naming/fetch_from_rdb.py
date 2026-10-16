"""
Fetch information from the database or locally cached files
"""

import json
import logging
from enum import Enum, StrEnum, auto
from importlib.resources import files
from urllib.parse import urlsplit, urlunsplit

import requests

from dls_pv_naming.rdb_domain import RDB_API_ADDRESS, RDB_DOMAIN


class RdbUrl(StrEnum):
    DOMAIN = f"{RDB_API_ADDRESS}/cs_epigetdomain.php"
    SUBDOMAIN = f"{RDB_API_ADDRESS}/cs_epigetsubdomain.php"
    TECH_AREA = f"{RDB_API_ADDRESS}/cs_epigettecharea.php"
    COMPONENT = f"{RDB_API_ADDRESS}/cs_epigetcomponent.php"


URL_CACHE_MAP = {
    RdbUrl.DOMAIN: "domains.json",
    RdbUrl.SUBDOMAIN: "subdomains.json",
    RdbUrl.TECH_AREA: "techarea.json",
    RdbUrl.COMPONENT: "component.json",
}


class State(Enum):
    INIT = auto()
    RDB_AVAILABLE = auto()
    RDB_UNAVAILABLE = auto()


STATE = State.INIT


def fetch_data(request_address: str, key: str, value: str) -> dict | None:
    """Get dictionary of all results which have key and value attributes"""

    data = _fetch_data(request_address)
    if "Error" not in data:
        first_key = list(data[0].keys())[0]
        return {element[key]: element[value] for element in data[0][first_key]}
    else:
        return None


def _fetch_data(request_address: str):
    global STATE
    if STATE == State.INIT:
        STATE = _test_rdb(RDB_DOMAIN)

    if STATE == State.RDB_AVAILABLE:
        data = fetch_from_rdb(request_address)
    else:
        data = fetch_from_cache(request_address)
    return data


def _test_rdb(rdb_domain: str) -> State:
    """Attempt to connect to the RDB, and mark if connection is/isn't possible"""
    try:
        resp = requests.head(rdb_domain)
        resp.raise_for_status()
        state = State.RDB_AVAILABLE
    except Exception:
        logging.error("Unable to connect to RDB. Falling back to local cache")
        state = State.RDB_UNAVAILABLE

    return state


def fetch_from_rdb(request_address: str):
    try:
        resp = requests.get(request_address)
    except requests.ConnectionError:
        logging.error(f"Unable to connect to {request_address}")
        raise

    resp.raise_for_status()

    return resp.json()


def fetch_from_cache(request_address: str):
    """Read the cached files associated with the requested address, apply any query
    strings, and return it in the same format as the RDB"""
    url_split = urlsplit(request_address)

    queries = []
    if url_split.query:
        # The cache contains the entire unfiltered dataset, so remove query param and
        # re-apply then as a filter later
        request_address = RdbUrl(urlunsplit(url_split._replace(query="")))

        # There will be one or more query parameters (key=value pairs)
        all_queries = url_split.query.split("&")
        for query in all_queries:
            query_key, query_value = query.split("=")
            queries.append((query_key, query_value))

    data = _read_cache_file(request_address)

    # The data is stored as a list with a single item: A dictionary with a single key,
    # whose values are then a list of dictionaries. e.g.:
    # [ {'domain' : [
    #       {'domainid': 'AM', 'domainname': 'Active Materials Building'},
    #       {'domainid': 'BK', 'domainname': 'Vacuum bakeout'}
    #     ]
    #   }
    # ]

    # If there was a query, we must now apply the query string(s) to search the data
    if queries:
        section = data[0]
        assert len(section) == 1
        # Extract the top level dict's one and only key
        key = next(iter(section))

        results = []

        for i in section[key]:
            # There are two formats of query parameters: "xxxid" and "xxxname"
            # e.g. "domainid" and "domainname".
            # "xxxid" looks for an exact match in the id field.
            # "xxxname" looks for a case-insensitive partial match in the name field.
            if queries[0][0].endswith("name"):
                assert len(queries) == 1, "Can only search on one 'name' parameter"
                # The RDB does case-insensitive searching
                if queries[0][1].lower() in i[queries[0][0]].lower():
                    results.append(i)

            elif all(i[query_key] == query_value for query_key, query_value in queries):
                # Re-create the format the RDB would return the data in - similar to
                # what is documented above
                return [{key: [i]}]
        else:
            # If we get here we must have had a "name" parameter and the list of
            # sections is now exhausted
            return [{key: results}]

    return data


def _read_cache_file(request_address: str):
    """Read the cache file related to the requested address.
    Address must not have any query parameters or fragments."""
    datafile = URL_CACHE_MAP[RdbUrl(request_address)]
    with files("dls_pv_naming.data").joinpath(datafile).open() as f:
        data = json.load(f)

    assert len(data) == 1, f"Unexpected extra data read from cached file {datafile}"
    return data


def fetch_value_rdb(request_address: str, key: str) -> dict | None:
    """Get a specific value from the RDB"""
    data = _fetch_data(request_address)
    if "Error" not in data:
        first_key = list(data[0].keys())[0]
        return data[0][first_key][0][key]
    else:
        return None


def fetch_pairs(request_address: str, key: str, value: str) -> dict | None:
    """
    Special function to extract lists of values which are paired together
    Prime example is getting lists of all subdomains which match a particular domain,
    and the inverse, all of the domains which match a particular subdomain.
    """
    data = _fetch_data(request_address)
    if "Error" not in data:
        first_key = list(data[0].keys())[0]
        # Generate list of matching values from key to value
        # return {key: [value, value, value], ...}
        pairs: dict = {}
        for element in data[0][first_key]:
            if element[key] not in pairs:
                # Start a list
                pairs[element[key]] = [element[value]]
            else:
                # Add to the list
                pairs[element[key]].append(element[value])
        return pairs
    else:
        return None


def fetch_all_information() -> dict:
    """Collect all useful information from the database"""
    return {
        "domain": fetch_data(RdbUrl.DOMAIN, "domainid", "domainname"),
        "subdomain": fetch_data(RdbUrl.SUBDOMAIN, "subdomainid", "subdomainname"),
        "domain_pair": fetch_pairs(RdbUrl.SUBDOMAIN, "domainid", "subdomainid"),
        "subdomain_pair": fetch_pairs(RdbUrl.SUBDOMAIN, "subdomainid", "domainid"),
        "technical_area": fetch_data(RdbUrl.TECH_AREA, "techareaid", "techareaname"),
        "component": fetch_data(RdbUrl.COMPONENT, "componentid", "componentname"),
    }
