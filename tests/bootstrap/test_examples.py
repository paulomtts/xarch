"""The example check through the wiring: the bundled examples obey their architectures' rules, and a custom
architecture's can be checked."""
import io
import tokenize
from pathlib import Path

import pytest

import xarch
from tests.bootstrap.project import bundled_profiles, example_problems
from xarch.bootstrap.wiring import build_controllers


def test_the_bundled_examples_obey_their_architectures_rules():
    for profile in bundled_profiles():
        assert example_problems(profile) == (), profile


EXAMPLES = Path(xarch.__file__).parent / "architectures" / "examples"


def trailing_comments(text: str) -> list[int]:
    """The lines of a text on which a comment follows code."""
    lines = text.splitlines(keepends=True)
    return [token.start[0] for token in tokenize.generate_tokens(io.StringIO(text).readline)
            if token.type == tokenize.COMMENT and lines[token.start[0] - 1][:token.start[1]].strip()]


def test_every_comment_of_a_bundled_example_sits_on_a_line_of_its_own():
    """A comment at the end of a code line would be cut from it when review sends the example: each says why the code
    below it sits where it does on a line above it instead."""
    found = {path.relative_to(EXAMPLES).as_posix(): lines for path in sorted(EXAMPLES.rglob("*.py"))
             if (lines := trailing_comments(path.read_text(encoding="utf-8")))}
    assert found == {}


@pytest.mark.parametrize("text, lines", [
    ("x = 1  # one\n", [1]),
    ("# one\nx = 1\n", []),
    ("x = '# not a comment'\n", []),
    ("def f():\n    # inside\n    return 1  # after\n", [3]),
])
def test_trailing_comments(text, lines):
    assert trailing_comments(text) == lines


CUSTOM = """\
xarch: 2
name: layered
parts:
  api:   {path: "src/<module>/api", role: handlers, may_import: [store]}
  store: {path: "src/<module>/store", role: database access}
docs:
  entry: api
  pages:
    architecture.md: {from: layered.md}
  examples: [examples]
"""


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


@pytest.mark.parametrize("code, problems", [
    ("from app.src.billing.store import Repo\n", ()),
    ("from app.src.tax.store import Repo\n",
     ("example (src/billing/api/handler.py): imports app.src.tax.store which api may not import (parts.api.may_import)",)),
])
def test_a_custom_architecture_can_be_checked(tmp_path, code, problems):
    """Not checked unless asked."""
    write(tmp_path / "examples" / "src/billing/api/handler.py", code)
    write(tmp_path / "layered.md", "{{example:src/billing/api/handler.py}}\n")
    path = write(tmp_path / "layered.yaml", CUSTOM)
    assert example_problems(path) == problems
    texts = {"/".join(f.path): f.template for f in build_controllers().spec.docs(str(path)).files}
    assert texts["architecture.md"] == f"```python\n# src/billing/api/handler.py\n{code}```\n"
