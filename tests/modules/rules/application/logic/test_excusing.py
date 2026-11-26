"""The findings a check of the profile's own accepts (checks.<id>.accepted), on hand-made source files: a finding an
entry names by its file, and by the values of the variables the entry writes, is taken out and named; an entry that
names none is a violation of the check."""
from dataclasses import replace

import pytest

from tests.modules.rules.builders import imp, profile, source
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.excusing import checks
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.application.logic.own_checks import resolved
from xarch.modules.rules.domain.published import Excused
from xarch.profile_values.checks import APP, AcceptedFinding, Quantified, Saying, Scope, WrittenCheck, WrittenTarget

KEY = "checks.no-platform.accepted"
CHECK = WrittenCheck(("import-into-app",), Scope(APP, "kernel"), Quantified("may_not", (WrittenTarget("part", ("platform",)),)),
                     (Saying("{file} imports {target}", "drop it"),))


def sifted(*entries: AcceptedFinding):
    """What the check comes to on kernel/a.py importing platform/db.py and platform/io.py, and kernel/b.py importing
    platform/db.py, with the entries given."""
    files = [source("kernel/a.py", imp(1, "app.platform.db"), imp(2, "app.platform.io")),
             source("kernel/b.py", imp(3, "app.platform.db")), source("platform/db.py"), source("platform/io.py")]
    checked = resolved(profile(written={"no-platform": replace(CHECK, accepted=entries)}))
    return checks(tuple(c.rule for c in checked.checks), facts_of(files, [], checked, "app"), checked)


def entry(file: str, *by: tuple[str, str]) -> AcceptedFinding:
    return AcceptedFinding(tuple(file.split("/")), by, "why")


@pytest.mark.parametrize("entries, kept, excused", [
    pytest.param((), ["app/kernel/a.py:1", "app/kernel/a.py:2", "app/kernel/b.py:3"], [], id="no entry"),
    pytest.param((entry("kernel/a.py"),), ["app/kernel/b.py:3"], ["app/kernel/a.py:1", "app/kernel/a.py:2"],
                 id="every finding of a file"),
    pytest.param((entry("kernel/a.py", ("target", "app.platform.io")),),
                 ["app/kernel/a.py:1", "app/kernel/b.py:3"], ["app/kernel/a.py:2"], id="a finding by a variable"),
])
def test_each_finding_an_entry_names_is_taken_out_and_named(entries, kept, excused):
    found = sifted(*entries)
    assert [f"{item.file}:{item.line}" for item in found.kept] == kept
    assert [f"{item.file}:{item.line}" for item in found.excused] == excused
    assert found.stale == ()


def test_an_accepted_finding_says_what_it_is_and_why():
    (item,) = sifted(entry("kernel/b.py")).excused
    assert item == Excused("no-platform", "app/kernel/b.py", 3, KEY, "app/kernel/b.py imports app.platform.db", "why")


@pytest.mark.parametrize("stale, message", [
    pytest.param(entry("kernel/b.py", ("target", "app.platform.io")),
                 f"{KEY} accepts a finding of kernel/b.py with target app.platform.io, and the check finds none ({KEY})",
                 id="a variable no finding prints"),
    pytest.param(entry("kernel/c.py"), f"{KEY} accepts the findings of kernel/c.py, and the check finds none ({KEY})",
                 id="a file with no finding"),
])
def test_an_entry_that_names_no_finding_is_a_violation_of_the_check(stale, message):
    found = sifted(stale)
    path = "/".join(stale.file)
    assert found.stale == (Violation(f"app/{path}", 0, message, "no-platform", f"drop the entry of {path} from {KEY}",
                                     True),)


def test_an_entry_written_with_the_app_folder_first_is_told_to_write_its_path_below_the_app():
    (item,) = sifted(entry("app/kernel/a.py")).stale
    assert (item.file, item.fix) == (
        "app/app/kernel/a.py", "write the path relative to the app: kernel/a.py, not app/kernel/a.py")
