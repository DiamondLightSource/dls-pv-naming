from dls_pv_naming.pv_database_check import pv_database_check

# Mock out database
mock_database = {
    "domain": {"BL": "Beamline", "AA": "Test Domain"},
    "subdomain": {"00I": "Mocked Beamline", "99B": "Test Subdomain"},
    "domain_pair": {"BL": ["00I"]},
    "subdomain_pair": {"00I": ["BL"]},
    "technical_area": {"PY": "Python"},
    "component": {"TEST": "Test"},
}


def test_complete_valid_name_passes():
    assert pv_database_check("BL00I-PY-TEST-01", mock_database) is True


def test_valid_name_with_suffixes_passes():
    assert (
        pv_database_check("BL00I-PY-TEST-01:SOME:MORE_DEVICE:DETAILS", mock_database)
        is True
    )


def test_valid_name_without_subdomain_passes():
    assert (pv_database_check("AA-PY-TEST-01", mock_database)) is True


def test_invalid_domain_fails():
    assert (pv_database_check("XX-PY-TEST-01", mock_database)) is False


def test_invalid_technical_area_fails():
    assert (pv_database_check("BL-XX-TEST-01", mock_database)) is False


def test_invalid_component_fails():
    assert (pv_database_check("BL-PY-XX-01", mock_database)) is False


def test_invalid_subdomain_fails():
    assert (pv_database_check("BL00X-PY-TEST-01", mock_database)) is False


def test_invalid_domain_with_no_subodmain_pair_fails():
    assert (pv_database_check("AA00I-PY-TEST-01", mock_database)) is False


def test_subdomain_not_matched_to_domain_fails():
    assert pv_database_check("BL99B-PY-TEST-01", mock_database) is False


def test_invalid_identifier():
    assert pv_database_check("AA-PY-TEST-XX", mock_database) is False


def test_not_enough_values_fails():
    assert pv_database_check("AA", mock_database) is False
