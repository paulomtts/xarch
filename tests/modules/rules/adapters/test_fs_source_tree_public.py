"""FsSourceTree on every Python file of xarch's own source (the bundled example project included) and of the recorded
corpora, each archive unpacked and never edited: each class, function (a method too), constant and name an import
takes is public exactly when its name does not start with the prefix of private names the language's data file
gives, the rule the checks read by spelling before the reader said it. A file that does not parse defines nothing and
is passed over."""
import tarfile
from importlib import resources
from pathlib import Path

import pytest
import yaml

from xarch.modules.rules.adapters.fs_source_tree import FsSourceTree
from xarch.modules.rules.domain.parsed import SourceFile
from xarch.platform.filesystem import FileSystem

PRIVATE = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))["private"]
SPECIAL = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))["special"]
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


def told(files: list[SourceFile]) -> dict[str, list[tuple[str, bool]]]:
    """Each name the files define or take by an import, by what it is, with whether the reader says it is public."""
    return {"class": [(c.name, c.public) for f in files for c in f.classes],
            "function": [(fn.name, fn.public) for f in files for fn in f.functions],
            "constant": [(c.name, c.public) for f in files for c in f.constants],
            "imported name": [(name, name not in i.withheld) for f in files for i in f.imports for name in i.names or ()]}


def broken(found: dict[str, list[tuple[str, bool]]]) -> dict[str, list[str]]:
    """The names, by what they are, whose flag is not the rule of the prefix."""
    return {what: sorted({name for name, public in named if public == name.startswith(PRIVATE)})
            for what, named in found.items()}


def test_every_name_of_xarch_s_own_source_is_public_exactly_when_it_does_not_start_with_the_prefix():
    files = read(SOURCE)
    assert files and broken(told(files)) == {"class": [], "function": [], "constant": [], "imported name": []}


@pytest.mark.parametrize("archive", [
    pytest.param("df537ca", id="the commit df537ca, as recorded"),
    pytest.param("7cc6111", id="the commit 7cc6111, as recorded"),
    pytest.param("examples", id="the bundled examples, as recorded"),
])
def test_every_name_of_a_recorded_corpus_is_public_exactly_when_it_does_not_start_with_the_prefix(tmp_path, archive):
    files = read(unpacked(archive, tmp_path))
    assert files and broken(told(files)) == {"class": [], "function": [], "constant": [], "imported name": []}


def test_the_source_read_holds_public_names_and_others_of_every_kind_so_that_the_rule_is_not_held_vacuously(tmp_path):
    found = told(read(SOURCE))
    for archive in ARCHIVES:
        for what, named in told(read(unpacked(archive, tmp_path / archive))).items():
            found[what] += named
    assert {what: {public for _, public in named} for what, named in found.items()} == {
        "class": {True, False}, "function": {True, False}, "constant": {True, False}, "imported name": {True, False}}
