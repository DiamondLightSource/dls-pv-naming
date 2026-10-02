"""Command line tool to provide easy access to JSON search provided by RDB"""

from argparse import ArgumentParser

from dls_pv_naming.fetch_from_rdb import fetch_from_rdb
from dls_pv_naming.rdb_domain import RDB_API_ADDRESS

# Constants to dictate which section to search
DOMAIN = 0
TECHNICAL_AREA = 1
COMPONENT = 2


def json_search_by_name(search_term: str, section: int) -> str:
    """
    Search the correct section and return a formatted string of results
    If no results are found, return an error message
    """

    if section == DOMAIN:
        results = fetch_from_rdb(
            f"{RDB_API_ADDRESS}/cs_epigetdomain.php?domainname={search_term}",
            "domainid",
            "domainname",
        )
        tag = "domains"
    elif section == TECHNICAL_AREA:
        results = fetch_from_rdb(
            f"{RDB_API_ADDRESS}/cs_epigettecharea.php?techareaname={search_term}",
            "techareaid",
            "techareaname",
        )
        tag = "technical areas"
    elif section == COMPONENT:
        results = fetch_from_rdb(
            f"{RDB_API_ADDRESS}/cs_epigetcomponent.php?componentname={search_term}",
            "componentid",
            "componentname",
        )
        tag = "components"
    else:
        results = None
        tag = "unknown"

    if results is None:
        return f"""Search term \"{search_term}\" could not be found in recorded {tag}.
Please try a single short term."""
    else:
        result_string = f'The following {tag} were found for "{search_term}":\n'
        for k, v in results.items():
            result_string += f"{k}: {v}\n"
        return result_string


DESCRIPTION = """This tool provides a command line interface to the database API, \
to help you search for domains, technical areas and component names which are found in \
the database.
Works best with short search terms with no spaces.
If no arguments are applied it will search for components."""


def cli_json_search():
    parser = ArgumentParser(
        description=DESCRIPTION,
        epilog="Example to search for pump-related components: dls-pv-name-search pump",
    )

    parser.add_argument("search_term", type=str, help="the term to search for")
    parser.add_argument(
        "-c",
        "--component",
        action="store_true",
        default=False,
        help="search in components only <default>",
    )
    parser.add_argument(
        "-d",
        "--domain",
        action="store_true",
        default=False,
        help="search in domains only",
    )
    parser.add_argument(
        "-t",
        "--techarea",
        action="store_true",
        default=False,
        help="search in technical areas only",
    )

    args = parser.parse_args()

    if args.component:
        print(json_search_by_name(args.search_term, COMPONENT))
    elif args.domain:
        print(json_search_by_name(args.search_term, DOMAIN))
    elif args.techarea:
        print(json_search_by_name(args.search_term, TECHNICAL_AREA))
    else:
        # Use component as default
        print(json_search_by_name(args.search_term, COMPONENT))
