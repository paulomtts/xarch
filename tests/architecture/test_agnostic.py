"""xarch's code names no part of any bundled architecture as an architecture concept: those names come from the
profile, and belong in xarch/architectures/ (the bundled profiles, templates and examples).

Scope: every string literal in xarch's Python source outside xarch/architectures/, including the text of f-strings;
docstrings are prose and are not scanned, nor are identifiers and import statements, so xarch's own package folders
(xarch.modules, xarch.kernel, ...) and its own names do not count. A name is matched as a whole word. The names are
every part and every layout folder of the bundled profiles, and the singular name of the repeating folder (`module`):
as a string literal it is an architecture concept, while Python's own notion of a module (docstrings, `ast.Module`,
`imp.module`, `sys.stdlib_module_names`) is an identifier or prose and never a string literal here. Nothing is allowed: ALLOWED stays empty.
"""
import ast
import io
import re
import tokenize
from pathlib import Path

import xarch
from xarch.bootstrap.wiring import load_architecture

SRC = Path(xarch.__file__).parent
BUNDLED = SRC / "architectures"

ALLOWED: dict[tuple[str, str], str] = {}


def concept_names() -> set[str]:
    names: set[str] = set()

    def walk(tree):
        for name, sub in tree.items():
            names.add(name.removesuffix(".py"))
            if sub:
                walk(sub)

    for profile in ("cli", "web"):
        architecture = load_architecture(profile)
        names |= set(architecture.parts) | {architecture.singular}
        walk(architecture.layout)
    return names - {"*"}


def docstring_lines(tree: ast.AST) -> set[int]:
    lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                lines.add(first.lineno)
    return lines


def literals_naming(names: set[str], root: Path = SRC) -> list[tuple[str, int, str]]:
    word = re.compile(r"\b(" + "|".join(sorted(names)) + r")\b")
    found = []
    for file in sorted(root.rglob("*.py")):
        if file.is_relative_to(BUNDLED) and root == SRC:
            continue
        text = file.read_text()
        docs = docstring_lines(ast.parse(text))
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type in (tokenize.STRING, tokenize.FSTRING_MIDDLE) and token.start[0] not in docs:
                for match in word.finditer(token.string):
                    found.append((file.relative_to(root).as_posix(), token.start[0], match[1]))
    return found


def test_xarch_names_no_part_of_a_bundled_architecture_outside_the_bundled_files():
    found = [f"xarch/{file}:{line}: names '{name}'" for file, line, name in literals_naming(concept_names())
             if (file, name) not in ALLOWED]
    assert found == []


def test_the_scan_would_catch_a_part_name(tmp_path):
    (tmp_path / "words.py").write_text('"""A docstring about cli."""\nNAME = "cli"\nOTHER = f"the {NAME} bootstrap"\n')
    assert literals_naming({"cli", "bootstrap"}, tmp_path) == [("words.py", 2, "cli"), ("words.py", 3, "bootstrap")]


def test_the_singular_name_of_the_repeating_folder_is_among_the_names_scanned():
    assert "module" in concept_names()
