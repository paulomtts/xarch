"""xarch's code names no part of any bundled architecture as an architecture concept, and no test framework: those
names come from the profile, and belong in xarch/architectures/ (the bundled profiles, templates and examples).

Scope: every string literal in xarch's Python source outside xarch/architectures/, including the text of f-strings;
docstrings are prose and are not scanned, nor are identifiers and import statements, so xarch's own package folders
(xarch.modules, xarch.kernel, ...) and its own names do not count. A name is matched as a whole word. The names are
every part and every layout folder of the bundled profiles, and the word of each repeating folder (`module`):
as a string literal it is an architecture concept, while Python's own notion of a module (docstrings, `ast.Module`,
`imp.module`, `sys.stdlib_module_names`) is an identifier or prose and never a string literal here. Nothing is allowed: ALLOWED stays empty.

The test framework is scanned the same way, in the same literals. Its names are read from what the bundled profiles
say for it: every dotted name of the guards (the table's decorator and row, the mocks, the autospec functions) and of
`tests.skips` (the markers and calls that skip a test) split into its words, the keywords (the table's, the spec's), and
the stems of the patterns of the test files and of the declared functions (`test_`, `_test`), found at the start of a name, never inside
a longer word (`latest_`). A few words of the
dotted names are ordinary English that the messages use for their own concept, a mock, a spec, an id, a mark, a
param, a test, a skip: they are EXEMPT, and the longer names around them (`unittest`, `Mock`, `spec_set`, `parametrize`)
are what the scan holds. Python itself is not scanned for: `typing.Protocol`, `__init__.py` and the standard
library's names are not a framework's, and neither are `importlib.import_module` and `__import__`, which the
enforcement section counts as dynamic imports.
"""
import ast
import io
import re
import tokenize
from pathlib import Path

import xarch
from xarch.bootstrap.wiring import load_architecture
from xarch.profile_values.testing import Place, ScenarioCoverage, StandIns

SRC = Path(xarch.__file__).parent
BUNDLED = SRC / "architectures"

ALLOWED: dict[tuple[str, str], str] = {}

EXEMPT = {"mock", "mark", "param", "id", "spec", "test", "skip"}

OWN_CONCEPTS = {"part", "parts", "tier", "tiers", "port", "ports", "fake", "fakes", "guard", "guards", "profile", "profiles",
                "command"}


def inflected(names: set[str]) -> set[str]:
    forms: set[str] = set()
    for name in names:
        forms |= {name, name + "s"}
        if name.endswith("s") and len(name) > 3 and not name.endswith("ss"):
            forms.add(name[:-1])
    return forms - OWN_CONCEPTS


def concept_names() -> set[str]:
    names: set[str] = set()

    def walk(tree):
        for name, sub in tree.items():
            names.add(name.removesuffix(".py"))
            if sub:
                walk(sub)

    for profile in ("cli", "web"):
        architecture = load_architecture(profile)
        names |= set(architecture.parts) | {repeat.word for repeat in architecture.repeats}
        walk(architecture.layout)
    return inflected(names - {"*"})


def framework_names() -> tuple[set[str], set[str]]:
    """The words and the stems the bundled profiles name for their test framework, EXEMPT words left out."""
    words: set[str] = set()
    stems: set[str] = set()
    for profile in ("cli", "web"):
        architecture = load_architecture(profile)
        assert architecture.framework is not None
        patterns = (*architecture.framework.files,
                    *(form.function for form in architecture.framework.declared if form.function))
        stems |= {stem for pattern in patterns for stem in re.split(r"\*|\.py$", pattern) if stem}
        words |= {word for name in architecture.framework.skips for word in name}
        for guard in architecture.guards:
            dotted: tuple[tuple[str, ...], ...] = ()
            if isinstance(guard, ScenarioCoverage):
                forms = architecture.framework.tables
                dotted = (*(form.decorator for form in forms), *(form.row for form in forms),
                          *(tuple(place.keyword for place in (form.columns_from, form.rows)
                                  if isinstance(place, Place) and place.keyword) for form in forms))
            elif isinstance(guard, StandIns):
                dotted = (*guard.mocks, *guard.autospec, guard.spec)
            words |= {word for name in dotted for word in name}
    return words - EXEMPT, stems


