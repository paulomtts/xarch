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
from xarch.profile_values.testing import Place, RowId, TableForm

SOURCE = "layered.yaml"
PYTEST_TABLE = {"decorator": "pytest.mark.parametrize", "columns_from": {"position": 0, "keyword": "argnames"},
                "rows": {"position": 1, "keyword": "argvalues"}, "row": "pytest.param", "id": {"keyword": "id"}}
"""The one form pytest writes a table of cases in, as an entry of `testing.tables`."""
PYTEST_FORM = TableForm(Place(0, "argnames"), Place(1, "argvalues"), ("pytest", "param"), RowId(keyword="id"),
                        decorator=("pytest", "mark", "parametrize"))
"""PYTEST_TABLE as the loader reads it."""
TESTING = {"files": ["test_*.py", "*_test.py"], "declared": [{"function": "test_*"}], "skips": ["pytest.mark.skip", "pytest.skip"],
           "tables": [PYTEST_TABLE],
           "mocks": {"calls": ["unittest.mock.Mock", "unittest.mock.MagicMock"],
                     "autospec": ["unittest.mock.create_autospec"],
                     "specs": [{"keyword": "spec"}, {"keyword": "spec_set"}, {"position": 0}],
                     "fixtures": {"mocker": {"calls": ["Mock", "MagicMock"], "autospec": ["create_autospec"]}}}}
PRESETS = {"pytest": TESTING}
LANGUAGES = {"python": PYTHON}
EX = {"ex": ("tests/src/billing/service/test_rules.py", "tests/src/billing/builders.py", "tests/checks/rules/test_x.py")}
"""The files of one example project, by its folder: what the listing holds for `docs.examples: [ex]`."""


def layered(**changes) -> dict:
    """A profile with no tiers and no tests; the keys given are added or replaced."""
    return {
        "name": "layered",
        "parts": {
            "src/<module>/": {
                "api/": {"role": "HTTP handlers", "imports": {"may": ["module.service"]}},
                "service/": {"role": "business logic", "imports": {"may": ["module.store", "parts.shared"]}},
                "store/": {"role": "database access", "imports": {"may": ["parts.shared"], "libraries": ["sqlmodel"]}},
            },
            "shared/": {"role": "shared code"},
        },
    } | changes


def two_folders(**changes) -> dict:
    """layered(), with a second repeating folder, ext/<plugin>/, holding a hooks folder and a manifest.py file."""
    document = layered()
    document["parts"]["ext/<plugin>/"] = {"hooks/": {"role": "what a plugin runs"},
                                          "manifest.py": {"role": "what a plugin declares",
                                                          "imports": {"may": ["plugin.hooks"]}}}
    return document | changes


def covered(**changes) -> dict:
    """layered(), with the test framework, a unit and an integration tier, and every part in a tier or untested."""
    document = layered(testing=deepcopy(TESTING),
                       tiers={"unit": {"proves": "a rule", "litmus": "Does it decide?\nIf yes, it is a unit test.\n"},
                              "integration": {"proves": "a request", "litmus": "Does it need the database?"}})
    for name, tier in (("api", "integration"), ("service", "unit"), ("store", "integration")):
        part_of(document, name)["tests"] = tier
    part_of(document, "shared")["untested"] = "reached through the parts that use it"
    return document | changes


def part_of(document: dict, name: str) -> dict:
    """The map of the part named name in the document's folder tree: the folder or file whose `name` is name, else
    whose last step, or whose file name before the first dot, is."""
    found = _part_in(document["parts"], name)
    assert found is not None, f"no part {name!r} in the tree"
    return found


def _part_in(node: dict, name: str) -> dict | None:
    for key, value in node.items():
        if not isinstance(key, str) or not (key.endswith("/") or "." in key) or not isinstance(value, dict):
            continue
        last = key.rstrip("/").split("/")[-1]
        given = last if key.endswith("/") else last.split(".")[0]
        if value.get("name", given) == name and any(not (k.endswith("/") or "." in k) for k in value):
            return value
        deeper = _part_in(value, name)
        if deeper is not None:
            return deeper
    return None


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
