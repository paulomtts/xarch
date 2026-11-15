"""How `xarch init` and `xarch new` show what they did, on a hand-made Report."""
from pathlib import Path

from xarch.cli.reports.scaffold_report import report_lines
from xarch.modules.scaffold.contract import Report


def test_the_report_says_a_line_per_file_created_then_updated_then_skipped():
    report = Report(created=[Path("app/a.py")], skipped=[Path("app/c.py")], updated=[Path("pyproject.toml")])
    assert report_lines(report) == ["created app/a.py", "updated pyproject.toml", "skipped app/c.py"]
