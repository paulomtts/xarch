"""Knowledge of the checked language stays in two places, so that another language can be added as another data file and
another reader: the reader adapter, which turns source into neutral facts, and the language's data file shipped beside
the profiles (xarch/architectures/presets/language/<name>.yaml). This file holds two guards.

Reading source: no file of xarch's own code (outside xarch/architectures/, whose source files are the bundled profiles'
example project, content that xarch ships and never runs) imports a module that reads source (ast, tokenize, symtable,
inspect, or importlib, which loads it) but the files listed in READERS, each with the modules it may import and why.
importlib.resources is not reading source: it reads the package data the bundled profiles ship (yaml, templates,
examples) and is allowed everywhere. An import is read as written, `import m`, `import m.sub` and `from m import x`
(as m.x), in any scope of the file; a relative import is xarch's own.

Naming the language: no file of xarch's own code, but the reader and the platform (technology: the interpreter, the
package data), carries a word that encodes what is true of the language. The words are read from the data file of
the language the bundled profiles name: its title, the ending of a source file's name, the file that stands for a
folder (and its stem), every step of the names that mark an interface and of those that import by a computed name, the
namespace of the builtins and the folder of compiled files; and WORDS_BESIDES, the words the data file cannot hold
because it has no key for them. They are looked for in:

    every string literal  the text of an f-string included, whole words (an ending is a word that ends a name)
    every docstring       prose too: a docstring that describes the mechanism says it in the words of any language
    every identifier      a name, an attribute, a parameter or keyword, a function or class name, an imported module or
                          name, read as snake_case and camelCase words, for NAMES_BESIDES and the title of the language

`Protocol` is a word of the literals and docstrings, not of the identifiers: xarch's own ports are typing.Protocol, and
its own imports of the standard library are of no concern to the guard. EXEMPT names every file or word that stays, with
why; a stale entry fails the test. Nothing is exempt by pattern but the reader and the platform.
"""
import ast
import re
from pathlib import Path

import pytest
import yaml

import xarch

SRC = Path(xarch.__file__).parent
READING_SOURCE = {"ast", "tokenize", "symtable", "inspect", "importlib"}
DATA = ("importlib", "resources")

