import argparse
import json

from pv_naming.analysis_scripts import report_builder_iocs


def command_line_report_builder_iocs():

    argument_parser = argparse.ArgumentParser(
        description="Produces a report for database files found for the iocs in the builder directory provided"
    )

    argument_parser.add_argument(
        "builder_dir", default=".", help="top level builder directory to inspect"
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

    args = argument_parser.parse_args()

    report = report_builder_iocs(args.builder_dir)

    if args.output:
        with open(args.output, "w") as fp:
            json.dump(report, fp, indent=2)
    elif args.verbose:
        print(json.dumps(report, indent=2))
    else:
        for filename in report:
            for error_type in report[filename]:
                for device in report[filename][error_type]:
                    if len(report[filename][error_type][device]["occurences"]) > 3:
                        # Add elipses after the third value
                        report[filename][error_type][device]["occurences"] = report[
                            filename
                        ][error_type][device]["occurences"][:3] + ["..."]
        print(json.dumps(report, indent=2))
