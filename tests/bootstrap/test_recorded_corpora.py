"""The check on xarch's own source at earlier commits, where it found many violations, gives exactly the findings the
hand-written checks gave before they became rules as data: each finding's rule, file, line, message and fix, in the
order found, violations and weak findings alike. The source of a commit is kept beside this test as data, its
Python files and its profile (`corpora/<commit>.tar.xz`, from `git archive <commit>`).

    7cc6111   its own profile: 90 violations and 111 weak findings
    df537ca   its own profile: 48 violations and 6 weak findings
    7cc6111 + corpora/stress.yaml, xarch's profile with most keys tightened and nothing excluded: some 1600
              violations, compared by rule as a count and a digest, and as a whole by a digest of the order

and the example projects the bundled profiles ship, the shared one with each entry's (cli, web) put together as an
app and its tests, checked against that bundled profile.

The findings were recorded once, from the hand-written checks; a change of the engine that changes one fails here.
"""
import hashlib
import json
import tarfile
from pathlib import Path

import pytest

import xarch
from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import AppChecked, CheckApp

CORPORA = Path(__file__).parent / "corpora"
EXAMPLES = Path(xarch.__file__).parent / "architectures" / "examples"


def archived(commit: str, into: Path) -> Path:
    """The source of the commit, unpacked below into."""
    with tarfile.open(CORPORA / f"{commit}.tar.xz") as archive:
        archive.extractall(into, filter="data")
    return into


def findings(project: Path, profile: str, app: str = "xarch") -> list[list]:
    checked = build_controllers().rules.check_app(CheckApp(project / app, profile, project / "tests", True))
    assert isinstance(checked, AppChecked)
    return ([["V", v.rule, v.file, v.line, v.message, v.fix] for v in checked.violations]
            + [["W", w.rule, w.file, w.line, w.message, w.fix] for w in checked.enforcement.weak])


def digest(items: list) -> str:
    return hashlib.sha256(json.dumps(items, ensure_ascii=False).encode()).hexdigest()


@pytest.mark.parametrize("commit", ["7cc6111", "df537ca"])
def test_an_earlier_commit_checked_against_its_own_profile_gives_the_findings_recorded_from_the_old_checks(
        commit, tmp_path):
    project = archived(commit, tmp_path)
    recorded = json.loads((CORPORA / f"{commit}.json").read_text(encoding="utf-8"))["findings"]
    assert findings(project, str(project / "architecture.yaml")) == recorded


def test_an_earlier_commit_checked_against_a_tightened_profile_gives_the_findings_recorded_from_the_old_checks(
        tmp_path):
    project = archived("7cc6111", tmp_path)
    recorded = json.loads((CORPORA / "stress-7cc6111.json").read_text(encoding="utf-8"))
    found = findings(project, str(CORPORA / "stress.yaml"))
    groups: dict[str, list] = {}
    for item in found:
        groups.setdefault(f"{item[0]} {item[1]}", []).append(item)
    assert {key: [len(items), digest(items)] for key, items in groups.items()} == recorded["groups"]
    assert digest(found) == recorded["order"]


@pytest.mark.parametrize("entry", ["cli", "web"])
def test_the_bundled_examples_put_together_give_the_findings_recorded_from_the_old_checks(entry, tmp_path):
    for example in ("shared", entry):
        for file in (EXAMPLES / example).rglob("*"):
            relative = file.relative_to(EXAMPLES / example)
            if file.is_file() and "__pycache__" not in relative.parts:
                into = tmp_path / (relative if relative.parts[0] == "tests" else Path("app") / relative)
                into.parent.mkdir(parents=True, exist_ok=True)
                into.write_bytes(file.read_bytes())
    recorded = json.loads((CORPORA / f"examples-{entry}.json").read_text(encoding="utf-8"))["findings"]
    assert findings(tmp_path, entry, "app") == recorded
