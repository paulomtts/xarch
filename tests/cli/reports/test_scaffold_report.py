"""How `xarch init` and `xarch new` show what they did, on a hand-made ReportView, and why `new` refuses."""
from pathlib import Path

import pytest

from xarch.cli.reports.scaffold_report import refused_reason, report_lines
from xarch.modules.scaffold.contract import KindIsAFolder, NotInitialized, ReportView


def test_the_report_says_a_line_per_file_created_then_updated_then_skipped():
    report = ReportView(created=[Path("app/a.py")], skipped=[Path("app/c.py")], updated=[Path("pyproject.toml")])
    assert report_lines(report) == ["created app/a.py", "updated pyproject.toml", "skipped app/c.py"]


@pytest.mark.parametrize("refused, reason", [
    pytest.param(KindIsAFolder("modules/", "module"), "no kind 'modules/' in the profile: that is the folder of the kind "
                 "module: write `xarch new module <name>`", id="the folder of a kind says the command with its word"),
    pytest.param(NotInitialized(Path("app/modules")), "app/modules does not exist: run 'xarch init' first",
                 id="an app with no skeleton says to build it first"),
])
def test_why_new_refuses_says_what_to_type(refused, reason):
    assert refused_reason(refused) == reason
