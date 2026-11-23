"""FsSourceTree on every Python file of xarch's own source (the bundled example project included) and of the recorded
corpora, each archive unpacked and never edited: each class is a record exactly when the rule the checks worked out
before the reader said it holds of it, every method's name matching the language's special pattern in full and a
function of its file's top level naming the class in its return annotation. A file that does not parse defines nothing
and is passed over."""
import re
import tarfile
from importlib import resources
from pathlib import Path

import pytest
import yaml

from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.domain.parsed import Class, SourceFile
from xarch.platform.filesystem import FileSystem

PYTHON = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                        .read_text(encoding="utf-8"))
PRIVATE, SPECIAL = PYTHON["private"], PYTHON["special"]
SOURCE = Path(__file__).parents[4] / "xarch"
CORPORA = Path(__file__).parents[3] / "bootstrap" / "corpora"
ARCHIVES = ("df537ca", "7cc6111", "examples")


def read(root: Path) -> list[SourceFile]:
    """Every file below root that parses, read as `check` reads it."""
    tree = FsSourceTree(FileSystem())
    return [file for file in tree.read(root, tree.paths(root, (".py",)), standard=frozenset(), private=PRIVATE,
                                       special=SPECIAL) if file.error is None]


def unpacked(name: str, into: Path) -> Path:
    with tarfile.open(CORPORA / f"{name}.tar.xz") as archive:
        archive.extractall(into, filter="data")
    return into


def old(cls: Class, file: SourceFile) -> bool:
    """The rule the checks worked out before the reader said it: every method special, and a function of the file's
    top level naming the class in its return annotation."""
    return all(re.fullmatch(SPECIAL, method.name) for method in cls.methods) and any(
        cls.name in function.returns_named for function in file.functions if not function.owner)


def told(files: list[SourceFile]) -> list[tuple[str, bool, bool]]:
    """Each class of the files, by its file and its name, with what the reader says and what the old rule says."""
    return [(f"{file.name}:{cls.name}", cls.record, old(cls, file)) for file in files for cls in file.classes]


def broken(found: list[tuple[str, bool, bool]]) -> list[str]:
    """The classes the reader and the old rule disagree on."""
    return sorted(name for name, record, rule in found if record != rule)


def test_every_class_of_xarch_s_own_source_is_a_record_exactly_when_the_old_rule_says_it_is():
    files = read(SOURCE)
    assert files and broken(told(files)) == []


@pytest.mark.parametrize("archive", [
    pytest.param("df537ca", id="the commit df537ca, as recorded"),
    pytest.param("7cc6111", id="the commit 7cc6111, as recorded"),
    pytest.param("examples", id="the bundled examples, as recorded"),
])
def test_every_class_of_a_recorded_corpus_is_a_record_exactly_when_the_old_rule_says_it_is(tmp_path, archive):
    files = read(unpacked(archive, tmp_path))
    assert files and broken(told(files)) == []


def test_the_source_read_holds_records_and_other_classes_so_that_the_rule_is_not_held_vacuously(tmp_path):
    found = told(read(SOURCE))
    for archive in ARCHIVES:
        found += told(read(unpacked(archive, tmp_path / archive)))
    assert {record for _, record, _ in found} == {True, False}
