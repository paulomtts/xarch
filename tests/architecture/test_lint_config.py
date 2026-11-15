"""The linter config: xarch's own is the one the bundled profiles write, except for what only this repository needs."""
import tomllib
from pathlib import Path

import xarch

REPOSITORY = Path(xarch.__file__).parent.parent
TEMPLATE = Path(xarch.__file__).parent / "architectures" / "lint.toml"
EXCLUDE = (
    "# Only here: the bundled examples are reference snippets without their imports, and .claude/ holds agents' worktrees:\n"
    "# neither is linted, even when a path is named.\n"
    'extend-exclude = [".claude", "xarch/architectures/examples"]\n'
    "force-exclude = true\n"
)


def test_the_repository_config_is_the_template_plus_the_exclusion_of_the_reference_snippets():
    template = TEMPLATE.read_text()
    marker = 'line-length = 140\n'
    expected = template.replace(marker, marker + "\n" + EXCLUDE)
    assert (REPOSITORY / "ruff.toml").read_text() == expected


def test_the_template_selects_what_the_profiles_rely_on():
    lint = tomllib.loads(TEMPLATE.read_text())["lint"]
    assert {"E", "F", "I", "TID252", "ANN201", "PT", "T20", "DTZ", "RUF100"} <= set(lint["select"])
    assert lint["flake8-pytest-style"]["parametrize-names-type"] == "csv"
