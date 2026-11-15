"""Reading Python source stays behind its seam, so that another language can be added as another adapter: no file of
xarch's own code (outside xarch/architectures/, whose Python files are the bundled profiles' example project, content
that xarch ships and never runs) imports a module that reads Python source (ast, tokenize, symtable, inspect, or importlib, which
loads it) but the files listed in READERS, each with the modules it may import and why.

importlib.resources is not reading source: it reads the package data the bundled profiles ship (yaml, templates,
examples) and is allowed everywhere. An import is read as written, `import m`, `import m.sub` and `from m import
x` (as m.x), in any scope of the file; a relative import is xarch's own.
"""
import ast
from pathlib import Path

import pytest

import xarch

SRC = Path(xarch.__file__).parent
READING_SOURCE = {"ast", "tokenize", "symtable", "inspect", "importlib"}
DATA = ("importlib", "resources")

READERS: dict[str, tuple[set[str], str]] = {
    "modules/rules/adapters/fs_source_tree.py": (
        {"ast", "tokenize"}, "the seam: the SourceTree adapter, which parses the checked app's files into SourceFile"),
    "modules/spec/application/logic/example_imports.py": (
        {"ast"}, "the example check parses the bundled profiles' own Python examples, which ship with xarch as docs "
                 "content and are Python because the docs' example project is; a profile in another language brings "
                 "its own examples, and this check would go behind a port of the spec module then"),
}


def reading(path: Path) -> set[str]:
    """The source-reading modules the file imports, by their top-level name."""
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        names = ([alias.name for alias in node.names] if isinstance(node, ast.Import)
                 else [f"{node.module}.{alias.name}" for alias in node.names]
                 if isinstance(node, ast.ImportFrom) and node.module and not node.level else [])
        found |= {name.split(".")[0] for name in names
                  if name.split(".")[0] in READING_SOURCE and tuple(name.split("."))[:2] != DATA}
    return found


def test_only_the_listed_readers_import_a_module_that_reads_python_source():
    found = {path.relative_to(SRC).as_posix(): modules for path in sorted(SRC.rglob("*.py"))
             if "architectures" not in path.relative_to(SRC).parts and (modules := reading(path))}
    assert found == {path: modules for path, (modules, _) in READERS.items()}


@pytest.mark.parametrize("text, modules", [
    pytest.param("import ast\n", {"ast"}, id="an import of a reading module is found"),
    pytest.param("import inspect as i\n", {"inspect"}, id="an aliased import is found"),
    pytest.param("from tokenize import generate_tokens\n", {"tokenize"}, id="a from-import is found"),
    pytest.param("def f():\n    import symtable\n", {"symtable"}, id="an import inside a function is found"),
    pytest.param("import importlib.util\n", {"importlib"}, id="importlib, which loads source, is found"),
    pytest.param("from importlib import import_module\n", {"importlib"}, id="importlib's loader is found"),
    pytest.param("from importlib import resources\nfrom importlib.resources.abc import Traversable\n", set(),
                 id="importlib.resources reads package data and is not reading source"),
    pytest.param("import astroid\nfrom . import ast\n", set(), id="a longer name or a relative import is not one"),
])
def test_reading(tmp_path, text, modules):
    (tmp_path / "f.py").write_text(text)
    assert reading(tmp_path / "f.py") == modules
