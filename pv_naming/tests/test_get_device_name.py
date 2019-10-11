"""Test that get device name is working as imagined for a wide number of device scenarios"""

from pv_naming.pv_format_check import get_device_name


def test_check_returns():
    device = "BL16I-EA-IOC-01"
    assert get_device_name(device) == device


def test_subdevice_returns_device():
    assert get_device_name("BL16I-EA-IOC-01:DEVICE") == "BL16I-EA-IOC-01"


def test_multi_subdevice_returns_device():
    assert get_device_name("BL16I-EA-IOC-01:DEVICE:second_device") == "BL16I-EA-IOC-01"


def test_multi_colon():
    assert get_device_name("BL16I-EA-IOC-01::DEVICE") == "BL16I-EA-IOC-01::"


def test_underscores():
    assert get_device_name("BL16I-EA-IOC_01") == "BL16I-EA-IOC_01"


def test_missing_colons():
    assert get_device_name("BL16I-EA-IOC-01Missed_Colon") == get_device_name(
        "BL16I-EA-IOC-01Oops"
    )


def test_valid_equal_to_missing_colon():
    assert get_device_name("BL16I-EA-IOC-01") == get_device_name(
        "BL16I-EA-IOC-01MissingColon"
    )


def test_valid_equal_to_missing_colon_with_underscores():
    assert get_device_name("BL16I-EA-IOC-01") == get_device_name(
        "BL16I-EA-IOC-01Missing_Colon"
    )


def test_late_colon():
    assert get_device_name("BL16I-EA-IOC-01") == get_device_name(
        "BL16I-EA-IOC-01Missing:Colon"
    )
