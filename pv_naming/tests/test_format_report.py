"""Test the output for format reports"""

from pv_naming.pv_format_check import pv_format_report


def test_valid_pv_returns_empty():
    assert pv_format_report("BL16I-EA-IOC-01") == []


def test_missing_colon():
    assert pv_format_report("BL16I-EA-K65-01SourceVoltage") == [
        "Missing a colon after the device name"
    ]

