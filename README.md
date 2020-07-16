[![pipeline status](https://gitlab.diamond.ac.uk/controls/python3/pv-naming/badges/master/pipeline.svg)](https://gitlab.diamond.ac.uk/controls/python3/pv-naming/commits/master)
[![coverage report](https://gitlab.diamond.ac.uk/controls/python3/pv-naming/badges/master/coverage.svg)](https://gitlab.diamond.ac.uk/controls/python3/pv-naming/commits/master)
[![Python 3.7](https://upload.wikimedia.org/wikipedia/commons/f/fc/Blue_Python_3.7_Shield_Badge.svg)](https://upload.wikimedia.org/wikipedia/commons/f/fc/Blue_Python_3.7_Shield_Badge.svg)

# PV Naming

Set of tools to help engineers at **Diamond Light Source** to name PVs consistently.

## Install

Hopefully you are at Diamond Light Source and this should just work:

`pipenv install`

## Test a PV/Device Name

When you are creating a database or an electical drawing, you may wish to confirm that your names are matching the [Diamond Naming Convention](<http://diamvdocs13.diamond.ac.uk/TECHNICAL%20DIVISION%20(TEC)/Controls%20and%20Interlocks%20CTRL/Reports%20(REP)/CTRL-XX-rpt-010%20Proposal%20for%20a%20DIAMOND%20Control%20System%20Naming%20Convention/CTRL-XX-rpt-010%20Proposal%20for%20a%20DIAMOND%20control%20system%20naming%20convention.doc>) and that the acronyms you are choosing have been properly recorded in the [Device Database](https://rdb.pri.diamond.ac.uk/php/login/cs_framepage.php).

To perform this check, use:

`dls-pv-name-check MY-DEVICE-NAME`

where `MY-DEVICE-NAME` is the name you wish to verify.

If the name passes all the checks you will receive a lovely message and if not then hopefully you will get some useful feedback.

## Analyse EPICS Database

To test an EPICS database against the Diamond naming convention and database, use `dls-pv-name-report`. This tool can run analysis on one or many \*.db files at once, and will produce a JSON styled report which should be easy to understand.

To analyse a database file:

`dls-pv-name-report my_db.db`

To analyse multiple database files at the same time:

`dls-pv-name-report my_db.db my_other_db.db`

To pipe the output to a file where you can view it later:

`dls-pv-name-report my_db.db --output /path/to/output.txt`

As the database has not been kept up to date, you might find yourself inundated with database errors.
To check only for formatting errors, which can usually be fixed in builder or the associated support module, use the `-f` option:

`dls-pv-name-report -f my_db.db`

which will only test against the naming convention.

## Analyse Builder IOC

To test whether your builder IOC is creating PV names which match the Diamond convention, build the IOCs and then use the `-b` option to specify a builder directory:

`dls-pv-name-report -b my_dir`

where `my_dir` is the absolute address of the top level builder directory you are interested in.
This will investigate every IOC in _/iocs_ and every database in the _/db_ directory of those IOCs.

By default, this will print the report to your terminal.
If you would like to write this to a file, use:

`dls-pv-name-report -b my_dir --output /path/to/output.txt`

As the database has not been kept up to date, you might find yourself inundated with database errors.
To check only for formatting errors, which can usually be fixed in builder or the associated support module, use the `-f` option:

`dls-pv-name-report -b -f my_dir`

which will only test against the naming convention.

## Search the Database

To find which terms have already been included in the database, use `dls-pv-name-search`.
This will search the description fields of the database to find matches to your search term.

By default, it will search for components, as this is the most numerous section:

```bash
$ dls-pv-name-search temp
The following components were found for "temp":
CRWAT: RF Circulator Temperature Compensation Unit
DIODE: Low temp diode
INJTP: Injection temperature
PT100: Temperature monitoring device
TCTRL: Temperature Controller Instrument (often cryostatic crontrol)
TEMPS: Temperature sensor
TMON: Temperature Monitor Instrument
TMPCC: TEMPERATURE CONTROL CRATE ( INTERLOCKS)
VTEMP: Vessel Temperature
```

You can also search for technical areas or domains with the `-t` and `-d` options:

```bash
$ dls-pv-name-search -t experiment
The following technical areas were found for "experiment":
EA: Experimental Apparatus
$ dls-pv-name-search -d experiment
The following domains were found for "experiment":
BL: Experimental Area
TE: Test Experimental Area (Test Beamlines)
```

The seach is relatively basic so you would be best served by using short, single word search terms which are more likely to return many results.
You could then narrow down this search by piping to grep if required:

```bash
$ dls-pv-name-search pump | grep -i scroll
SCROL: Scroll Vacuum Pump
```

## Analyse All IOCs

If you would like to get a more general feel for how consistent PV naming is in our production databases, use:

`pipenv run python pv_naming/analysis_scripts.py`

This will produce a file at `/scratch/ioc_reports.json` which provides the output of databases found in the latest version of every ioc in `/dls_sw/prod/R3.14.12.3/ioc` and `/dls_sw/prod/R3.14.12.7/ioc`.

# Gitlab CI

It is now possible to run some of the above commands as part of the Gitlab CI pipeline process.
Whenever code is pushed to the Gitlab repo, the PV checks will run and provide reports if failures occur.
The reports can be easily viewed in the browser.

The CI Templates for `pv-naming` are located [in the ci_templates repo](https://gitlab.diamond.ac.uk/controls/reports/ci_templates/-/blob/master/pv_name_report.yml).

An example of use can be found on the `ci-dev` branch of [**BL10J-BUILDER**](https://gitlab.diamond.ac.uk/controls/support/bl10j-builder/-/tree/ci-dev).
You can view the failing pv name report [here](https://gitlab.diamond.ac.uk/controls/support/bl10j-builder/-/jobs/17717) - otherwise click on `CI/CD -> Pipelines` and click a failing pipeline, marked with a red cross on the `ci-dev` branch.


# Development

While developing, please use the pre-commit hooks provided.
They can be easily activated when installing the package:

```bash
# Installs the package
pipenv install
# Installs the pre-commit hooks
pipenv run pre-commit install
```

These hooks are run by the continuous integration job on Gitlab so will otherwise fail.
They help to keep the code neat, tidy and correct.

Thanks!
