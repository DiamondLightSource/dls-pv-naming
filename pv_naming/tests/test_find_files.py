import glob

from pv_naming.find_files import find_builder_ioc_filenames


def test_finds_db_file_where_there_is_only_one(tmpdir):
    """To mock out the file set up, must mkdir() at every level
    so that Path.iterdir works properly.
    Must also write to file so that glob.glob catchs it properly"""
    iocs_dir = tmpdir / "iocs"
    iocs_dir.mkdir()
    mydb_dir = iocs_dir / "mydb"
    mydb_dir.mkdir()
    db_dir = mydb_dir / "db"
    db_dir.mkdir()
    mydb = db_dir / "mydb.db"
    mydb.write("")
    assert find_builder_ioc_filenames(tmpdir) == [mydb]


def test_finds_dbs_from_two_iocs(tmpdir):
    iocs_dir = tmpdir / "iocs"
    iocs_dir.mkdir()
    mydb1_dir = iocs_dir / "mydb1"
    mydb1_dir.mkdir()
    db1_dir = mydb1_dir / "db"
    db1_dir.mkdir()
    mydb1 = db1_dir / "mydb1.db"
    mydb1.write("")
    mydb2_dir = iocs_dir / "mydb2"
    mydb2_dir.mkdir()
    db2_dir = mydb2_dir / "db"
    db2_dir.mkdir()
    mydb2 = db2_dir / "mydb2.db"
    mydb2.write("")
    assert find_builder_ioc_filenames(tmpdir) == [mydb1, mydb2]


def test_finds_all_dbs_in_one_iocs(tmpdir):
    iocs_dir = tmpdir / "iocs"
    iocs_dir.mkdir()
    mydb_dir = iocs_dir / "mydb"
    mydb_dir.mkdir()
    db_dir = mydb_dir / "db"
    db_dir.mkdir()
    mydb1 = db_dir / "mydb1.db"
    mydb1.write("")
    mydb2 = db_dir / "mydb2.db"
    mydb2.write("")
    print(find_builder_ioc_filenames(tmpdir))
    assert find_builder_ioc_filenames(tmpdir) == [mydb1, mydb2]
