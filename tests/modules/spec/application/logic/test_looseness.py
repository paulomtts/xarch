"""How a custom profile is looser than a bundled one, on hand-made architectures, as the origin of the custom one says
it: a rule's target is shown as the file writes it, and each way is said naming the key that says it. The sentence of
each way a profile is looser is asserted here or in tests/modules/spec/application/test_origin.py (a package added to
`imports.libraries`, a part that may import any outside package, an `imports.must` target added or the key dropped)."""
from dataclasses import replace

import pytest

from tests.modules.spec.application.origins import BASE, PARTS, TESTING, TIER, part
from tests.modules.spec.profiles import covered, layered, parsed
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
    custom["parts"]["api"]["imports"] = {"may": written}
    stricter = layered()
    stricter["parts"]["api"]["imports"] = {"may": []}
    assert loosened(parsed(custom), parsed(stricter)) == (
        Loosened("imports.may", "api", shown, f"api may also import {shown} (parts.api.imports.may)"),)


@pytest.mark.parametrize("target", [
    pytest.param("shared/text", id="a folder below a part the bundled profile allows narrows it"),
    pytest.param("shared:*Text", id="a name pattern on a part the bundled profile allows narrows it"),
    pytest.param("store/sql:Sql*", id="a folder and a name pattern below an allowed part narrow it both"),
])
def test_a_target_below_one_the_bundled_profile_allows_is_not_looser(target):
    custom = layered()
    custom["parts"]["service"]["imports"] = {"may": ["store", "shared", target]}
    assert loosened(parsed(custom), parsed(layered())) == ()


def test_the_bundled_profile_a_profile_says_it_is_based_on_wins_over_the_one_sharing_most_parts():
    full = parsed(layered())
    bundled = {"alpha": full, "beta": replace(full, parts={"api": full.parts["api"]})}
    mine = replace(full, parts={name: full.parts[name] for name in ("api", "store")})
    assert origin_of("mine.yaml", mine, False, bundled).closest == "alpha"
    assert origin_of("mine.yaml", replace(mine, based_on="beta"), False, bundled).closest == "beta"


def test_a_profile_that_checks_no_outside_package_is_looser_than_one_that_does():
    assert loosened(replace(parsed(layered()), libraries=None), parsed(layered())) == (
        Loosened("imports.libraries", "", "", "outside packages are not checked"),)


def test_every_way_a_profile_is_looser_than_another_is_found_in_order():
    parts = {**PARTS, "core": {**PARTS["core"], "imports": {"may": ["store"], "libraries": ["yaml"]}},
             "store": {"path": "store", "role": "storage",
                       "imports": {"may": ["core"], "libraries": ["sqlmodel", "requests"]}, "untested": "trust me"}}
    custom = {**BASE, "parts": parts, "never": {"pure": ["socket"]},
              "tiers": {"unit": {key: value for key, value in TIER.items() if key != "imports"}
                        | {"uses": {"apply_never": False}, "imports": {"also": ["edge"]}}},
              "testing": {**TESTING, "skips": ["pytest.mark.skip"]}, "guards": {},
              "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    assert loosened(parsed(custom), parsed(BASE)) == (
        Loosened("imports.may", "core", "store", "core may also import store (parts.core.imports.may)"),
        Loosened("imports.libraries", "core", "yaml", "core may also import yaml (parts.core.imports.libraries)"),
        Loosened("imports.libraries", "store", "requests", "store may also import requests (parts.store.imports.libraries)"),
        Loosened("uses.never", "core", "time.time", "core no longer forbids time.time (parts.core.uses.never)"),
        Loosened("untested", "store", "", "store is newly marked untested (parts.store.untested)"),
        Loosened("imports.types_only", "unit", "store",
                 "the unit tests may now call store (tiers.unit.imports.types_only)"),
        Loosened("imports.also", "unit", "edge", "the unit tests may also import edge (tiers.unit.imports.also)"),
        Loosened("uses.apply_never", "unit", "",
                 "the unit tests are no longer held to their part's never list (tiers.unit.uses.apply_never)"),
        Loosened("testing.skips", "", "pytest.mark.xfail",
                 "pytest.mark.xfail is no longer counted as a skip (testing.skips)"),
        Loosened("files.pinned", "", "tests/test_rules.py",
                 "tests/test_rules.py is no longer pinned (files.tests/test_rules.py.pinned)"))


@pytest.mark.parametrize("bundled, custom, found", [
    pytest.param([], ["shared/text", "store@any"], (
        Loosened("imports.also", "unit", "shared/text",
                 "the unit tests may also import shared/text (tiers.unit.imports.also)"),
        Loosened("imports.also", "unit", "store@any",
                 "the unit tests may also import store@any (tiers.unit.imports.also)")),
                 id="each target the bundled tier does not give is looser, shown as written"),
    pytest.param(["shared", "store"], ["shared/text", "store"], (),
                 id="a target the bundled tier's covers is not looser"),
    pytest.param(["shared"], [], (), id="a target dropped is stricter, and not listed"),
])
def test_what_a_tiers_tests_may_also_import_beyond_the_bundled_tier_is_looser(bundled, custom, found):
    base, mine = covered(), covered()
    base["tiers"]["unit"]["imports"] = {"also": bundled}
    mine["tiers"]["unit"]["imports"] = {"also": custom}
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


