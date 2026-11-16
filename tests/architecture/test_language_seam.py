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

The data files of the profile format (presets/format/), which hold the texts xarch says of a profile's keys, carry
none of these words anywhere: they say a fact of the language only as a `%word%` that the language fills in.

`Protocol` is a word of the literals and docstrings, not of the identifiers: xarch's own ports are typing.Protocol, and
its own imports of the standard library are of no concern to the guard.

The data file also gives the tokens of the language's code, which are looked for by their kind:

    a literal that is a token     the prefix of a private name, the affix of a special one, the special method calling
                                  an instance runs, the annotation of no value, the comment marker, the shebang: a
                                  string literal equal to one is the language's rule written in xarch's code
    a directive word              the comment texts its tools read, as whole words in literals and docstrings
    a branching keyword           quoted as code (`if`) in literals and docstrings: plain prose may say "if"

EXEMPT names every file or word that stays, with why; a stale entry fails the test. Nothing is exempt by pattern but
the reader and the platform.
"""
import ast
import re
from dataclasses import fields
from pathlib import Path

import pytest
import yaml

import xarch
from xarch.profile_values.language import CheckedLanguage

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


LANGUAGES = tuple(sorted((SRC / "architectures" / "presets" / "language").glob("*.yaml")))
"""The data file of every language xarch reads: the guard holds the source to each."""
LANGUAGE = SRC / "architectures" / "presets" / "language" / "python.yaml"
"""The language the guard's own tests below are written for."""
WORDS_BESIDES = {"stdlib_module_names": "the interpreter's list of the standard library, which no data file can hold "
                                        "current: the platform reads it and the reader marks each import with it"}
NAMES_BESIDES = {"iskeyword", "kwlist", "isidentifier"}
"""Identifiers of the interpreter's own tests of a name against the language's rules, which no data file can hold."""
IDENTIFIER_FREE = {"protocol", "typing", "typing_extensions"}
"""Words that are literal text and docstring prose to the guard but may be identifiers: xarch's own ports are
typing.Protocol."""
SEAM = ("modules/rules/adapters/fs_source_tree.py", "platform/")
"""The reader adapter and the platform: where the language and its interpreter are allowed to be named."""

EXEMPT: dict[tuple[str, str], str] = {
    ("__main__.py", "python"): "`python -m xarch` is how the interpreter that runs xarch starts it, not the language "
                               "xarch checks",
    ("modules/rules/application/logic/scenarios.py", "_"): "the separator of snake_case, which the profile format "
                                                            "defines `{name}` to be in the test file of a use case "
                                                            "(guards.scenario-coverage.file); it is no private prefix, "
                                                            "and a profile in another language would still say "
                                                            "{name} in that case",
}


def language_words(language: Path = LANGUAGE) -> tuple[re.Pattern[str], set[str]]:
    """The pattern of the words the data file gives, as literal text, and the lowercase words of an identifier."""
    data = yaml.safe_load(language.read_text(encoding="utf-8"))
    steps = {step for name in (*data["interface"], *data["dynamic"]) for step in name.split(".")}
    words = {data["namespace"], data["cache"], data["package_file"].removesuffix(data["extension"]), *steps,
             *WORDS_BESIDES}
    ending = re.escape(data["extension"])
    whole = "|".join(sorted((re.escape(word) for word in words), key=len, reverse=True))
    title = f"(?i:{re.escape(data['title'])})"
    pattern = re.compile(rf"(?<![A-Za-z0-9_])(?:{title}|{whole})(?![A-Za-z0-9_])|{ending}(?![A-Za-z0-9_])")
    return pattern, {data["title"].lower(), data["namespace"], *{s.lower() for s in steps} - IDENTIFIER_FREE,
                     *WORDS_BESIDES, *NAMES_BESIDES}


TOKEN_KEYS = ("private", "special", "call", "nothing", "comment", "shebang")
"""The keys of the data file whose value is a token of the language's code."""


def language_tokens(language: Path = LANGUAGE) -> tuple[set[str], re.Pattern[str]]:
    """The tokens a literal may not be, and the pattern of the directive words and of the branching keywords quoted as
    code."""
    data = yaml.safe_load(language.read_text(encoding="utf-8"))
    tokens = {data[key] for key in TOKEN_KEYS}
    directives = "|".join(sorted((re.escape(word) for word in data["directives"]), key=len, reverse=True))
    branching = "|".join(re.escape(word) for word in data["branching"])
    return tokens, re.compile(rf"(?<![A-Za-z0-9_])(?:{directives})(?![A-Za-z0-9_])|`(?:{branching})`")


def token_leaks(root: Path, language: Path = LANGUAGE) -> list[tuple[str, int, str]]:
    """(file below root, line, token) of every literal that is a token of the language, and every directive word or
    branching keyword quoted as code, outside the seam."""
    tokens, words = language_tokens(language)
    found: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root).as_posix()
        if relative.startswith(("architectures/", *SEAM)):
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                found += [(relative, node.lineno, node.value)] if node.value in tokens else []
                found += [(relative, node.lineno, match[0]) for match in words.finditer(node.value)]
    return found


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


def named(language: Path) -> set[tuple[str, str]]:
    return {(file, word) for file, _, word in leaks(SRC, *language_words(language))}


def written(language: Path) -> set[tuple[str, str]]:
    return {(file, token) for file, _, token in token_leaks(SRC, language)}


@pytest.mark.parametrize("language", LANGUAGES, ids=lambda path: path.stem)
def test_no_file_outside_the_reader_and_the_platform_names_the_language_of_the_data_file(language):
    assert sorted(named(language) - set(EXEMPT)) == []


FORMAT = tuple(sorted((SRC / "architectures" / "presets" / "format").glob("*.yaml")))
"""The data files of the profile format, whose texts say a language's facts only through its `%word%`s."""


