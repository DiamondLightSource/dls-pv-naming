from unittest.mock import patch

from dls_pv_naming.analyse_file import (
    get_record_pvs,
    record_file_report,
)


def test_empty_list_for_text_with_no_records_in():
    assert (
        get_record_pvs(
            """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
     Duis viverra ex ut sagittis faucibus. Phasellus efficitur
     leo quis quam tincidunt, in porttitor mauris egestas. Sed
     eleifend congue nibh, a pulvinar velit semper sit amet.
     Donec imperdiet dui ultrices nibh lacinia pellentesque.
     Sed erat lacus, ultricies at lobortis quis, dictum non leo.
     Quisque ullamcorper lacinia accumsan. Aenean ac nulla sit
     amet est faucibus faucibus. Nunc semper feugiat quam id
     blandit. In lobortis porta tellus hendrerit euismod. Donec
     feugiat tortor diam, non efficitur ex fermentum vitae.
     Duis tincidunt, nisi id volutpat cursus, elit ex sagittis
     nunc, ac egestas dolor dolor sit amet nulla. Pellentesque
     molestie bibendum diam nec pellentesque. Nulla auctor
     scelerisque dui, id eleifend sapien finibus vel.
    """
        )
        == []
    )


def test_gets_device_name_from_record_declaration():
    assert get_record_pvs('record(mbbo, "BL16I-EA-IOC-04:ACCESS")') == [
        "BL16I-EA-IOC-04:ACCESS"
    ]


def test_gets_device_name_when_surrounded_by_other_text():
    assert get_record_pvs(
        """
#% macro, __doc__, Create some records for reading IOC statistics and details.
#% macro, IOC, Device prefix

# Used by Channel Access Security to determine access to this IOC.
record(mbbo, "BL16I-EA-IOC-04:ACCESS")
{
  field(DESC, "BL16I-EA-IOC-04 Acc Mode")
  field(PINI, "YES")
  field(ZRST, "Running")
  field(ZRSV, "NO_ALARM")
  field(ONST, "Maintenance")
  field(ONSV, "MINOR")
  field(TWST, "Test")
  field(TWSV, "MINOR")
  field(THST, "OFFLINE")
  field(THSV, "MAJOR")
  info(autosaveFields, "VAL")
}
record(stringin, "BL16I-EA-IOC-04:STARTTOD")
{
    field(DESC, "Time and date of startup")
    field(DTYP, "Soft Timestamp")
    field(PINI, "YES")
    field(INP, "@%Y-%m-%d %H:%M:%S")
}
    """
    ) == ["BL16I-EA-IOC-04:ACCESS", "BL16I-EA-IOC-04:STARTTOD"]


def test_ignores_pv_names_in_gui_tags():
    assert (
        get_record_pvs(
            "# % gui, i16Andor1.cam, enum, Shutter mode,   BL16I-EA-ANDOR-01:CAM:"
            "ShutterMode"
        )
        == []
    )


@patch("dls_pv_naming.analyse_file.record_text_report")
def test_record_file_report_calls_record_text_report_with_text_from_file(
    mocked_text_report, tmp_path
):
    text = "mocked database"
    mock_file = tmp_path / "mock_db.db"
    mock_file.write_text(text)

    record_file_report(mock_file, {})

    # Check that it read the file and called record_text_report
    mocked_text_report.assert_called_once_with(text, {}, False)
