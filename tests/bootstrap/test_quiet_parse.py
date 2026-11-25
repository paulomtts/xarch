"""`xarch check` prints nothing on stderr when the code it reads makes the parser warn, such as an invalid escape
sequence in a string: the warnings are the parser's about the user's code, not xarch's output."""
import subprocess
import sys
import warnings
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

WARNED = {
    "app/kernel/patterns.py": 'DIGITS = "\\d+"\nWORD = "[\\w]+"\n',
    "app/kernel/quoted.py": "TEXT = r'\"\\d\" and \"\\s\"'\n",
}
"""A string with an invalid escape, which the parser warns of; and a string holding one, which the reader parses as
code when it reads the names a string mentions."""
CASES = pytest.mark.parametrize("path, text", list(WARNED.items()), ids=["an invalid escape", "a string holding one"])


def project(root: Path, path: str, text: str) -> Path:
    for folder in ("app", "app/kernel"):
        (root / folder).mkdir(exist_ok=True)
        (root / folder / "__init__.py").write_text("")
    (root / path).write_text(text)
    (root / "pyproject.toml").write_text('[tool.xarch]\nprofile = "cli"\n')
    return root


@CASES
def test_check_run_as_a_program_prints_nothing_on_stderr_for_a_file_the_parser_warns_of(tmp_path, path, text):
    done = subprocess.run([sys.executable, "-W", "default", "-m", "xarch", "check"], cwd=project(tmp_path, path, text),
                          capture_output=True, text=True,
                          env={"PYTHONPATH": str(Path(__file__).resolve().parents[2]), "PATH": ""})
    assert done.stdout and done.stderr == ""


@CASES
def test_check_raises_no_warning_of_the_parser(tmp_path, monkeypatch, path, text):
    monkeypatch.chdir(project(tmp_path, path, text))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        CliRunner().invoke(app, ["check"])
    assert [str(w.message) for w in caught if issubclass(w.category, SyntaxWarning)] == []
