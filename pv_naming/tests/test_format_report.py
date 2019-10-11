"""Test the output for format reports"""

from pv_naming.pv_format_check import pv_format_report


def test_valid_pv_returns_empty():
    assert pv_format_report("BL16I-EA-IOC-01") == []


def test_missing_colon():
    assert pv_format_report("BL16I-EA-K65-01SourceVoltage") == [
        "Missing a colon after the device name"
    ]


def test_underscore_instead_of_hyphen():
    assert pv_format_report("BL16I-EA-IOC_01") == [
        "PV must not contain underscores in device name"
    ]


def test_too_many_elements():
    # Too many elements to report as a missing colon because that makes the most sense
    assert pv_format_report("BL16I-EA-IOC-01-Extra-Group") == [
        "Missing a colon after the device name"
    ]


def test_not_enough_elements():
    assert pv_format_report("BL16I-EA-IOC") == [
        "Device name must contain 4 elements separated by hyphens: Domain-TechnicalArea-Component-Identifier"
    ]


def test_double_colon():
    assert pv_format_report("BL16I-EA-IOC-01::SubDevice") == [
        "Only use single colons to separate device and subdevices"
    ]
