"""Reading a TOML file into plain values, and refusing one that is not TOML."""
import pytest

from xarch.platform.toml import TomlReader


def test_a_toml_file_reads_into_plain_values(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "web"\n')
    assert TomlReader().read(tmp_path / "pyproject.toml") == {"tool": {"xarch": {"profile": "web"}}}


def test_a_file_that_is_not_toml_raises_value_error(tmp_path):
    (tmp_path / "pyproject.toml").write_text("[tool\n")
    with pytest.raises(ValueError, match="Expected"):
        TomlReader().read(tmp_path / "pyproject.toml")