@pytest.mark.parametrize("language", LANGUAGES, ids=lambda path: path.stem)
def test_no_data_file_of_the_format_names_the_language_of_the_data_file(language):
    pattern, _ = language_words(language)
    found = [(path.name, match[0]) for path in FORMAT for match in pattern.finditer(path.read_text(encoding="utf-8"))]
    assert FORMAT and found == []


@pytest.mark.parametrize("language", LANGUAGES, ids=lambda path: path.stem)
def test_no_file_outside_the_reader_and_the_platform_writes_a_token_of_the_language_of_the_data_file(language):
    assert sorted(written(language) - set(EXEMPT)) == []


def test_every_exemption_is_one_some_language_still_needs():
    found = set().union(*(named(language) | written(language) for language in LANGUAGES))
    assert LANGUAGES and sorted(set(EXEMPT) - found) == []


@pytest.mark.parametrize("text, found", [
    pytest.param('PRIVATE = "_"\nx = name.startswith(("_", "."))\n', ["_", "_"], id="a literal that is the private prefix"),
    pytest.param('x = name.startswith("__") and name.endswith("__")\n', ["__", "__"], id="the affix of a special name"),
    pytest.param('A = "__call__"\nB = "None"\nC = "#"\nD = "#!"\n', ["__call__", "None", "#", "#!"],
                 id="the call method, no value, the comment marker and the shebang"),
    pytest.param('def f():\n    """Allowed: `# noqa` and `# type: ignore`; no `if` or `for`."""\n',
                 ["noqa", "type: ignore", "`if`", "`for`"], id="directive words and quoted branching keywords"),
    pytest.param('def f():\n    """None if nothing is found, for a start."""\nA = "a_b"\n', [],
                 id="prose and a literal that only holds a token are no leak"),
])
def test_the_guard_finds_a_token_of_the_language_where_it_is_written(tmp_path, text, found):
    (tmp_path / "tokens.py").write_text(text)
    assert sorted(token for _, _, token in token_leaks(tmp_path)) == sorted(found)


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


ENGINE = tuple(sorted(str(path.relative_to(SRC)) for folder in ("modules/rules/domain", "modules/rules/application/logic",
                                                                 "modules/rules/application/services", "kernel/logic")
                     for path in (SRC / folder).glob("*.py")))
"""The engine of rules and what it builds on: the domain of rules (the vocabulary, the rule, the records the reader
fills), its logic and services (the files that read, filter, match, say and expand, and the checks), and the kernel's
logic."""
SYNTAX = {"signature", "positional", "keyword_only", "star", "double", "decorated", "callee"}
"""The fields of the reader's records that say how the language writes a function and a call: its parameters by kind,
its decorators, the callee of its one call. What they mean (a method that only forwards) is the reader's to say. The
arguments of a call are read by the position and the keywords the profile's data gives."""
SAID = {field.name for field in fields(CheckedLanguage)} | {
    name for name, member in vars(CheckedLanguage).items()
    if not name.startswith("_") and (isinstance(member, property) or callable(member))}
"""What the engine may read of the language: what its data file says, CheckedLanguage's fields, and what CheckedLanguage
works out of them, its public properties and methods."""


def read_attributes(path: Path) -> set[str]:
    return {node.attr for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))) if isinstance(node, ast.Attribute)}


def _is_language(node: ast.AST) -> bool:
    return isinstance(node, ast.Attribute) and node.attr == "language"


def _annotated_language(arg: ast.arg) -> bool:
    annotation = arg.annotation
    return (isinstance(annotation, ast.Name) and annotation.id == CheckedLanguage.__name__) or (
        isinstance(annotation, ast.Constant) and annotation.value == CheckedLanguage.__name__)


def language_reads(path: Path) -> set[str]:
    """The attributes read of the language: on `<x>.language`, on a local name bound to one (`lang = x.language`), and
    on a parameter annotated CheckedLanguage."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    aliases = {target.id for node in ast.walk(tree) if isinstance(node, ast.Assign) and _is_language(node.value)
               for target in node.targets if isinstance(target, ast.Name)}
    aliases |= {node.arg for node in ast.walk(tree) if isinstance(node, ast.arg) and _annotated_language(node)}
    return {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
            and (_is_language(node.value) or (isinstance(node.value, ast.Name) and node.value.id in aliases))}


@pytest.mark.parametrize("file", ENGINE)
def test_the_engine_holds_no_fact_of_the_language_but_what_its_data_file_says(file):
    assert read_attributes(SRC / file) & SYNTAX == set()
    assert language_reads(SRC / file) <= SAID


@pytest.mark.parametrize("code, syntax, unsaid", [
    pytest.param("def f(function, profile):\n    return function.signature.star or profile.language.keywords\n",
                 {"signature", "star"}, {"keywords"}, id="how a function is written, and a word the data file lacks"),
    pytest.param("def f(profile):\n    lang = profile.language\n    return lang.decorators, lang.extension\n",
                 set(), {"decorators"}, id="a read through a local name bound to the language"),
    pytest.param("def f(language: CheckedLanguage):\n    return language.keywords, language.is_public('x')\n",
                 set(), {"keywords"}, id="a read of a parameter annotated as the language"),
    pytest.param("def f(profile):\n    return profile.language.call, profile.language.marks\n", set(), set(),
                 id="a field and a property of the language are said"),
])
def test_the_guard_would_catch_the_engine_reading_what_the_language_does_not_say(tmp_path, code, syntax, unsaid):
    (tmp_path / "facts.py").write_text(code)
    assert (read_attributes(tmp_path / "facts.py") & SYNTAX, language_reads(tmp_path / "facts.py") - SAID) == (
        syntax, unsaid)
