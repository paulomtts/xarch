"""Builders for the spec module's tests of profile format 2: a profile with a repeating src/<module>/ folder (api,
service, store) and a shared/ part, written in format 2, each document built afresh so a test changes its own copy;
and how a document is parsed, or rejected with its problems."""
from __future__ import annotations

from copy import deepcopy

import pytest

from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.profile_v2 import parse_v2
from xarch.modules.spec.domain.values import Architecture

SOURCE = "layered.yaml"
TESTING = {"files": ["test_*.py", "*_test.py"], "functions": "test_*", "skips": ["pytest.mark.skip", "pytest.skip"],
           "table": {"decorator": "pytest.mark.parametrize", "row": "pytest.param", "id": "id",
                     "keywords": ["argnames", "argvalues"]},
           "mocks": {"calls": ["unittest.mock.Mock", "unittest.mock.MagicMock"],
                     "autospec": ["unittest.mock.create_autospec"], "spec_keywords": ["spec", "spec_set"],
                     "fixtures": {"mocker": {"calls": ["Mock", "MagicMock"], "autospec": ["create_autospec"]}}}}
PRESETS = {"pytest": TESTING}
EX = {"ex": ("tests/src/billing/service/test_rules.py", "tests/src/billing/builders.py", "tests/checks/rules/test_x.py")}
"""The files of one example project, by its folder: what folder_files answers for `docs.examples: [ex]`."""


def layered(**changes) -> dict:
    """A profile in format 2 with no tiers and no tests; the keys given are added or replaced."""
    return {
        "xarch": 2, "name": "layered",
        "parts": {
            "api": {"path": "src/<module>/api", "role": "HTTP handlers", "may_import": ["service"]},
            "service": {"path": "src/<module>/service", "role": "business logic", "may_import": ["store", "shared"]},
            "store": {"path": "src/<module>/store", "role": "database access", "may_import": ["shared"],
                      "libraries": ["sqlmodel"]},
            "shared": {"path": "shared", "role": "shared code"},
        },
    } | changes


def two_folders(**changes) -> dict:
    """layered(), with a second repeating folder, ext/<plugin>/, holding a hooks folder and a manifest.py file."""
    document = layered()
    document["parts"]["hooks"] = {"path": "ext/<plugin>/hooks", "role": "what a plugin runs"}
    document["parts"]["manifest"] = {"path": "ext/<plugin>/manifest.py", "role": "what a plugin declares",
                                     "may_import": ["hooks"]}
    return document | changes


def covered(**changes) -> dict:
    """layered(), with the test framework, a unit and an integration tier, and every part in a tier or untested."""
    document = layered(testing=deepcopy(TESTING),
                       tiers={"unit": {"proves": "a rule", "litmus": "Does it decide?\nIf yes, it is a unit test.\n"},
                              "integration": {"proves": "a request", "litmus": "Does it need the database?"}})
    for name, tier in (("api", "integration"), ("service", "unit"), ("store", "integration")):
        document["parts"][name]["tier"] = tier
    document["parts"]["shared"]["untested"] = "reached through the parts that use it"
    return document | changes


def parsed(document: dict, has_file=lambda relative: True, presets=PRESETS, bundled=("cli", "web"),
           folder_files=None) -> Architecture:
    return parse_v2(document, SOURCE, has_file, folder_files, presets, bundled)


def problems(document: dict, has_file=lambda relative: True, presets=PRESETS, bundled=("cli", "web"),
             folder_files=None) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        parsed(document, has_file, presets, bundled, folder_files)
    return list(caught.value.problems)
