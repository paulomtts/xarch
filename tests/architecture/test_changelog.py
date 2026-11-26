"""The CHANGELOG leads with the release pyproject.toml gives: its heading is that version with a date, a link compares
it with the release before, its sections keep Keep a Changelog's order, so that breaking changes, when it has any, open
it, and its table of old and new names every key, value and rule id the release retired."""
import re
import tomllib
from datetime import date
from pathlib import Path

from xarch.modules.spec.domain.profile_keys import RETIRED

ROOT = Path(__file__).resolve().parents[2]
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
RELEASE = re.compile(r"^## \[(\d+\.\d+\.\d+)\] - (\d{4}-\d{2}-\d{2})$", re.MULTILINE)
CELL = re.compile(r"(?<!\\)\|")
SECTIONS = ["Breaking changes", "Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]


def latest_release() -> str:
    """The text of the first release headed with a version and a date, up to the next heading of level two."""
    rest = CHANGELOG[RELEASE.search(CHANGELOG).end():]
    following = re.search(r"^## ", rest, re.MULTILINE)
    return rest[:following.start()] if following else rest


def table_rows() -> list[list[str]]:
    """The cells of each row of the first table under the latest release's breaking changes, header and rule aside."""
    breaking = latest_release().partition("### Breaking changes\n")[2].split("\n### ")[0].splitlines()
    first = next((i for i, line in enumerate(breaking) if line.startswith("|")), len(breaking))
    end = next((i for i in range(first, len(breaking)) if not breaking[i].startswith("|")), len(breaking))
    return [CELL.split(row)[1:-1] for row in breaking[first:end][2:]]


def test_the_latest_release_is_the_version_pyproject_gives():
    version, day = RELEASE.search(CHANGELOG).groups()
    assert (version, date.fromisoformat(day).isoformat()) == (VERSION, day)


def test_the_latest_release_has_a_compare_link():
    previous = next(version for version, _ in RELEASE.findall(CHANGELOG) if version != VERSION)
    link = f"[{VERSION}]: https://github.com/paulomtts/xarch/compare/v{previous}...v{VERSION}"
    assert link in CHANGELOG.splitlines()


def test_the_latest_release_keeps_the_order_of_its_sections_breaking_changes_first():
    sections = re.findall(r"^### (.+)$", latest_release(), re.MULTILINE)
    assert sections and set(sections) <= set(SECTIONS)
    assert sections == sorted(sections, key=SECTIONS.index)


def test_every_row_of_the_table_of_old_and_new_has_two_cells():
    rows = table_rows()
    assert bool(rows) is any(VERSION in retired.text for retired in RETIRED)
    assert [row for row in rows if len(row) != 2] == []


def test_every_name_retired_in_this_release_is_in_the_table_of_old_and_new():
    spans = [span for row in table_rows() for span in re.findall(r"`([^`]+)`", row[0])]
    named = [word for retired in RETIRED if VERSION in retired.text
             for word in (retired.name, retired.value) if word]
    missing = {word for word in named if not any(re.search(rf"\b{re.escape(word)}\b", span) for span in spans)}
    assert sorted(missing) == []
