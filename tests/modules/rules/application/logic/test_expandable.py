"""Whether a key is one the engine expands to rules when a profile sets it, for a key a profile sets nowhere."""
import pytest

from xarch.modules.rules.application.logic.expandable import expands
from xarch.modules.rules.application.logic.expansion import KEYS, book
from xarch.modules.rules.application.logic.explained import general
from xarch.modules.rules.domain.values import PartInfo, Profile
from xarch.profile_values.placement import Target
from xarch.profile_values.testing import Fakes, Framework
from xarch.profile_values.tiers import CheckedTier

EVERY_KEY = Profile(
    parts={"one": ("one",), "two": ("two",)}, rules={"one": (Target("two"),), "two": ()},
    libraries={"one": ("outside",)}, forbidden={"one": (("outside",),)},
    tiers=(CheckedTier("tier", (Target("one"),), ("tier",), types_only=("two",), forbidden=True,
                       may_import=(Target("two"),), must_import=("two",)),),
    package_only=("two",), types_only={"one": ("two",)}, no_callbacks=("one",), names={"one": ("*",)},
    built_by={"two": ("one",)}, private_imports=True, no_comments=True, closed_tree=True, holds={"one": "classes"},
    immutable=("two",), must_import={"one": (Target("two"),)}, dead_code=True, untested=True, tests_only=True,
    pass_through=("one",), fakes=Fakes(("fakes",), ("two",)), framework=Framework(("*",), "*"),
    info={"one": PartInfo(), "two": PartInfo()})
"""A profile of two parts and a tier that sets every key the engine expands."""


@pytest.mark.parametrize("address, expected", [
    pytest.param("parts.types_only", True, id="a key of every part the engine expands"),
    pytest.param("parts.services.types_only", True, id="the same key of one part"),
    pytest.param("tiers.unit.types_only", True, id="a key of a tier"),
    pytest.param("guards.no-comments", True, id="a guard the engine runs"),
    pytest.param("guards.no-twins", False, id="a guard a check of xarch's own runs"),
    pytest.param("parts.path", False, id="a key of the layout"),
    pytest.param("docs", False, id="a key of the docs"),
])
def test_a_key_is_expandable_when_the_engine_expands_it_once_set(address, expected):
    assert expands(address) is expected


def test_the_keys_the_engine_expands_are_those_the_rules_of_a_profile_setting_them_all_are_keyed_by():
    keys = [general(key.strip()) for rules in book(EVERY_KEY).values() for rule in rules for key in rule.key.split(";")
            if rule.key]
    assert tuple(dict.fromkeys(keys)) == KEYS
