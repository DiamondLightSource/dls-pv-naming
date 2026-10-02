"""Test the output for format reports"""

from dls_pv_naming.pv_format_check import pv_format_report


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
        "Device name must contain 4 elements separated by hyphens: Domain-TechnicalArea"
        "-Component-Identifier"
    ]


def test_double_colon():
    assert pv_format_report("BL16I-EA-IOC-01::SubDevice") == [
        "Only use single colons to separate device and subdevices"
    ]


def test_lowercase_not_allowed():
    assert "PV device name must not contain lowercase characters" in set(
        pv_format_report("BL16I-ea-IOC-01")
    )


def test_domain_must_have_two_capital_letters():
    assert "Domain in B16I should be composed of two capital letters" in set(
        pv_format_report("B16I-EA-IOC-01")
    )


def test_subdomain_must_have_number_alphanumeric_letter():
    assert pv_format_report("BL16-EA-IOC-01") == [
        "Subdomain in BL16 should be composed of a number, alphanumeric, and a letter"
    ]


def test_technical_area_must_have_two_capital_letters():
    assert pv_format_report("BL16I-E-IOC-01") == [
        "Technical Area of E must contain 2 letters"
    ]


def test_component_has_up_to_five_alphanumerics():
    assert pv_format_report("BL16I-EA-TOOLONG-01") == [
        "Component of TOOLONG must contain up to five alphanumeric characters, first "
        "character must be letter"
    ]


def test_identifier_has_only_two_numbers():
    assert pv_format_report("BL16I-EA-IOC-0L") == [
        "Identifier of 0L must contain only 2 numbers"
    ]


def test_indentifier_has_letter_O_instead_of_zero():  # noqa: N802 Need a capital letter in name
    assert "Found capital letter O in identifier, expected number zero" in set(
        pv_format_report("BL16I-EA-IOC-O1")
    )
