"""How a custom profile is looser than a bundled one, on hand-made architectures, as the origin of the custom one says
it: a rule's target is shown as the file writes it, and each way is said naming the key that says it. The sentence of
each way a profile is looser is asserted here or in tests/modules/spec/application/test_origin.py (a package added to
`libraries`, a part that may import any outside package, a `must_import` target added or the key dropped)."""
from dataclasses import replace

import pytest

from tests.modules.spec.application.origins import BASE, PARTS, TESTING, TIER, part
from tests.modules.spec.profiles_v2 import covered, layered, parsed
from xarch.modules.spec.application.logic.looseness import LOOSER, origin_of
from xarch.modules.spec.domain.published import Loosened
from xarch.modules.spec.domain.values import Architecture


def loosened(custom: Architecture, base: Architecture) -> tuple[Loosened, ...]:
    """Every way custom is looser than base, as the origin of custom, based on base, lists them."""
    return origin_of("mine.yaml", replace(custom, based_on="base"), False, {"base": base}).looser


@pytest.mark.parametrize("written, shown", [
    pytest.param(["service"], "service", id="a part in the repeating folder is shown by its bare name, which means its own instance"),
    pytest.param(["store@any/sql"], "store@any/sql", id="a scope and a sub path are both shown"),
    pytest.param(["shared/text"], "shared/text", id="a part outside the repeating folder has no scope"),
    pytest.param("everything", "everything", id="everything is shown as the word"),
    pytest.param(["api@any"], "api@any", id="another instance of the part itself is looser than its own, which is implied"),
])
def test_a_target_added_to_a_rule_is_shown_as_written(written, shown):
    custom = layered()
    custom["parts"]["api"]["may_import"] = written
    stricter = layered()
    stricter["parts"]["api"]["may_import"] = []
    assert loosened(parsed(custom), parsed(stricter)) == (
        Loosened("may_import", "api", shown, f"api may also import {shown} (parts.api.may_import)"),)


@pytest.mark.parametrize("target", [
    pytest.param("shared/text", id="a folder below a part the bundled profile allows narrows it"),
    pytest.param("shared:*Text", id="a name pattern on a part the bundled profile allows narrows it"),
    pytest.param("store/sql:Sql*", id="a folder and a name pattern below an allowed part narrow it both"),
])
def test_a_target_below_one_the_bundled_profile_allows_is_not_looser(target):
    custom = layered()
    custom["parts"]["service"]["may_import"] = ["store", "shared", target]
    assert loosened(parsed(custom), parsed(layered())) == ()


def test_the_bundled_profile_a_profile_says_it_is_based_on_wins_over_the_one_sharing_most_parts():
    full = parsed(layered())
    bundled = {"alpha": full, "beta": replace(full, parts={"api": full.parts["api"]})}
    mine = replace(full, parts={name: full.parts[name] for name in ("api", "store")})
    assert origin_of("mine.yaml", mine, False, bundled).closest == "alpha"
    assert origin_of("mine.yaml", replace(mine, based_on="beta"), False, bundled).closest == "beta"


def test_a_profile_that_checks_no_outside_package_is_looser_than_one_that_does():
    assert loosened(replace(parsed(layered()), libraries=None), parsed(layered())) == (
        Loosened("libraries", "", "", "outside packages are not checked"),)


def test_every_way_a_profile_is_looser_than_another_is_found_in_order():
    parts = {**PARTS, "core": {**PARTS["core"], "may_import": ["store"], "libraries": ["yaml"]},
             "store": {"path": "store", "role": "storage", "may_import": ["core"],
                       "libraries": ["sqlmodel", "requests"], "untested": "trust me"}}
    custom = {**BASE, "parts": parts, "forbidden": {"pure": ["socket"]},
              "tiers": {"unit": {key: value for key, value in TIER.items() if key != "types_only"}
                        | {"apply_forbidden": False, "may_also_import": ["edge"]}},
              "testing": {**TESTING, "skips": ["pytest.mark.skip"]}, "guards": {},
              "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    assert loosened(parsed(custom), parsed(BASE)) == (
        Loosened("may_import", "core", "store", "core may also import store (parts.core.may_import)"),
        Loosened("libraries", "core", "yaml", "core may also import yaml (parts.core.libraries)"),
        Loosened("libraries", "store", "requests", "store may also import requests (parts.store.libraries)"),
        Loosened("forbidden", "core", "time.time", "core no longer forbids time.time (parts.core.forbidden)"),
        Loosened("untested", "store", "", "store is newly marked untested (parts.store.untested)"),
        Loosened("types_only", "unit", "store", "the unit tests may now call store (tiers.unit.types_only)"),
        Loosened("may_also_import", "unit", "edge", "the unit tests may also import edge (tiers.unit.may_also_import)"),
        Loosened("apply_forbidden", "unit", "",
                 "the unit tests are no longer held to their part's forbidden list (tiers.unit.apply_forbidden)"),
        Loosened("testing.skips", "", "pytest.mark.xfail",
                 "pytest.mark.xfail is no longer counted as a skip (testing.skips)"),
        Loosened("files.pinned", "", "tests/test_rules.py",
                 "tests/test_rules.py is no longer pinned (files.tests/test_rules.py.pinned)"))


