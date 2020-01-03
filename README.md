[![pipeline status](https://gitlab.diamond.ac.uk/controls/python3/pv-naming/badges/master/pipeline.svg)](https://gitlab.diamond.ac.uk/controls/python3/pv-naming/commits/master)
[![coverage report](https://gitlab.diamond.ac.uk/controls/python3/pv-naming/badges/master/coverage.svg)](https://gitlab.diamond.ac.uk/controls/python3/pv-naming/commits/master)
[![Python 3.7](https://upload.wikimedia.org/wikipedia/commons/f/fc/Blue_Python_3.7_Shield_Badge.svg)](https://upload.wikimedia.org/wikipedia/commons/f/fc/Blue_Python_3.7_Shield_Badge.svg)

# PV Naming

Set of tools to help engineers at **Diamond Light Source** to name PVs consistently.

## Install

Hopefully you are at Diamond Light Source and this should just work:

`pipenv install`

## Test a PV/Device Name

When you are creating a database or an electical drawing, you may wish to confirm that your names are matching the [Diamond Naming Convention](http://diamvdocs13.diamond.ac.uk/TECHNICAL%20DIVISION%20(TEC)/Controls%20and%20Interlocks%20CTRL/Reports%20(REP)/CTRL-XX-rpt-010%20Proposal%20for%20a%20DIAMOND%20Control%20System%20Naming%20Convention/CTRL-XX-rpt-010%20Proposal%20for%20a%20DIAMOND%20control%20system%20naming%20convention.doc) and that the acronyms you are choosing have been properly recorded in the [Device Database](https://rdb.pri.diamond.ac.uk/php/login/cs_framepage.php).

To perform this check, use:

`pipenv run device_name_check MY-DEVICE-NAME`

where `MY-DEVICE-NAME` is the name you wish to verify.

If the name passes all the checks you will receive a lovely message and if not then hopefully you will get some useful feedback.

## Analyse Builder IOC

To test whether your builder IOC is creating PV names which match the Diamond convention, build the IOCs and then use:

`pipenv run builder_ioc_naming_report my_dir`

where `my_dir` is the absolute address of the top level builder directory you are interested in.
This will investigate every IOC in */iocs* and every database in the */db* directory of those IOCs.

By default, this will print the report to your terminal.
If you would like to write this to a file, use:

`pipenv run builder_ioc_naming_report my_dir --output /path/to/my/file`

## Analyse All IOCs

If you would like to get a more general feel for how consistent PV naming is in our production databases, use:

`pipenv run python pv_naming/analysis_scripts.py`

This will produce a file at `/scratch/ioc_reports.json` which provides the output of databases found in the latest version of every ioc in `/dls_sw/prod/R3.14.12.3/ioc` and `/dls_sw/prod/R3.14.12.7/ioc`.