def test_a_part_whose_line_is_below_the_one_the_base_gives_it_is_looser_and_a_higher_line_is_not():
    def lines(**written: float) -> dict:
        return layered(evals={"placement": {"lines": written}})
    assert loosened(parsed(lines(store=0.2, api=0.4, service=0.1)), parsed(lines(service=0.05))) == (
        Loosened("evals.placement.lines", "store", "0.20", "store reads as doubtful only below 0.20, a lower line "
                 "than the profile it is compared with gives it (evals.placement.lines)"),)
    assert loosened(parsed(layered()), parsed(lines(store=0.4))) == (
        Loosened("evals.placement.lines", "store", "0.30", "store reads as doubtful only below 0.30, a lower line "
                 "than the profile it is compared with gives it (evals.placement.lines)"),)


def test_every_key_a_profile_is_looser_under_has_a_sentence_of_its_own():
    """Each case of LOOSER is reached by one of these pairs (custom, base), and each key is said its own way."""
    store = {key: value for key, value in PARTS["store"].items() if key != "tests"}
    every = {**BASE, "parts": {**PARTS, "store": store | {"untested": "trust me",
                               "imports": {"may": ["core"], "libraries": ["sqlmodel", "requests"]}},
                               "core": {**PARTS["core"], "imports": {"may": ["store"]}}},
             "never": {"pure": ["socket"]}, "testing": {**TESTING, "skips": ["pytest.mark.skip"]},
             "tiers": {"unit": {key: value for key, value in TIER.items() if key != "imports"}
                       | {"uses": {"apply_never": False}, "imports": {"also": ["edge"]}}},
             "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    litmus = layered()
    litmus["parts"]["api"]["litmus"] = "Does it answer a request?"
    pairs = [
        (parsed(every), parsed(BASE)),
        (parsed(BASE), parsed({**BASE, "parts": part("store", imports={"may": ["core"], "must": ["core"], "libraries": ["sqlmodel"]})})),
        (parsed(layered()), parsed(litmus)),
        (parsed(layered()), parsed(layered(reserved={"ast": "the reader's"}))),
        (parsed(covered(guards={"dead-code": {"tests_only": True, "known": ["shared/wiring.py:build"]}},
                        fakes={"folder": "fakes", "for": ["store"]})), parsed(covered())),
        (parsed(covered(guards={"no-twins": {"translated": ["api"]}})), parsed(covered())),
        (parsed(layered()), parsed(layered(review={"never": ["src/drafts"], "mask": ["Northwind"]}))),
        (parsed(layered(evals={"placement": {"lines": {"store": 0.2}}})), parsed(layered())),
        (parsed(marked(["store", "shared"])), parsed(marked(["store", {"shared": "types_only"}]))),
    ]
    found = [item for custom, base in pairs for item in loosened(custom, base)]
    assert sorted({item.key for item in found}) == sorted(LOOSER)
    assert [item.key for item in found if "is no longer reserved" in item.sentence] == ["reserved"]


MARK = "imports.may.types_only"
"""The key a types_only mark dropped from an entry of a part's imports.may is listed under."""


def marked(may) -> dict:
    """layered(), its part service allowed may."""
    document = layered()
    document["parts"]["service"]["imports"]["may"] = may
    return document


@pytest.mark.parametrize("base, custom, found", [
    pytest.param(["store", {"shared": "types_only"}], ["store", "shared"],
                 [(MARK, "service", "shared", "service may now call shared, which it used only as a type "
                                             "(parts.service.imports.may.types_only)")],
                 id="a mark dropped from an entry that stays"),
    pytest.param(["store", {"shared": "types_only"}], ["store"], [], id="the entry dropped with its mark"),
    pytest.param(["store", {"shared": "types_only"}], ["store", {"shared": "types_only"}], [], id="the mark kept"),
    pytest.param(["store", {"shared/x": "types_only"}], ["store", {"shared": "types_only"}], [],
                 id="a wider mark covers it"),
    pytest.param(["store", {"shared": "types_only"}], "everything",
                 [(MARK, "service", "shared", "service may now call shared, which it used only as a type "
                                             "(parts.service.imports.may.types_only)")],
                 id="everything over a mark"),
])
def test_a_mark_dropped_while_its_target_stays_allowed_is_looser(base, custom, found):
    assert [(item.key, item.part, item.what, item.sentence)
            for item in loosened(parsed(marked(custom)), parsed(marked(base))) if item.key == MARK] == found


def test_a_tier_s_looser_keys_are_those_of_its_group_and_the_old_words_are_gone():
    assert LOOSER.index("imports.types_only") < LOOSER.index("imports.also") < LOOSER.index("uses.apply_never")
    assert not {"types_only", "may_also_import"} & set(LOOSER)
