"""Builders for the tests of converting a profile of format 1: a layered profile of format 1, the same with tiers, and
its conversion with the files next to it given as data."""
from copy import deepcopy

from xarch.modules.spec.application.logic.migrate_examples import referenced_v1
from xarch.modules.spec.application.logic.migrate_profile import Converted, convert
from xarch.modules.spec.application.logic.profile_listing import listing

KIT = {"files": ["test_*.py"], "functions": "test_*"}


def old(**changes) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"api": {}, "service": {}}}, "shared": {}},
        "parts": {"api": {"path": "src/*/api", "role": "HTTP handlers"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "shared": {"path": "shared", "role": "shared code"}},
        "rules": {"api": ["service@own"], "service": ["shared"], "shared": []},
    } | changes


def tiered(**changes) -> dict:
    return old(tests=deepcopy(KIT), tiers=[
        {"name": "unit", "subject": ["service", "shared"], "proves": "a rule", "may_touch": "nothing",
         "litmus": "Does it decide?\n"},
        {"name": "integration", "subject": ["api"], "proves": "a request", "may_touch": "the database",
         "litmus": "Does it need the database?"}]) | changes


def made(document: dict, files: dict[str, tuple[str, ...]] | None = None, presets=None,
         missing: frozenset[str] | set[str] = frozenset()) -> Converted:
    """The conversion, with every file the document names next to it but those missing, and the folders in files."""
    named = referenced_v1(document)[0]
    return convert(document, "layered.yaml", presets or {},
                   listing((name for name in named if name not in missing), files or {}), "python")
