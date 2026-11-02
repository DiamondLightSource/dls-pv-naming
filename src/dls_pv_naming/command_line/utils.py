from argparse import ArgumentParser

from dls_pv_naming.fetch_data import State


def add_datasource_argument(argument_parser: ArgumentParser):
    """Add the datasource mutually exclusive group to the given ArgumentParser.
    Writes value into "datasource" attribute."""

    arg_destination = "datasource"

    exclusive_group = argument_parser.add_mutually_exclusive_group()
    exclusive_group.set_defaults(**{arg_destination: State.INIT})
    exclusive_group.add_argument(
        "-r",
        "--rdb",
        action="store_const",
        const=State.USE_RDB,
        help="Retrieve data only from the Diamond RDB, ignoring local snapshot",
        dest=arg_destination,
    )
    exclusive_group.add_argument(
        "-s",
        "--snapshot",
        action="store_const",
        const=State.USE_SNAPSHOT,
        help="Retrieve data only from the local snapshot, ignoring the Diamond RDB",
        dest=arg_destination,
    )
    exclusive_group.add_argument(
        "-a",
        "--attempt-rdb",
        action="store_const",
        const=State.INIT,
        help="(default) Attempt to retrieve data from Diamond RDB, and fall back to "
        "snapshot if uncontactable",
        dest=arg_destination,
    )
