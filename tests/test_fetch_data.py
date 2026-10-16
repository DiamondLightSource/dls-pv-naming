import json
from importlib.resources import files
from unittest.mock import patch

import pytest
from pytest_httpserver.httpserver import HTTPServer

import dls_pv_naming.fetch_data
from dls_pv_naming.fetch_data import (
    URL_CACHE_MAP,
    RdbUrl,
    State,
    _fetch_data,
    _test_rdb,
    fetch_from_cache,
    fetch_pairs,
)

DOMAINID = "domainid"
DOMAINNAME = "domainname"
DATA_DOMAIN = [
    {DOMAINID: "AA", DOMAINNAME: "Test AA"},
    {DOMAINID: "BB", DOMAINNAME: "Test BB"},
]


def test_test_rdb_success(httpserver: HTTPServer):
    httpserver.expect_request("/", method="HEAD").respond_with_data("OK")

    assert _test_rdb(httpserver.url_for("/"))

    httpserver.check()


def test_test_rdb_fails_when_no_response():
    """Test that the method will mark the RDB as uncontactable when it cannot be
    reached"""

    assert _test_rdb("http://localhost:999999") == State.RDB_UNAVAILABLE


def test_test_rdb_fails_when_bad_status_returned(httpserver: HTTPServer):
    """Test that the method will mark the RDB as uncontactable when it reads an
    error HTTP code"""

    httpserver.expect_request("/", method="HEAD").respond_with_data("Error", status=404)

    assert _test_rdb(httpserver.url_for("/")) == State.RDB_UNAVAILABLE

    httpserver.check()


@patch("dls_pv_naming.fetch_data.STATE", State.RDB_AVAILABLE)
def test__fetch_data_rdb_connected(monkeypatch):
    """Test _fetch_data calls the RDB when it is marked as connected"""
    data = [{"abc": "def"}]
    monkeypatch.setattr(dls_pv_naming.fetch_data, "fetch_from_rdb", lambda x: data)

    # Arbitrary RdbUrl
    assert _fetch_data(RdbUrl.DOMAIN) == data


@patch("dls_pv_naming.fetch_data.STATE", State.RDB_UNAVAILABLE)
def test__fetch_data_rdb_disconnected(monkeypatch):
    """Test _fetch_data uses the cache when the RDB is marked as disconnected"""
    data = [{"abc": "def"}]
    monkeypatch.setattr(dls_pv_naming.fetch_data, "fetch_from_cache", lambda x: data)

    # Arbitrary RdbUrl
    assert _fetch_data(RdbUrl.DOMAIN) == data


def idfn(val: str):
    # Truncate the rdb_url to something more readable
    return val.split("/")[-1]


@pytest.mark.parametrize("rdb_url, filename", URL_CACHE_MAP.items(), ids=idfn)
def test_fetch_from_cache_returns_file_data(rdb_url, filename):
    """Test that the function returns the data exactly as appears on disk"""

    actual_data = fetch_from_cache(rdb_url)

    data_text = files("dls_pv_naming.data").joinpath(filename).read_text()
    expected_data = json.loads(data_text)

    assert actual_data == expected_data


@pytest.mark.parametrize(
    "rdb_url, query_str, expected_data",
    [
        (
            RdbUrl.DOMAIN,
            "domainid=SV",
            [{"domain": [{"domainid": "SV", "domainname": "Services"}]}],
        ),
        (
            RdbUrl.SUBDOMAIN,
            "subdomainid=01A",
            [
                {
                    "subdomain": [
                        {
                            "domainid": "SR",
                            "domainname": "Storage Ring",
                            "subdomainid": "01A",
                            "subdomainname": "Storage Ring - Arc -01",
                        }
                    ]
                }
            ],
        ),
        (
            RdbUrl.SUBDOMAIN,
            "domainid=SR&subdomainid=01C",
            [
                {
                    "subdomain": [
                        {
                            "domainid": "SR",
                            "domainname": "Storage Ring",
                            "subdomainid": "01C",
                            "subdomainname": "Storage Ring - Cell 01 (Common to Arc "
                            "and Straight)",
                        }
                    ]
                }
            ],
        ),
        (
            RdbUrl.TECH_AREA,
            "techareaid=BM",
            [
                {
                    "techarea": [
                        {
                            "techareaid": "BM",
                            "techareaname": "Building Management Interface",
                        }
                    ]
                }
            ],
        ),
        (
            RdbUrl.COMPONENT,
            "componentid=IOC",
            [
                {
                    "component": [
                        {
                            "componentid": "IOC",
                            "componentname": "IOC (Single VME processor and associated "
                            "I/O)",
                        }
                    ]
                }
            ],
        ),
    ],
)
def test_fetch_from_cache_using_id_query_string(rdb_url, query_str, expected_data):
    """Test various query strings apply correct filtering to cached data when using a
    'id' type of query string"""

    actual_data = fetch_from_cache(rdb_url + f"?{query_str}")

    assert actual_data == expected_data


