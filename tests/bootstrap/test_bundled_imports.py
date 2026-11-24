"""What a part, or a tier, of a bundled profile or of xarch's own may import, must import and may import from outside
stays what it was before the import keys moved into `imports` groups: `where` says the same of a file of every part of
xarch's own profile and of a test of each of its tiers, and the rules the keys expand to are, as checks, the same text
for each profile but for the key."""
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
    ("cli", "may"): (12, "b5fb19f749264287"), ("cli", "must"): (1, "3a6fe3a7e4628850"),
    ("cli", "libraries"): (24, "ae1fba4a77503d1a"),
    ("web", "may"): (12, "f06766b1dbdc51b7"), ("web", "must"): (1, "3a6fe3a7e4628850"),
    ("web", "libraries"): (24, "058402903c045a47"),
    ("architecture.yaml", "may"): (15, "0d94a54e9f44405d"), ("architecture.yaml", "must"): (1, "3a6fe3a7e4628850"),
    ("architecture.yaml", "libraries"): (30, "27ee07b82ce0c6a6"),
}
"""For each profile and key of the group: how many rules it expands to, and the first 16 hex digits of the SHA-256 of
their checks text before the change. The rules come in the order of the parts, which became the folder tree's reading
order in 0.3.0 (`contract` after `adapters`, `kernel` before `kernel-logic`): the lines of `may` and `libraries` are the
same as before, and only their order, so only their digests, moved."""
TIER_KEYS = {"types_only": "tiers.imports.types_only", "must": "tiers.imports.must",
             "also": "tiers.imports.also", "tiers": "tiers"}
"""The address `profile explain` is asked for each key of a tier's group that rules are keyed by, and for `tiers`,
whose rule a tier's `also` keys too."""
TIER_RULES = {
    ("cli", "types_only"): (1, "29bdb75af0440d40"), ("cli", "must"): (0, "e3b0c44298fc1c14"),
    ("cli", "also"): (0, "e3b0c44298fc1c14"), ("cli", "tiers"): (3, "07ebde882b66c963"),
    ("web", "types_only"): (1, "29bdb75af0440d40"), ("web", "must"): (0, "e3b0c44298fc1c14"),
    ("web", "also"): (0, "e3b0c44298fc1c14"), ("web", "tiers"): (3, "07ebde882b66c963"),
    ("architecture.yaml", "types_only"): (2, "329ba93378533550"), ("architecture.yaml", "must"): (2, "0083c4a5a67770c5"),
    ("architecture.yaml", "also"): (1, "297bcd04b21ab4d8"), ("architecture.yaml", "tiers"): (3, "07ebde882b66c963"),
}
"""For each profile and key of a tier: how many rules it expands to, and the first 16 hex digits of the SHA-256 of
their checks text before the change."""
TESTS = {"unit": "tests/modules/spec/domain/test_x.py", "integration": "tests/modules/spec/application/test_x.py",
         "wired": "tests/bootstrap/test_x.py", "guard": "tests/architecture/test_x.py",
         "wired, of cli": "tests/cli/test_x.py"}
"""A test of each tier of xarch's own profile, the wired one twice: once below bootstrap/, once mirroring cli/."""
TYPES = ["domain", "logic", "ports", "services", "controller", "adapters", "platform"]
TIER_WHERE = {
    "unit": ("unit", "its own module's `domain/`, `kernel/`, `kernel/logic/`, `profile_values/`", [], "5e0f441d9899ecd1"),
    "integration": ("integration", "its own module's `application/controller.py`, `application/services/`, `contract/` "
                    "and `domain/errors`, `kernel/`, `kernel/logic/`, `profile_values/`, its own module's "
                    "`domain/values`, `domain/profile`, `domain/parsed` and `domain/outcomes`", [], "ae600445e22537b0"),
    "wired": ("wired", "everything", TYPES, "2a05a9860791084b"),
    "guard": ("guard", "everything", TYPES, "4f53cda18c2baa0c"),
    "wired, of cli": ("wired", "`cli/`, `cli/reports/`, any module's `application/controller.py` and `contract/`, "
                      "`kernel/`, `kernel/logic/`", TYPES, "46205533adc1e5b6"),
}
"""What `where` said of each test before the change: its tier, may_import_text, test.types_only, and the first 16 hex
digits of the SHA-256 of its may_import list."""


def explained(address: str, profile: str) -> tuple[int, str]:
    found = json.loads(runner.invoke(app, ["profile", "explain", address, "--rule", "--profile", profile,
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
    assert explained(KEYS[key], profile) == RULES[profile, key]


@pytest.mark.parametrize("test", list(TESTS))
def test_where_says_what_a_test_of_each_tier_of_xarch_may_import_as_before(test):
    found = json.loads(runner.invoke(app, ["where", TESTS[test], "--format", "json"]).output)
    reached = hashlib.sha256(json.dumps(found["may_import"], sort_keys=True).encode()).hexdigest()[:16]
    assert (found["tier"]["name"], found["may_import_text"], found["test"]["types_only"], reached) == TIER_WHERE[test]


@pytest.mark.parametrize("profile, key", list(TIER_RULES))
def test_each_key_of_a_tier_s_group_expands_to_the_rules_of_before(profile, key):
    assert explained(TIER_KEYS[key], profile) == TIER_RULES[profile, key]
