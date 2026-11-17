"""Builders for the spec module's tests of profiles: a profile with a repeating src/<module>/ folder (api,
service, store) and a shared/ part, each document built afresh so a test changes its own copy;
and how a document is parsed, or rejected with its problems."""
from __future__ import annotations

from collections.abc import Collection, Mapping
from copy import deepcopy

import pytest

from tests.modules.spec.languages import PYTHON
from xarch.modules.spec.application.logic.profile_listing import listing, referenced
from xarch.modules.spec.application.logic.profile_parsing import parse_profile
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Architecture

SOURCE = "layered.yaml"
TESTING = {"files": ["test_*.py", "*_test.py"], "functions": "test_*", "skips": ["pytest.mark.skip", "pytest.skip"],
           "table": {"decorator": "pytest.mark.parametrize", "row": "pytest.param", "id": "id",
                     "keywords": ["argnames", "argvalues"]},
           "mocks": {"calls": ["unittest.mock.Mock", "unittest.mock.MagicMock"],
                     "autospec": ["unittest.mock.create_autospec"], "spec_keywords": ["spec", "spec_set"],
                     "spec_position": 0, "fixtures": {"mocker": {"calls": ["Mock", "MagicMock"], "autospec": ["create_autospec"]}}}}
PRESETS = {"pytest": TESTING}
LANGUAGES = {"python": PYTHON}
EX = {"ex": ("tests/src/billing/service/test_rules.py", "tests/src/billing/builders.py", "tests/checks/rules/test_x.py")}
"""The files of one example project, by its folder: what the listing holds for `docs.examples: [ex]`."""


def layered(**changes) -> dict:
    """A profile with no tiers and no tests; the keys given are added or replaced."""
    return {
        "name": "layered",
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


def listed(document: dict, files: Collection[str] | None = None, folders: Mapping[str, tuple[str, ...]] | None = None,
           missing: Collection[str] = ()) -> tuple[str, ...]:
    """The listing the loader reads: the files given, or else every file the document names, but those missing, and
    every file of each folder in folders."""
    named = referenced(document)[0] if files is None else files
    return listing((name for name in named if name not in missing), folders or {})


def parsed(document: dict, files: Collection[str] | None = None, presets=PRESETS, bundled=("cli", "web"),
           folders: Mapping[str, tuple[str, ...]] | None = None, missing: Collection[str] = (),
           languages=LANGUAGES) -> Architecture:
    return parse_profile(document, SOURCE, listed(document, files, folders, missing), presets, bundled, languages)


def problems(document: dict, files: Collection[str] | None = None, presets=PRESETS, bundled=("cli", "web"),
             folders: Mapping[str, tuple[str, ...]] | None = None, missing: Collection[str] = (),
             languages=LANGUAGES) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        parsed(document, files, presets, bundled, folders, missing, languages)
    return list(caught.value.problems)
