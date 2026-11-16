"""How a custom profile is looser than a bundled one, on hand-made architectures: a rule's target is shown as the file
writes it."""
from dataclasses import replace

import pytest

from tests.modules.spec.application.origins import BASE, PARTS, TESTING, TIER
from tests.modules.spec.profiles_v2 import layered, parsed
from xarch.modules.spec.application.logic.looseness import closest, looser, sentence


@pytest.mark.parametrize("target, shown", [
    pytest.param("service", "service", id="a part in the repeating folder is shown by its bare name, which means its own instance"),
    pytest.param("store@any/sql", "store@any/sql", id="a scope and a sub path are both shown"),
    pytest.param("shared/text", "shared/text", id="a part outside the repeating folder has no scope"),
    pytest.param("everything", "everything", id="everything is shown as the word"),
    pytest.param("api@any", "api@any", id="another instance of the part itself is looser than its own, which is implied"),
])
def test_a_target_added_to_a_rule_is_shown_as_written(target, shown):
    custom = layered()
    custom["parts"]["api"]["may_import"] = target if target == "everything" else [target]
    stricter = layered()
    stricter["parts"]["api"]["may_import"] = []
    assert looser(parsed(custom), parsed(stricter)) == [("may_import", "api", shown)]


def test_the_bundled_profile_a_profile_says_it_is_based_on_wins_over_the_one_sharing_most_parts():
    full = parsed(layered())
    bundled = {"alpha": full, "beta": replace(full, parts={"api": full.parts["api"]})}
    mine = replace(full, parts={name: full.parts[name] for name in ("api", "store")})
    assert closest(mine, bundled) == "alpha"
    assert closest(replace(mine, based_on="beta"), bundled) == "beta"


@pytest.mark.parametrize("looser, said", [
    pytest.param(("may_import", "domain", "platform"),
                 "domain may also import platform (parts.domain.may_import)", id="a rule target added"),
    pytest.param(("libraries", "", ""), "outside packages are not checked", id="libraries switched off"),
    pytest.param(("libraries", "web", "requests"), "web may also import requests (parts.web.libraries)",
                 id="a package added"),
    pytest.param(("libraries", "web", "*"), "web may import any outside package (parts.web.libraries)",
                 id="a part left unchecked"),
    pytest.param(("forbidden", "domain", "time.time"),
                 "domain no longer forbids time.time (parts.domain.forbidden)", id="a forbidden name dropped"),
    pytest.param(("must_import", "adapters", "contract@any"),
                 "adapters may also meet must_import with contract@any (parts.adapters.must_import)",
                 id="a must_import target added"),
    pytest.param(("must_import", "adapters"), "adapters no longer has to import anything "
                                                      "(parts.adapters.must_import)", id="must_import dropped"),
    pytest.param(("untested", "platform"), "platform is newly marked untested (parts.platform.untested)",
                 id="a part marked untested"),
    pytest.param(("litmus", "cli"),
                 "cli has no litmus, though the profile it is compared with gives it one (parts.cli.litmus)",
                 id="a litmus dropped"),
    pytest.param(("types_only", "rendering", "controller"),
                 "the rendering tests may now call controller (tiers.rendering.types_only)",
                 id="a types-only part dropped"),
    pytest.param(("apply_forbidden", "unit"),
                 "the unit tests are no longer held to their part's forbidden list (tiers.unit.apply_forbidden)",
                 id="a tier's forbidden dropped"),
    pytest.param(("testing.skips", "", "pytest.skip"),
                 "pytest.skip is no longer counted as a skip (testing.skips)", id="a skip dropped"),
    pytest.param(("files.pinned", "", "tests/test_rules.py"),
                 "tests/test_rules.py is no longer pinned (files.tests/test_rules.py.pinned)",
                 id="an init file unpinned"),
    pytest.param(("reserved", "", "ast"), "ast is no longer reserved (reserved.ast)", id="a reserved name dropped"),
    pytest.param(("other", "", "x"), "other x", id="a key it does not know is said by its words"),
])
def test_sentence(looser, said):
    assert sentence(*looser) == said


def test_every_way_a_profile_is_looser_than_another_is_found_in_order():
    parts = {**PARTS, "core": {**PARTS["core"], "may_import": ["store"], "libraries": ["yaml"]},
             "store": {"path": "store", "role": "storage", "may_import": ["core"],
                       "libraries": ["sqlmodel", "requests"], "untested": "trust me"}}
    custom = {**BASE, "parts": parts, "forbidden": {"pure": ["socket"]},
              "tiers": {"unit": {key: value for key, value in TIER.items() if key != "types_only"}
                        | {"apply_forbidden": False}},
              "testing": {**TESTING, "skips": ["pytest.mark.skip"]}, "guards": {},
              "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    assert looser(parsed(custom), parsed(BASE)) == [
        ("may_import", "core", "store"), ("libraries", "core", "yaml"), ("libraries", "store", "requests"),
        ("forbidden", "core", "time.time"), ("untested", "store", ""), ("types_only", "unit", "store"),
        ("apply_forbidden", "unit", ""), ("testing.skips", "", "pytest.mark.xfail"),
        ("files.pinned", "", "tests/test_rules.py")]


def test_a_name_the_base_reserves_and_the_custom_profile_does_not_is_looser():
    base = parsed(layered(reserved={"ast": "the reader's", "json": "the store's"}))
    assert looser(parsed(layered(reserved={"json": "mine"})), base) == [("reserved", "", "ast")]
    assert looser(parsed(layered(reserved={"ast": "the reader's", "json": "the store's", "csv": "x"})), base) == []


def test_a_part_redefined_without_the_litmus_the_base_gives_it_is_looser_and_one_the_base_gives_none_is_not():
    base = layered()
    base["parts"]["api"]["litmus"] = "Does it answer a request?"
    custom = layered()
    custom["parts"]["store"]["litmus"] = "Does it keep a record?"
    assert looser(parsed(custom), parsed(base)) == [("litmus", "api", "")]
    assert looser(parsed(base), parsed(base)) == []
