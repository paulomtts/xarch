"""What a part of a bundled profile, or of xarch's own, may import, must import and may import from outside stays what
it was before the part's import keys moved into one `imports` group: `where` says the same of a file of every part of
xarch's own profile, and the rules the keys expand to are, as checks, the same text for each profile but for the key."""
import hashlib
import json

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()
KEYS = {"may": "parts.imports.may", "must": "parts.imports.must", "libraries": "parts.imports.libraries"}
"""The address `profile explain` is asked for each key of the group."""
PATHS = {"domain": "xarch/modules/spec/domain/x.py", "logic": "xarch/modules/spec/application/logic/x.py",
         "ports": "xarch/modules/spec/application/ports/x.py",
         "services": "xarch/modules/spec/application/services/x.py",
         "controller": "xarch/modules/spec/application/controller.py", "adapters": "xarch/modules/spec/adapters/x.py",
         "platform": "xarch/platform/x.py", "cli": "xarch/cli/x.py", "reports": "xarch/cli/reports/x.py",
         "main": "xarch/__main__.py", "bootstrap": "xarch/bootstrap/x.py",
         "contract": "xarch/modules/spec/contract/x.py", "profile-values": "xarch/profile_values/x.py",
         "kernel-logic": "xarch/kernel/logic/x.py", "kernel": "xarch/kernel/x.py"}
"""One path of each part of xarch's own profile."""
WHERE = {
    "domain": ("its own module's `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "logic": ("its own module's `application/logic/` and `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "ports": ("its own module's `application/ports/` and `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "services": ("its own module's `application/services/`, `application/logic/`, `domain/`, `application/ports/` and "
                 "`contract/`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "controller": ("its own module's `application/controller.py`, `application/services/`, `contract/` and "
                   "`domain/errors`, `kernel/`, `kernel/logic/`, `profile_values/`", []),
    "adapters": ("its own module's `adapters/`, `application/ports/` and `domain/`, `kernel/`, `kernel/logic/`, "
                 "`profile_values/`, `platform/`, any module's `contract/`", ["ast", "tokenize"]),
    "platform": ("`platform/`, `kernel/`, `kernel/logic/`", ["yaml"]),
    "cli": ("`cli/`, `cli/reports/`, any module's `application/controller.py` and `contract/`, `kernel/`, "
            "`kernel/logic/`", ["typer"]),
    "reports": ("`cli/reports/`, any module's `contract/`, `kernel/`, `kernel/logic/`", []),
    "main": ("`__main__.py`, `bootstrap/`", []),
    "bootstrap": ("everything", []),
    "contract": ("its own module's `contract/`, `domain/values:*Id` and `domain/published`, `kernel/`, `kernel/logic/`, "
                 "`profile_values/`", []),
    "profile-values": ("`profile_values/`, `kernel/`", []),
    "kernel-logic": ("`kernel/logic/`, `kernel/`, `profile_values/`", []),
    "kernel": ("`kernel/`", []),
}
"""What `where` said of each part before the change: may_import_text and libraries."""
RULES = {
    ("cli", "may"): (12, "56c3045d340f9998"), ("cli", "must"): (1, "3a6fe3a7e4628850"),
    ("cli", "libraries"): (24, "530c3c0c9fe79616"),
    ("web", "may"): (12, "0f4747306974eadd"), ("web", "must"): (1, "3a6fe3a7e4628850"),
    ("web", "libraries"): (24, "482cc8c560189bf3"),
    ("architecture.yaml", "may"): (15, "55bbcc7bd4a5acdd"), ("architecture.yaml", "must"): (1, "3a6fe3a7e4628850"),
    ("architecture.yaml", "libraries"): (30, "5a45f6bcb3e80741"),
}
"""For each profile and key of the group: how many rules it expands to, and the first 16 hex digits of the SHA-256 of
their checks text before the change."""


def explained(key: str, profile: str) -> tuple[int, str]:
    found = json.loads(runner.invoke(app, ["profile", "explain", KEYS[key], "--rule", "--profile", profile,
                                           "--format", "json"]).output)
    text = found["checks"].replace(".imports.libraries)", ".libraries)")
    return found["rules"], hashlib.sha256(text.encode()).hexdigest()[:16]


@pytest.mark.parametrize("part", list(PATHS))
def test_where_says_what_each_part_of_xarch_may_import_as_before(part):
    found = json.loads(runner.invoke(app, ["where", PATHS[part], "--format", "json"]).output)
    assert found["part"]["name"] == part
    assert (found["may_import_text"], found["libraries"]) == WHERE[part]


@pytest.mark.parametrize("profile, key", list(RULES))
def test_each_key_of_the_group_expands_to_the_rules_of_before(profile, key):
    assert explained(key, profile) == RULES[profile, key]
