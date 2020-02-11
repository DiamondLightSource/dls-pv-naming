from pathlib import Path

from mock import patch
from pytest import raises

from pv_naming.analysis_scripts import report_dbs


@patch("pv_naming.analysis_scripts.fetch_all_information")
class TestReportDbs:
    def test_fetch_all_information_is_called_once(self, mock_fetch_all, tmpdir):
        mock_db = tmpdir / "mydb.db"
        mock_db.write("")
        with patch.object(Path, "is_file") as mock_is_file:
            mock_is_file.return_value = True
            report_dbs([mock_db], verbose=False)
            mock_fetch_all.assert_called_once()

    def test_report_many_called_with_all_files(self, mock_fetch_all, tmpdir):
        mock_db1 = tmpdir / "mydb1.db"
        mock_db2 = tmpdir / "mydb2.db"

        mock_fetch_all.return_value = {}

        with patch.object(Path, "is_file") as mock_is_file:
            mock_is_file.return_value = True
            with patch(
                "pv_naming.analysis_scripts.record_file_report_many"
            ) as mock_record_file_report_many:
                report_dbs([mock_db1, mock_db2], verbose=False)
                mock_record_file_report_many.assert_called_once_with(
                    [mock_db1, mock_db2], {}, False, False
                )

    def test_raises_value_error_if_bad_path_given(self, mock_fetch_all):
        with raises(ValueError):
            report_dbs(["not a db"], verbose=False)
