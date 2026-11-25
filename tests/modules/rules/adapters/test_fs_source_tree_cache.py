"""FsSourceTree with a cache folder: a file read again, unchanged, is not parsed again, and what it is read as is the
same; a change of its text, of what its relative imports name on disk, of how it is read, or of the reader's own code
reads it afresh, and a cache that cannot be read or written is no cache."""
import ast
import sys
from importlib import resources
from pathlib import Path

import pytest
import yaml

from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.platform.filesystem import FileSystem

STANDARD = frozenset(sys.stdlib_module_names)
"""The modules spec hands the reader for the language the tests' sources are written in."""
LANGUAGE = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                          .read_text(encoding="utf-8"))
HANDED = {"private": LANGUAGE["private"], "special": LANGUAGE["special"]}
"""What the reader is handed of the language's tokens, as `check` hands it."""


@pytest.fixture
def parses(monkeypatch):
    """How many times the language's parser runs from here on."""
    count = []
    real = ast.parse

    def counted(*args, **kwargs):
        count.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr("ast.parse", counted)
    return count


def project(tmp_path: Path) -> tuple[Path, Path, Path]:
    app, cache, code = tmp_path / "app", tmp_path / "cache", tmp_path / "code"
    (app / "domain").mkdir(parents=True)
    (app / "domain" / "order.py").write_text("class Order:\n    pass\n")
    (app / "domain" / "use.py").write_text("from .order import Order\n\n\ndef make():\n    return Order()\n")
    code.mkdir()
    (code / "reader.py").write_text("READER = 1\n")
    return app, cache, code


PATHS = [("domain", "order.py"), ("domain", "use.py")]


def read(app: Path, cache: Path | None, code: Path, private: str = HANDED["private"]):
    tree = FsSourceTree(FileSystem(), cache=cache, code=code)
    return tree.read(app, PATHS, standard=STANDARD, private=private, special=HANDED["special"])


def test_a_second_read_of_unchanged_files_parses_none_and_reads_the_same(tmp_path, parses):
    app, cache, code = project(tmp_path)
    first = read(app, cache, code)
    assert len(parses) == 2 and list(cache.iterdir())
    second = read(app, cache, code)
    assert len(parses) == 2 and second == first == read(app, None, code)


def test_a_file_whose_text_changed_is_parsed_again_alone(tmp_path, parses):
    app, cache, code = project(tmp_path)
    read(app, cache, code)
    (app / "domain" / "order.py").write_text("class Order:\n    pass\n\n\nclass Line:\n    pass\n")
    again = read(app, cache, code)
    assert len(parses) == 3 and [c.name for c in again[0].classes] == ["Order", "Line"]


def test_a_relative_import_whose_target_is_gone_is_read_as_unresolved_again(tmp_path):
    app, cache, code = project(tmp_path)
    assert [i.unresolved for i in read(app, cache, code)[1].imports] == [False]
    (app / "domain" / "order.py").unlink()
    gone = FsSourceTree(FileSystem(), cache=cache, code=code).read(app, [("domain", "use.py")], standard=STANDARD,
                                                                   **HANDED)
    assert [i.unresolved for i in gone[0].imports] == [True]


def test_how_a_file_is_read_is_part_of_what_is_kept(tmp_path):
    app, cache, code = project(tmp_path)
    assert [c.public for c in read(app, cache, code)[0].classes] == [True]
    (app / "domain" / "order.py").write_text("class _Order:\n    pass\n")
    assert [c.public for c in read(app, cache, code)[0].classes] == [False]
    assert [c.public for c in read(app, cache, code, private="")[0].classes] == [True]


def test_a_change_of_the_reader_s_own_code_reads_every_file_afresh(tmp_path, parses):
    app, cache, code = project(tmp_path)
    read(app, cache, code)
    (code / "reader.py").write_text("READER = 2\n")
    read(app, cache, code)
    assert len(parses) == 4


def test_a_cache_that_cannot_be_read_is_no_cache(tmp_path, parses):
    app, cache, code = project(tmp_path)
    first = read(app, cache, code)
    for kept in cache.iterdir():
        kept.write_bytes(b"not what was kept")
    assert read(app, cache, code) == first and len(parses) == 4


def test_a_cache_folder_that_cannot_be_written_is_no_cache(tmp_path):
    app, _, code = project(tmp_path)
    (tmp_path / "taken").write_text("a file, not a folder\n")
    assert read(app, tmp_path / "taken" / "cache", code) == read(app, None, code)
