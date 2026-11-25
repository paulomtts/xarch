"""Whether a key is one the engine expands to rules when a profile sets it, for a key a profile sets nowhere."""
import pytest

from xarch.modules.rules.application.logic.expandable import expands
from xarch.modules.rules.application.logic.expansion import KEYS, book
from xarch.modules.rules.application.logic.explained import general
from xarch.modules.rules.domain.profile import PartInfo, Profile
from xarch.profile_values.placement import Target
from xarch.profile_values.testing import Fakes, Framework
from xarch.profile_values.tiers import CheckedTier

EVERY_KEY = Profile(
    parts={"one": ("one",), "two": ("two",)}, rules={"one": (Target("two"),), "two": ()},
    imports_libraries={"one": ("outside",)}, uses_never={"one": (("outside",),)},
    tiers=(CheckedTier("tier", (Target("one"),), ("tier",), imports_types_only=("two",), apply_never=True,
                       imports_may=(Target("two"),), imports_must=("two",), imports_also=(Target("two"),)),),
    package_only=("two",), imports_types_only={"one": (Target("two"),)}, no_callbacks=("one",),
    holds_names={"one": {"classes": ("*",)}, "two": {"functions": ("*",), "records": ("*",), "exceptions": ("*",)}},
    holds_built_by={"two": ("one",)}, private_imports=True, no_comments=True, closed_tree=True,
    holds={"one": ("classes",), "two": ("functions", "records", "exceptions")},
    holds_immutable={"one": ("classes",), "two": ("records",)}, imports_must={"one": (Target("two"),)}, dead_code=True,
    untested=True, tests_only=True,
    pass_through=("one",), fakes=Fakes(("fakes",), ("two",)), framework=Framework(("*",), "*"),
    info={"one": PartInfo(), "two": PartInfo()})
"""A profile of two parts and a tier that sets every key the engine expands."""


@pytest.mark.parametrize("address, expected", [
    pytest.param("parts.imports.may.types_only", True, id="a key of every part the engine expands"),
    pytest.param("parts.services.imports.may.types_only", True, id="the same key of one part"),
    pytest.param("tiers.unit.imports.types_only", True, id="a key of a tier"),
    pytest.param("guards.no-comments", True, id="a guard the engine runs"),
    pytest.param("guards.no-callbacks", True, id="the guard no-callbacks"),
    pytest.param("parts.no_callbacks", False, id="the part key no_callbacks, retired"),
    pytest.param("parts.holds", True, id="holds"),
    pytest.param("parts.services.holds.classes.names", True, id="the names of the classes of one part"),
    pytest.param("parts.holds.functions.names", True, id="the names of functions"),
    pytest.param("parts.holds.records.immutable", True, id="immutable of records"),
    pytest.param("parts.holds.classes.built_by", True, id="built_by of classes"),
    pytest.param("parts.holds.classes", False, id="a kind, which presence reads through holds"),
    pytest.param("parts.names", False, id="the part key names, retired"),
    pytest.param("parts.immutable", False, id="the part key immutable, retired"),
    pytest.param("parts.built_by", False, id="the part key built_by, retired"),
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


def test_the_keys_of_the_kinds_of_holds_are_in_the_order_of_the_book():
    assert [key for key in KEYS if key.startswith("parts.holds")] == [
        "parts.holds.classes.names", "parts.holds.functions.names", "parts.holds.records.names",
        "parts.holds.exceptions.names", "parts.holds.classes.built_by", "parts.holds", "parts.holds.classes.immutable",
        "parts.holds.records.immutable"]
    assert general("parts.services.holds.classes.names") == "parts.holds.classes.names"


def test_the_keys_of_the_group_are_expanded_and_the_old_part_keys_are_not():
    assert all(expands(key) for key in ("parts.imports.may", "parts.imports.must", "parts.imports.libraries",
                                        "parts.imports.may.types_only", "parts.services.imports.may.types_only"))
    assert not any(expands(key) for key in ("parts.may_import", "parts.must_import", "parts.libraries",
                                            "parts.types_only"))
    assert expands("tiers.imports.types_only") and expands("tiers.imports.must")
    assert {"parts.imports.may", "parts.imports.libraries", "parts.imports.must", "parts.imports.may.types_only"} <= set(KEYS)
    assert not {"parts.may_import", "parts.libraries", "parts.must_import", "parts.types_only"} & set(KEYS)


def test_the_keys_of_a_tier_s_group_are_expanded_and_the_old_tier_keys_are_not():
    assert all(expands(key) for key in ("tiers.imports.also", "tiers.imports.types_only", "tiers.imports.must",
                                        "tiers.unit.imports.must"))
    assert not any(expands(key) for key in ("tiers.may_also_import", "tiers.types_only", "tiers.must_import"))
    assert {"tiers.imports.also", "tiers.imports.types_only", "tiers.imports.must"} <= set(KEYS)
    assert not {"tiers.may_also_import", "tiers.types_only", "tiers.must_import"} & set(KEYS)