READERS: dict[str, tuple[set[str], str]] = {
    "modules/rules/adapters/fs_source_tree.py": (
        {"ast", "tokenize"}, "the seam: the SourceTree adapter, which parses the checked app's files into SourceFile"),
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


LANGUAGE = SRC / "architectures" / "presets" / "language" / "python.yaml"
WORDS_BESIDES = {"stdlib_module_names": "the interpreter's list of the standard library, which no data file can hold "
                                        "current: the platform reads it and the reader marks each import with it"}
NAMES_BESIDES = {"iskeyword", "kwlist"}
IDENTIFIER_FREE = {"protocol", "typing", "typing_extensions"}
"""Words that are literal text and docstring prose to the guard but may be identifiers: xarch's own ports are
typing.Protocol."""
SEAM = ("modules/rules/adapters/fs_source_tree.py", "platform/")
"""The reader adapter and the platform: where the language and its interpreter are allowed to be named."""

EXEMPT: dict[tuple[str, str], str] = {
    ("__main__.py", "python"): "`python -m xarch` is how the interpreter that runs xarch starts it, not the language "
                               "xarch checks",
}


def language_words() -> tuple[re.Pattern[str], set[str]]:
    """The pattern of the words the data file gives, as literal text, and the lowercase words of an identifier."""
    data = yaml.safe_load(LANGUAGE.read_text(encoding="utf-8"))
    steps = {step for name in (*data["interface"], *data["dynamic"]) for step in name.split(".")}
    words = {data["namespace"], data["cache"], data["package_file"].removesuffix(data["extension"]), *steps,
             *WORDS_BESIDES}
    ending = re.escape(data["extension"])
    whole = "|".join(sorted((re.escape(word) for word in words), key=len, reverse=True))
    title = f"(?i:{re.escape(data['title'])})"
    pattern = re.compile(rf"(?<![A-Za-z0-9_])(?:{title}|{whole})(?![A-Za-z0-9_])|{ending}(?![A-Za-z0-9_])")
    return pattern, {data["title"].lower(), data["namespace"], *{s.lower() for s in steps} - IDENTIFIER_FREE,
                     *WORDS_BESIDES, *NAMES_BESIDES}


def parts_of(identifier: str) -> set[str]:
    return {identifier.lower(), *filter(None, re.split(r"_+|(?<=[a-z0-9])(?=[A-Z])", identifier.lower()))}


def identifiers(node: ast.AST) -> list[tuple[int, str]]:
    names: list[str] = []
    match node:
        case ast.Name(id=name) | ast.arg(arg=name) | ast.FunctionDef(name=name) | ast.AsyncFunctionDef(name=name):
            names = [name]
        case ast.ClassDef(name=name) | ast.Attribute(attr=name):
            names = [name]
        case ast.keyword(arg=str() as name):
            names = [name]
        case ast.Import(names=aliases):
            names = [step for alias in aliases for step in alias.name.split(".")]
        case ast.ImportFrom(module=module, names=aliases):
            names = [*(module or "").split("."), *(alias.name for alias in aliases)]
    return [(getattr(node, "lineno", 0), name) for name in names if name]


def leaks(root: Path, pattern: re.Pattern[str], names: set[str]) -> list[tuple[str, int, str]]:
    """(file below root, line, word) of every word the language's data file gives, outside the seam, in the literals, the
    docstrings and the identifiers of the files below root."""
    found: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(("architectures/", *SEAM)):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                found += [(relative, node.lineno, match[0].lower()) for match in pattern.finditer(node.value)]
            found += [(relative, line, word) for line, name in identifiers(node)
                      for word in sorted(parts_of(name) & names)]
    return found


def test_no_file_outside_the_reader_and_the_platform_names_the_language_of_the_data_file():
    pattern, names = language_words()
    found = {(file, word) for file, _, word in leaks(SRC, pattern, names)}
    assert sorted(found - set(EXEMPT)) == []
    assert sorted(set(EXEMPT) - found) == []


def test_the_words_are_read_from_the_data_file_of_the_language():
    pattern, names = language_words()
    said = ("Python .py __init__ __init__.py typing_extensions Protocol importlib import_module __import__ builtins "
            "__pycache__ stdlib_module_names")
    assert {match[0] for match in pattern.finditer(said)} >= {
        "Python", ".py", "__init__", "typing_extensions", "Protocol", "importlib", "import_module", "__import__",
        "builtins", "__pycache__", "stdlib_module_names"}
    assert {"python", "builtins", "importlib", "__import__", "stdlib_module_names", "iskeyword"} <= names
    assert not {"protocol", "typing"} & names


@pytest.mark.parametrize("text, found", [
    pytest.param('NAME = "kernel.py"\n', [".py"], id="an ending in a literal"),
    pytest.param('A = "pythonic"\nB = "the python file"\n', ["python"], id="the title is a whole word"),
    pytest.param('A = f"{x}/__init__.py"\n', ["__init__", ".py"], id="the text of an f-string is read"),
    pytest.param('def f():\n    """About Protocol classes."""\n', ["protocol"], id="a docstring is read"),
    pytest.param('def f():\n    """xarch is a protocol, not a closed world."""\n', [], id="a word is read as written"),
    pytest.param('import importlib\nx = importlib.import_module\n', ["importlib", "importlib", "import_module"],
                 id="an imported module and an attribute are identifiers"),
    pytest.param('python_steps = 1\nIS_PYTHON = 2\n', ["python", "python"], id="a word of an identifier"),
    pytest.param('from typing import Protocol\nclass P(Protocol): ...\n', [], id="a port of its own is no leak"),
    pytest.param('import sys\nx = sys.stdlib_module_names\n', ["stdlib_module_names"], id="the interpreter's list"),
])
def test_the_guard_finds_a_word_of_the_language_wherever_it_is_written(tmp_path, text, found):
    (tmp_path / "words.py").write_text(text)
    pattern, names = language_words()
    assert sorted(word for _, _, word in leaks(tmp_path, pattern, names)) == sorted(found)


def test_the_reader_and_the_platform_are_where_the_language_may_be_named(tmp_path):
    (tmp_path / "platform").mkdir()
    (tmp_path / "platform" / "interpreter.py").write_text('import builtins\nA = "__init__.py"\n')
    (tmp_path / "modules" / "rules" / "adapters").mkdir(parents=True)
    (tmp_path / "modules" / "rules" / "adapters" / "fs_source_tree.py").write_text('A = "Python"\n')
    (tmp_path / "other.py").write_text('A = "Python"\n')
    pattern, names = language_words()
    assert [file for file, _, _ in leaks(tmp_path, pattern, names)] == ["other.py"]
