import argparse
import json
import logging

from pv_naming.analysis_scripts import report_builder_iocs, report_dbs


def command_line_file_report():

    logging.basicConfig(level=logging.INFO)

    argument_parser = argparse.ArgumentParser(
        description="""Produces a naming report for database files. Can analyse many at once.
Point directly to *.db files you wish to analyse.
Or to the <top> of a builder directory with build IOCs.""",
        epilog="""file-report mydb1.db mydb2.db mydb3.db
file-report -b /file/to/builder/top""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    argument_parser.add_argument(
        "databases",
        help="list of *.db files to analyse, or single builder directory to analyse",
        nargs="+",
    )

    argument_parser.add_argument(
        "-b",
        "--builder",
        action="store_true",
        help="specify that you are pointing to the <top> of a single builder directory and wish to view a report of built IOCs",
    )

    argument_parser.add_argument(
        "--output",
        help="specify an output file for the report rather than printing to terminal",
    )

    argument_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="add this option to print full list of occurences to the terminal",
    )

    argument_parser.add_argument(
        "-f",
        "--format-only",
        action="store_true",
        default=False,
        help="add this option if you do not want to include checks agains the database in the report",
    )

    args = argument_parser.parse_args()

    if args.builder:
        report = report_builder_iocs(args.databases[0], args.verbose, args.format_only)
    else:
        report = report_dbs(args.databases, args.verbose, args.format_only)

    if args.output:
        with open(args.output, "w") as fp:
            json.dump(report, fp, indent=2)
    else:
        print(json.dumps(report, indent=2))

    if report == {}:
        return 0
    else:
        # Return non zero value on failure for use as hook
        return 1
