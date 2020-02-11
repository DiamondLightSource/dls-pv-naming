from mock import patch

from pv_naming.command_line.json_search import (
    COMPONENT,
    DOMAIN,
    TECHNICAL_AREA,
    json_search_by_name,
)
from pv_naming.fetch_from_rdb import fetch_from_rdb
from pv_naming.rdb_domain import RDB_API_ADDRESS


@patch("pv_naming.command_line.json_search.fetch_from_rdb")
def test_api_called_once_for_component(mocked_fetch_rdb):
    json_search_by_name("term", COMPONENT)
    mocked_fetch_rdb.assert_called_once_with(
        f"{RDB_API_ADDRESS}/cs_epigetcomponent.php?componentname=term",
        "componentid",
        "componentname",
    )


@patch("pv_naming.command_line.json_search.fetch_from_rdb")
def test_domain_api_used_for_domain(mocked_fetch_rdb):
    json_search_by_name("term", DOMAIN)
    mocked_fetch_rdb.assert_called_once_with(
        f"{RDB_API_ADDRESS}/cs_epigetdomain.php?domainname=term",
        "domainid",
        "domainname",
    )


@patch("pv_naming.command_line.json_search.fetch_from_rdb")
def test_techarea_api_used_for_techarea(mocked_fetch_rdb):
    json_search_by_name("term", TECHNICAL_AREA)
    mocked_fetch_rdb.assert_called_once_with(
        f"{RDB_API_ADDRESS}/cs_epigettecharea.php?techareaname=term",
        "techareaid",
        "techareaname",
    )


@patch("pv_naming.command_line.json_search.fetch_from_rdb")
def test_return_string_has_expected_values(mocked_fetch_rdb):
    mocked_fetch_rdb.return_value = {"TERM": "a test term"}
    result = json_search_by_name("term", COMPONENT)
    assert "TERM" in result
    assert "a test term" in result


@patch("pv_naming.command_line.json_search.fetch_from_rdb")
def test_error_string_produced_on_none_in_database(mocked_fetch_rdb):
    mocked_fetch_rdb.return_value = None
    result = json_search_by_name("term", COMPONENT)
    assert isinstance(result, str)
    assert "term" in result
