from pv_naming.pv_database_check import split_into_elements
from pytest import raises


def test_response():
    assert split_into_elements("BL-EA-IOC-01") == ["BL", None,"EA","IOC", "01"]


def test_subdomain():
    assert split_into_elements("BL16I-EA-IOC-01") ==  ["BL", "16I","EA","IOC", "01"]


def test_not_enough_groups():
    with raises(ValueError):
        split_into_elements("BL:device")


def test_too_many_groups():
    with raises(ValueError):
        split_into_elements("BL-EA-IOC-01-02-03:device")
