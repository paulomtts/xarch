"""Builders for the spec module's tests of tiers: an architecture document with a repeating src/<module>/ folder
(api, service, store), a shared/ part no tier tests, and two tiers, each argument defaulted so a test names only
what it cares about; and how a document is parsed, or rejected with its problems."""
from __future__ import annotations

import pytest

from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Architecture

SOURCE = "layered.yaml"


def layered_tiers(*tiers: dict, **parts: dict) -> dict:
    """The document, with the tiers given (unit and integration if none) and the parts given added or replaced."""
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"api": {}, "service": {}, "store": {}}}, "shared": {}},
        "parts": {"api": {"path": "src/*/api", "role": "HTTP handlers"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "store": {"path": "src/*/store", "role": "database access"},
                  "shared": {"path": "shared", "role": "shared code",
                             "untested": "reached through the parts that use it"}} | parts,
        "rules": {},
        "tests": {"files": ["test_*.py"], "functions": "test_*"},
        "tiers": list(tiers) or [unit(), integration()],
    }


def unit(**extra) -> dict:
    return {"name": "unit", "subject": ["service", "service/rules"], "proves": "a rule", "may_touch": "nothing",
            "litmus": "Does it decide?\nIf yes, it is a unit test.\n"} | extra


def integration(**extra) -> dict:
    return {"name": "integration", "subject": ["api", "store"], "proves": "a request", "may_touch": "the database",
            "litmus": "Does it need the database?"} | extra


def tiered() -> dict:
    """The document whose tiers carry every text and an example each."""
    example = {"path": "tests/src/billing/service/test_rules.py", "file": "x/unit.py", "note": " (one per rule)"}
    return layered_tiers(
        unit(one_file_per="rule", cases_from="the invariants", data="built in the test", example=example),
        integration(subject_text="`src/` but `service/`", one_file_per="route", cases_from="its arguments",
                    data="the seed", example={"path": "tests/src/test_api.py", "file": "x/integration.py"}))


def parsed(document: dict, has_file=lambda relative: True) -> Architecture:
    return parse_architecture(document, SOURCE, has_file)


def problems(document: dict, has_file=lambda relative: True) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        parsed(document, has_file)
    return list(caught.value.problems)