def docstring_lines(tree: ast.AST) -> set[int]:
    lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                lines.add(first.lineno)
    return lines


def literals_naming(names: set[str], root: Path = SRC, stems: frozenset[str] | set[str] = frozenset()
                    ) -> list[tuple[str, int, str]]:
    pattern = r"\b(" + "|".join(sorted(names)) + r")\b"
    if stems:
        pattern += r"|(?<![A-Za-z0-9])(" + "|".join(re.escape(s) for s in sorted(stems)) + ")"
    word = re.compile(pattern)
    found = []
    for file in sorted(root.rglob("*.py")):
        if file.is_relative_to(BUNDLED) and root == SRC:
            continue
        text = file.read_text()
        docs = docstring_lines(ast.parse(text))
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type in (tokenize.STRING, tokenize.FSTRING_MIDDLE) and token.start[0] not in docs:
                for match in word.finditer(token.string):
                    found.append((file.relative_to(root).as_posix(), token.start[0], match[0]))
    return found


def test_xarch_names_no_part_of_a_bundled_architecture_outside_the_bundled_files():
    found = [f"xarch/{file}:{line}: names '{name}'" for file, line, name in literals_naming(concept_names())
             if (file, name) not in ALLOWED]
    assert found == []


def test_xarch_names_no_test_framework_outside_the_bundled_files():
    words, stems = framework_names()
    found = [f"xarch/{file}:{line}: names '{name}'" for file, line, name in literals_naming(words, SRC, stems)
             if (file, name) not in ALLOWED]
    assert found == []


def test_the_framework_names_are_those_of_the_bundled_profiles():
    words, stems = framework_names()
    assert {"pytest", "parametrize", "unittest", "Mock", "MagicMock", "AsyncMock", "NonCallableMock",
            "NonCallableMagicMock", "create_autospec", "spec_set", "argnames", "argvalues", "skipif", "xfail",
            "importorskip", "skipIf", "skipUnless", "expectedFailure"} <= words
    assert stems == {"test_", "_test"}
    assert not words & EXEMPT


def test_xarch_names_no_linter_outside_the_bundled_files():
    found = [f"xarch/{file}:{line}: names '{name}'" for file, line, name in literals_naming({"ruff"})]
    assert found == []


def test_the_scan_would_catch_the_linter(tmp_path):
    (tmp_path / "words.py").write_text('"""About ruff."""\nCOMMAND = ["ruff", "check"]\n')
    assert literals_naming({"ruff"}, tmp_path) == [("words.py", 2, "ruff")]


def test_the_scan_would_catch_a_framework_name(tmp_path):
    (tmp_path / "words.py").write_text('"""A docstring about pytest."""\nA = "pytest"\nB = f"a {A} Mock"\n'
                                       'C = "test_a.py"\nD = "latest_a"\nE = "a mock for the spec"\n')
    found = literals_naming({"pytest", "Mock"}, tmp_path, {"test_"})
    assert found == [("words.py", 2, "pytest"), ("words.py", 3, "Mock"), ("words.py", 4, "test_")]


def test_the_scan_would_catch_a_part_name(tmp_path):
    (tmp_path / "words.py").write_text('"""A docstring about cli."""\nNAME = "cli"\nOTHER = f"the {NAME} bootstrap"\n')
    assert literals_naming({"cli", "bootstrap"}, tmp_path) == [("words.py", 2, "cli"), ("words.py", 3, "bootstrap")]


def test_the_scan_would_catch_the_singular_and_the_plural_of_a_part_name(tmp_path):
    (tmp_path / "words.py").write_text('A = "write the service step"\nB = f"the {A} adapters"\nC = "a port and a part"\n')
    assert literals_naming(inflected({"services", "adapter", "ports"}), tmp_path) == [
        ("words.py", 1, "service"), ("words.py", 2, "adapters")]


def test_the_singular_of_a_bundled_part_is_among_the_names_scanned():
    assert {"service", "adapter", "controller", "services", "adapters"} <= concept_names()
    assert not concept_names() & OWN_CONCEPTS


def test_the_singular_name_of_the_repeating_folder_is_among_the_names_scanned():
    assert "module" in concept_names()