@pytest.mark.parametrize(
    "rdb_url, query_str, expected_data",
    [
        (
            RdbUrl.DOMAIN,
            "domainname=storage ring transfer line",
            [
                {
                    "domain": [
                        {
                            "domainid": "BS",
                            "domainname": "Booster - Storage Ring transfer Line",
                        },
                        {
                            "domainid": "TC",
                            "domainname": "Test Booster - Storage Ring Transfer Line",
                        },
                    ]
                }
            ],
        ),
        (
            RdbUrl.TECH_AREA,
            "techareaname=power",
            [
                {
                    "techarea": [
                        {
                            "techareaid": "PC",
                            "techareaname": "Power Converters",
                        },
                        {
                            "techareaid": "PD",
                            "techareaname": "Power distribution",
                        },
                    ]
                }
            ],
        ),
        (
            RdbUrl.COMPONENT,
            "componentname=bias power supply",
            [
                {
                    "component": [
                        {"componentid": "BPS", "componentname": "Bias Power Supply"},
                        {
                            "componentid": "KLBPS",
                            "componentname": "Klystron Bias Power Supply",
                        },
                    ]
                }
            ],
        ),
    ],
)
def test_fetch_from_cache_using_name_query_string(rdb_url, query_str, expected_data):
    """Test various query strings apply correct filtering to cached data when using a
    'name' type of query string"""

    actual_data = fetch_from_cache(rdb_url + f"?{query_str}")

    assert actual_data == expected_data


def test_pairs_returns_expected_data():

    actual_data = fetch_pairs(RdbUrl.SUBDOMAIN, "domainid", "subdomainid")

    # Format off otherwise this data takes up 350+ lines
    # fmt: off
    expected_data = {
        "BL": [
            "01B", "01I", "02B", "02I", "02J", "03B", "03I", "03J", "04B", "04I", "04J",
            "05B", "05I", "05J", "06B", "06I", "06J", "07B", "07C", "07H", "07I", "08B",
            "08I", "08J", "09B", "09I", "09J", "09K", "10B", "10I", "10J", "11B", "11I",
            "11J", "11K", "12B", "12I", "13B", "13I", "13J", "14B", "14I", "14J", "15B",
            "15I", "15J", "16B", "16I", "17B", "17I", "18B", "18I", "19B", "19I", "20B",
            "20I", "20J", "21B", "21I", "22B", "22I", "23B", "23I", "24B", "24I", "38P",
        ],
        "BR": ["01C", "01S", "02C", "02S", "03C", "03S", "04C", "04S", "05C"],
        "CS": ["01R", "02R", "03R", "04R"],
        "FE": [
            "01B", "01I", "02B", "02I", "02J", "03B", "03I", "04B", "04I", "04J", "05B",
            "05I", "06B", "06I", "07B", "07C", "07I", "08B", "08I", "09B", "09I", "10B",
            "10I", "11B", "11I", "11K", "12B", "12I", "13B", "13I", "14B", "14I", "15B",
            "15I", "16B", "16I", "17B", "17I", "18B", "18I", "19B", "19I", "20B", "20I",
            "21B", "21I", "22B", "22I", "23B", "23I", "24B", "24I",
        ],
        "HV": ["01R"],
        "LA": ["02R", "11R", "79R"],
        "ME": [
            "01C", "01D", "01S", "01T", "01V", "02P", "02V", "03C", "03V", "04T", "05M",
            "06H", "07M", "08G", "09C", "10E", "11B", "12G", "13C", "14E", "15I", "16V",
            "17G",
        ],
        "RF": ["1TF"],
        "RT": ["01C"],
        "SR": [
            "00A", "01A", "01C", "01I", "01S", "01T", "02A", "02C", "02I", "02J", "02S",
            "03A", "03C", "03I", "03S", "04A", "04C", "04I", "04J", "04S", "05A", "05C",
            "05I", "05S", "06A", "06C", "06I", "06S", "07A", "07C", "07I", "07S", "07T",
            "08A", "08C", "08I", "08S", "09A", "09C", "09I", "09J", "09S", "10A", "10B",
            "10C", "10I", "10J", "10S", "11A", "11C", "11I", "11S", "12A", "12C", "12I",
            "12S", "13A", "13C", "13I", "13J", "13S", "14A", "14C", "14I", "14S", "15A",
            "15C", "15I", "15S", "16A", "16C", "16I", "16S", "17A", "17C", "17I", "17S",
            "18A", "18C", "18I", "18S", "19A", "19C", "19I", "19S", "20A", "20C", "20I",
            "20J", "20S", "21A", "21C", "21I", "21S", "22A", "22C", "22I", "22S", "23A",
            "23C", "23I", "23S", "24A", "24C", "24I", "24S", "26C", "99I",
        ],
        "TS": ["11I"],
    }
    # fmt: on

    assert actual_data == expected_data