@pytest.mark.parametrize("bundled, custom, found", [
    pytest.param([], ["shared/text", "store@any"], (
        Loosened("may_also_import", "unit", "shared/text",
                 "the unit tests may also import shared/text (tiers.unit.may_also_import)"),
        Loosened("may_also_import", "unit", "store@any",
                 "the unit tests may also import store@any (tiers.unit.may_also_import)")),
                 id="each target the bundled tier does not give is looser, shown as written"),
    pytest.param(["shared", "store"], ["shared/text", "store"], (),
                 id="a target the bundled tier's covers is not looser"),
    pytest.param(["shared"], [], (), id="a target dropped is stricter, and not listed"),
])
def test_what_a_tiers_tests_may_also_import_beyond_the_bundled_tier_is_looser(bundled, custom, found):
    base, mine = covered(), covered()
    base["tiers"]["unit"]["may_also_import"] = bundled
    mine["tiers"]["unit"]["may_also_import"] = custom
    assert loosened(parsed(mine), parsed(base)) == found


def test_a_name_the_base_reserves_and_the_custom_profile_does_not_is_looser():
    base = parsed(layered(reserved={"ast": "the reader's", "json": "the store's"}))
    assert loosened(parsed(layered(reserved={"json": "mine"})), base) == (
        Loosened("reserved", "", "ast", "ast is no longer reserved (reserved.ast)"),)
    assert loosened(parsed(layered(reserved={"ast": "the reader's", "json": "the store's", "csv": "x"})), base) == ()


def test_a_part_redefined_without_the_litmus_the_base_gives_it_is_looser_and_one_the_base_gives_none_is_not():
    base = layered()
    base["parts"]["api"]["litmus"] = "Does it answer a request?"
    custom = layered()
    custom["parts"]["store"]["litmus"] = "Does it keep a record?"
    assert loosened(parsed(custom), parsed(base)) == (
        Loosened("litmus", "api", "",
                 "api has no litmus, though the profile it is compared with gives it one (parts.api.litmus)"),)
    assert loosened(parsed(base), parsed(base)) == ()


def test_a_public_name_accepted_as_only_the_tests_that_the_base_does_not_accept_is_looser():
    def dead(*known: str) -> dict:
        return covered(guards={"dead-code": {"tests_only": True, "known": list(known)}},
                       fakes={"folder": "fakes", "for": ["store"]})
    assert loosened(parsed(dead("shared/text.py:clean", "shared/wiring.py:build")), parsed(dead("shared/text.py:clean"))) == (
        Loosened("known", "", "shared/wiring.py:build",
                 "the tests-only check accepts shared/wiring.py:build as a name only the tests use (guards.dead-code.known)"),)
    assert loosened(parsed(dead("shared/text.py:clean")), parsed(dead("shared/text.py:clean", "shared/wiring.py:build"))) == ()


def test_a_part_whose_translations_no_twins_accepts_that_the_base_does_not_list_is_looser():
    def translated(*parts: str) -> dict:
        return covered(guards={"no-twins": {"translated": list(parts)}})
    assert loosened(parsed(translated("api", "store")), parsed(translated("api"))) == (
        Loosened("translated", "store", "",
                 "no-twins accepts each pair of classes a function of store translates (guards.no-twins.translated)"),)
    assert loosened(parsed(translated("api")), parsed(translated("api", "store"))) == ()


def test_a_path_review_never_sends_or_a_text_it_hides_that_the_base_holds_and_the_custom_drops_is_looser():
    base = parsed(layered(review={"never": ["src/drafts", "**/secrets"], "mask": ["Northwind", "DOC-*"]}))
    custom = parsed(layered(review={"never": ["**/secrets", "src/legal"], "mask": ["DOC-*"]}))
    assert loosened(custom, base) == (
        Loosened("review.never", "", "src/drafts",
                 "src/drafts may be sent again: the profile it is compared with holds it back (review.never)"),
        Loosened("review.mask", "", "Northwind", "Northwind is no longer masked before review sends (review.mask)"))
    assert loosened(base, parsed(layered())) == ()


def test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own():
    """Each case of LOOSER is reached by one of these pairs (custom, base), and each key is said its own way."""
    store = {key: value for key, value in PARTS["store"].items() if key != "tier"}
    every = {**BASE, "parts": {**PARTS, "store": store | {"untested": "trust me", "libraries": ["sqlmodel", "requests"]},
                               "core": {**PARTS["core"], "may_import": ["store"]}},
             "forbidden": {"pure": ["socket"]}, "testing": {**TESTING, "skips": ["pytest.mark.skip"]},
             "tiers": {"unit": {key: value for key, value in TIER.items() if key != "types_only"}
                       | {"apply_forbidden": False, "may_also_import": ["edge"]}},
             "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    litmus = layered()
    litmus["parts"]["api"]["litmus"] = "Does it answer a request?"
    pairs = [
        (parsed(every), parsed(BASE)),
        (parsed(BASE), parsed({**BASE, "parts": part("store", must_import=["core"])})),
        (parsed(layered()), parsed(litmus)),
        (parsed(layered()), parsed(layered(reserved={"ast": "the reader's"}))),
        (parsed(covered(guards={"dead-code": {"tests_only": True, "known": ["shared/wiring.py:build"]}},
                        fakes={"folder": "fakes", "for": ["store"]})), parsed(covered())),
        (parsed(covered(guards={"no-twins": {"translated": ["api"]}})), parsed(covered())),
        (parsed(layered()), parsed(layered(review={"never": ["src/drafts"], "mask": ["Northwind"]}))),
    ]
    found = [item for custom, base in pairs for item in loosened(custom, base)]
    assert sorted({item.key for item in found}) == sorted(LOOSER)
    assert [item.key for item in found if "is no longer reserved" in item.sentence] == ["reserved"]
