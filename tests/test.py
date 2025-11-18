import pytest
from src.commands import Operations
from src.commands import script_dir

def test_ls_invalid_path():
    ops = Operations(arg="no_such_dir")
    result = ops.ls()
    assert result == []

def test_ls_file_instead_of_dir(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("data")
    ops = Operations(arg=str(f))
    result = ops.ls()
    assert result == []


def test_cd_invalid_path():
    ops = Operations(arg="no_such_dir")
    result = ops.cd()
    assert result is None


def test_cat_directory_instead_of_file(tmp_path):
    d = tmp_path / "dir"
    d.mkdir()
    ops = Operations(arg=str(d))
    result = ops.cat()
    assert result is None

def test_cat_nonexistent_file():
    ops = Operations(arg="missing.txt")
    result = ops.cat()
    assert result is None


def test_cp_source_not_exists(tmp_path):
    ops = Operations(arg=[str(tmp_path / "missing.txt"), str(tmp_path)])
    result = ops.cp()
    assert result is None

def test_cp_dir_without_r(tmp_path):
    src = tmp_path / "dir"
    src.mkdir()
    ops = Operations(arg=[str(src), str(tmp_path)], key=False)
    result = ops.cp()
    assert result is None



def test_rm_protected_path():
    ops = Operations(arg=script_dir)
    result = ops.rm()
    assert result is None

def test_rm_nonexistent_path():
    ops = Operations(arg="no_such_file.txt")
    result = ops.rm()
    assert result is None


def test_mv_source_not_exists(tmp_path):
    ops = Operations(arg=[str(tmp_path / "missing.txt"), str(tmp_path)])
    result = ops.mv()
    assert result is None

def test_undo_history_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("src.commands.history_path", str(tmp_path / "missing"))
    ops = Operations(arg=None)
    result = ops.undo()
    assert result is None

def test_zip_nonexistent_folder():
    ops = Operations(arg="no_such_dir")
    result = ops.zip()
    assert result is None

def test_zip_empty_folder(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    ops = Operations(arg=str(empty))
    result = ops.zip()
    assert result is None



def test_tar_nonexistent_folder():
    ops = Operations(arg="no_such_dir")
    result = ops.tar()
    assert result is None

def test_tar_empty_folder(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    ops = Operations(arg=str(empty))
    result = ops.tar()
    assert result is None



def test_unzip_nonexistent_archive():
    ops = Operations(arg="no_such.zip")
    result = ops.unzip()
    assert result is None

def test_unzip_not_zip(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("not a zip")
    ops = Operations(arg=str(f))
    result = ops.unzip()
    assert result is None


def test_untar_nonexistent_archive():
    ops = Operations(arg="no_such.tar")
    result = ops.untar()
    assert result is None

def test_untar_not_tar(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("not a tar")
    ops = Operations(arg=str(f))
    result = ops.untar()
    assert result is None


def test_history_file_not_found(tmp_path, monkeypatch):
    monkeypatch.setattr("src.commands.history_path", str(tmp_path / "missing"))
    ops = Operations(arg=5)
    result = ops.history()
    assert result is None

def test_history_invalid_arg(monkeypatch):
    monkeypatch.setattr("src.commands.history_path", "not_exists")
    ops = Operations(arg="bad")
    result = ops.history()
    assert result is None
