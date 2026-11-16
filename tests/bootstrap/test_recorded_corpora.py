"""The check on xarch's own source at earlier commits, where it found many violations, gives exactly the findings the
hand-written checks gave before they became rules as data: each finding's rule, file, line, message and fix, the
violations in order of file, line and rule, then the weak findings in the order found. The source of a commit is
kept beside this test as data, its Python files and its profile (`corpora/<commit>.tar.xz`, from `git archive
<commit>`).

    7cc6111   its own profile: 90 violations and 111 weak findings
    df537ca   its own profile: 48 violations and 6 weak findings
    7cc6111 + corpora/stress.yaml, xarch's profile with most keys tightened and nothing excluded: 1735 findings
    examples  the example projects the bundled profiles ship, frozen as they were recorded (`corpora/examples.tar.xz`):
              the shared one with each entry's (cli, web) put together as an app and its tests, checked against that
              bundled profile

A failure names the first finding that differs, the one found and the one recorded.

How the findings were recorded, and how to record them again honestly. The oracle is commit 1f6b01b, the parent of
7202168 (where the engine began to run the checks): the last code whose checks are all hand-written. Run it, never the
code under test, on each corpus, as this test does (CheckApp on the unpacked project, strict), and write the findings
as `[kind, rule, file, line, message, fix]` with kind V or W:

    git archive 1f6b01b | tar -x -C <oracle>
    uv run --project <oracle> python -I <a script that calls build_controllers().rules.check_app(CheckApp(...))>

    - A change of wording only (a message or a fix said differently): change the recorded text by a find and replace
      of that sentence, and review the diff line by line. Never dump what the code under test finds.
    - A change of the order only: move the recorded findings' blocks by hand, each block's text and the file's layout
      kept, and show for every file that the findings are the same and only their order differs.
    - A change of what a check finds: extend the oracle by the same change, in its own worktree, and record from it;
      recording from the code under test would make it test itself.
    - A new check, a new key or a new format of profile: add a corpus (a new archive and its findings, or a new
      profile beside stress.yaml). Never edit an archived project or its profile, whose findings were recorded from it.
"""
import json
import lzma
import tarfile
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import AppChecked, CheckApp

CORPORA = Path(__file__).parent / "corpora"


def archived(name: str, into: Path) -> Path:
    """The archive of that name unpacked below into."""
    with tarfile.open(CORPORA / f"{name}.tar.xz") as archive:
        archive.extractall(into, filter="data")
    return into


def findings(project: Path, profile: str, app: str = "xarch") -> list[list]:
    checked = build_controllers().rules.check_app(CheckApp(project / app, profile, project, project / "tests", True))
    assert isinstance(checked, AppChecked)
    return ([["V", v.rule, v.file, v.line, v.message, v.fix] for v in checked.violations]
            + [["W", w.rule, w.file, w.line, w.message, w.fix] for w in checked.enforcement.weak])


def first_difference(found: list[list], recorded: list[list]) -> str:
    """Where two lists of findings first differ, and how, in words; "" when they are the same."""
    for index, (one, other) in enumerate(zip(found, recorded)):
        if one != other:
            return f"finding {index} differs:\n  found:    {one}\n  recorded: {other}"
    if len(found) != len(recorded):
        extra, side = (found, "found") if len(found) > len(recorded) else (recorded, "recorded")
        beyond = extra[min(len(found), len(recorded))]
        return f"{len(found)} found and {len(recorded)} recorded; the first {side} beyond the other: {beyond}"
    return ""


@pytest.mark.parametrize("found, recorded, said", [
    pytest.param([[1], [2]], [[1], [2]], "", id="the same findings differ nowhere"),
    pytest.param([[1], [3]], [[1], [2]], "finding 1 differs:\n  found:    [3]\n  recorded: [2]",
                 id="a finding that differs is named with both sides"),
    pytest.param([[1]], [[1], [2]], "1 found and 2 recorded; the first recorded beyond the other: [2]",
                 id="a finding missing is named"),
])
def test_a_difference_is_said_by_the_first_finding_that_differs(found, recorded, said):
    assert first_difference(found, recorded) == said


@pytest.mark.parametrize("commit", ["7cc6111", "df537ca"])
def test_an_earlier_commit_checked_against_its_own_profile_gives_the_findings_recorded_from_the_old_checks(
        commit, tmp_path):
    project = archived(commit, tmp_path)
    recorded = json.loads((CORPORA / f"{commit}.json").read_text(encoding="utf-8"))["findings"]
    assert first_difference(findings(project, str(project / "architecture.yaml")), recorded) == ""


def test_an_earlier_commit_checked_against_a_tightened_profile_gives_the_findings_recorded_from_the_old_checks(
        tmp_path):
    project = archived("7cc6111", tmp_path)
    with lzma.open(CORPORA / "stress-7cc6111.json.xz", "rt", encoding="utf-8") as file:
        recorded = json.load(file)["findings"]
    assert first_difference(findings(project, str(CORPORA / "stress.yaml")), recorded) == ""


@pytest.mark.parametrize("entry", ["cli", "web"])
def test_the_bundled_examples_put_together_give_the_findings_recorded_from_the_old_checks(entry, tmp_path):
    examples = archived("examples", tmp_path / "examples")
    for example in ("shared", entry):
        for file in (examples / example).rglob("*"):
            relative = file.relative_to(examples / example)
            if file.is_file():
                into = tmp_path / "project" / (relative if relative.parts[0] == "tests" else Path("app") / relative)
                into.parent.mkdir(parents=True, exist_ok=True)
                into.write_bytes(file.read_bytes())
    recorded = json.loads((CORPORA / f"examples-{entry}.json").read_text(encoding="utf-8"))["findings"]
    assert first_difference(findings(tmp_path / "project", entry, "app"), recorded) == ""
