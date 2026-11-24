"""How a custom profile is looser than a bundled one, on hand-made architectures, as the origin of the custom one says
it: a rule's target is shown as a reference (parts.<part> or <word>.<part>), and each way is said naming the key that
says it. The sentence of each way a profile is looser is asserted here or in
tests/modules/spec/application/test_origin.py (a package added to `imports.libraries`, a part that may import any
outside package, an `imports.must` target added or the key dropped)."""
from copy import deepcopy
from dataclasses import replace

import pytest

from tests.modules.spec.application.origins import BASE, PARTS, TESTING, TIER, part
from tests.modules.spec.profiles import covered, layered, parsed, part_of, two_folders
from xarch.modules.spec.application.logic.looseness import LOOSER, LOW, origin_of
from xarch.modules.spec.domain.guards import ORDER
from xarch.modules.spec.domain.published import Loosened, Origin
from xarch.modules.spec.domain.values import Architecture


def loosened(custom: Architecture, base: Architecture) -> tuple[Loosened, ...]:
    """Every way custom is looser than base, as the origin of custom, based on base, lists them."""
    return origin_of("mine.yaml", replace(custom, based_on="base"), False, {"base": base}).looser


@pytest.mark.parametrize("written, shown", [
    pytest.param(["module.service"], "module.service", id="an own-instance part is shown by its word"),
    pytest.param(["parts.store/sql"], "parts.store/sql", id="any instance and a sub path"),
    pytest.param(["parts.shared/text"], "parts.shared/text", id="a part outside the repeating folder is shown with parts."),
    pytest.param("everything", "everything", id="everything is shown as the word"),
    pytest.param(["parts.api"], "parts.api", id="another instance of the part itself is looser than its own, which is implied"),
])
def test_a_target_added_to_a_rule_is_shown_as_written(written, shown):
    custom = layered()
    part_of(custom, "api")["imports"] = {"may": written}
    stricter = layered()
    part_of(stricter, "api")["imports"] = {"may": []}
    assert loosened(parsed(custom), parsed(stricter)) == (
        Loosened("imports.may", "api", shown, f"api may also import {shown} (parts.api.imports.may)"),)


@pytest.mark.parametrize("may, shown", [
    pytest.param(["plugin.hooks"], "plugin.hooks", id="the own instance is named by the word of its part's own folder"),
    pytest.param(["parts.hooks"], "parts.hooks", id="any instance of a part of the second folder is named with parts."),
])
def test_the_word_a_target_is_shown_with_is_that_of_its_part_s_own_repeating_folder(may, shown):
    base, custom = two_folders(), two_folders()
    part_of(base, "manifest")["imports"] = {"may": []}
    part_of(custom, "manifest")["imports"] = {"may": may}
    assert loosened(parsed(custom), parsed(base)) == (
        Loosened("imports.may", "manifest", shown, f"manifest may also import {shown} (parts.manifest.imports.may)"),)


@pytest.mark.parametrize("target", [
    pytest.param("parts.shared/text", id="a folder below a part the bundled profile allows narrows it"),
    pytest.param("parts.shared:*Text", id="a name pattern on a part the bundled profile allows narrows it"),
    pytest.param("module.store/sql:Sql*", id="a folder and a name pattern below an allowed part narrow it both"),
])
def test_a_target_below_one_the_bundled_profile_allows_is_not_looser(target):
    custom = layered()
    part_of(custom, "service")["imports"] = {"may": ["module.store", "parts.shared", target]}
    assert loosened(parsed(custom), parsed(layered())) == ()


def test_a_profile_that_checks_no_outside_package_is_looser_than_one_that_does():
    assert loosened(replace(parsed(layered()), imports_libraries=None), parsed(layered())) == (
        Loosened("imports.libraries", "", "", "outside packages are not checked"),)


def test_every_way_a_profile_is_looser_than_another_is_found_in_order():
    parts = {**PARTS, "core/": {**PARTS["core/"], "imports": {"may": ["parts.store"], "libraries": ["yaml"]}},
             "store/": {"role": "storage",
                       "imports": {"may": ["parts.core"], "libraries": ["sqlmodel", "requests"]}, "untested": "trust me"}}
    custom = {**BASE, "parts": parts, "never": {"pure": ["socket"]},
              "tiers": {"unit": {key: value for key, value in TIER.items() if key != "imports"}
                        | {"uses": {"apply_never": False}, "imports": {"also": ["parts.edge"]}}},
              "testing": {**TESTING, "skips": ["pytest.mark.skip"]}, "guards": {},
              "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    assert loosened(parsed(custom), parsed(BASE)) == (
        Loosened("imports.may", "core", "parts.store", "core may also import parts.store (parts.core.imports.may)"),
        Loosened("imports.libraries", "core", "yaml", "core may also import yaml (parts.core.imports.libraries)"),
        Loosened("imports.libraries", "store", "requests", "store may also import requests (parts.store.imports.libraries)"),
        Loosened("uses.never", "core", "time.time", "core no longer forbids time.time (parts.core.uses.never)"),
        Loosened("untested", "store", "", "store is newly marked untested (parts.store.untested)"),
        Loosened("imports.types_only", "unit", "store",
                 "the unit tests may now call store (tiers.unit.imports.types_only)"),
        Loosened("imports.also", "unit", "parts.edge", "the unit tests may also import parts.edge (tiers.unit.imports.also)"),
        Loosened("uses.apply_never", "unit", "",
                 "the unit tests are no longer held to their part's never list (tiers.unit.uses.apply_never)"),
        Loosened("testing.skips", "", "pytest.mark.xfail",
                 "pytest.mark.xfail is no longer counted as a skip (testing.skips)"),
        Loosened("files.pinned", "", "tests/test_rules.py",
                 "tests/test_rules.py is no longer pinned (files.tests/test_rules.py.pinned)"))


@pytest.mark.parametrize("bundled, custom, found", [
    pytest.param([], ["parts.shared/text", "parts.store"], (
        Loosened("imports.also", "unit", "parts.shared/text",
                 "the unit tests may also import parts.shared/text (tiers.unit.imports.also)"),
        Loosened("imports.also", "unit", "parts.store",
                 "the unit tests may also import parts.store (tiers.unit.imports.also)")),
                 id="each target the bundled tier does not give is looser, shown as a reference"),
    pytest.param(["parts.shared", "module.store"], ["parts.shared/text", "module.store"], (),
                 id="a target the bundled tier's covers is not looser"),
    pytest.param(["parts.shared"], [], (), id="a target dropped is stricter, and not listed"),
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
    part_of(base, "api")["litmus"] = "Does it answer a request?"
    custom = layered()
    part_of(custom, "store")["litmus"] = "Does it keep a record?"
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
    store = {key: value for key, value in PARTS["store/"].items() if key != "tests"}
    every = {**BASE, "parts": {**PARTS, "store/": store | {"untested": "trust me",
                               "imports": {"may": ["parts.core"], "libraries": ["sqlmodel", "requests"]}},
                               "core/": {**PARTS["core/"], "imports": {"may": ["parts.store"]}}},
             "never": {"pure": ["socket"]}, "testing": {**TESTING, "skips": ["pytest.mark.skip"]},
             "tiers": {"unit": {key: value for key, value in TIER.items() if key != "imports"}
                       | {"uses": {"apply_never": False}, "imports": {"also": ["parts.edge"]}}},
             "files": {"tests/test_rules.py": {"from": "guard.py"}}}
    litmus = layered()
    part_of(litmus, "api")["litmus"] = "Does it answer a request?"
    pairs = [
        (parsed(every), parsed(BASE)),
        (parsed(BASE), parsed({**BASE, "parts": part("store", imports={"may": ["parts.core"], "must": ["parts.core"],
                                                                       "libraries": ["sqlmodel"]})})),
        (parsed(layered()), parsed(litmus)),
        (parsed(layered()), parsed(layered(reserved={"ast": "the reader's"}))),
        (parsed(covered(guards={"dead-code": {"tests_only": True, "known": ["shared/wiring.py:build"]}},
                        fakes={"folder": "fakes", "for": ["store"]})), parsed(covered())),
        (parsed(covered(guards={"no-twins": {"translated": ["api"]}})), parsed(covered())),
        (parsed(layered()), parsed(layered(review={"never": ["src/drafts"], "mask": ["Northwind"]}))),
        (parsed(layered(evals={"placement": {"lines": {"store": 0.2}}})), parsed(layered())),
        (parsed(marked(["module.store", "parts.shared"])), parsed(marked(["module.store", {"parts.shared": "types_only"}]))),
        (parsed(holding()), parsed(holding(classes={}))),
        (parsed(holding()), parsed(holding(classes={"names": "*Service", "immutable": True, "built_by": ["api"]},
                                           functions={"names": "is_*"}, records={"names": "*Record", "immutable": True},
                                           exceptions={"names": "*Error"}))),
        (parsed(layered()), parsed(given(layered(), "service", shared=3))),
        (parsed(covered()), parsed(tight())),
        (near(True), near(None)),
    ]
    found = [item for custom, base in pairs for item in loosened(custom, base)]
    assert sorted({item.key for item in found}) == sorted(LOOSER)
    assert [item.key for item in found if "is no longer reserved" in item.sentence] == ["reserved"]


MARK = "imports.may.types_only"
"""The key a types_only mark dropped from an entry of a part's imports.may is listed under."""


def marked(may) -> dict:
    """layered(), its part service allowed may."""
    document = layered()
    part_of(document, "service")["imports"]["may"] = may
    return document


@pytest.mark.parametrize("base, custom, found", [
    pytest.param(["module.store", {"parts.shared": "types_only"}], ["module.store", "parts.shared"],
                 [(MARK, "service", "parts.shared", "service may now call parts.shared, which it used only as a type "
                                                    "(parts.service.imports.may.types_only)")],
                 id="a mark dropped from an entry that stays"),
    pytest.param([{"module.store": "types_only"}, "parts.shared"], ["module.store", "parts.shared"],
                 [(MARK, "service", "module.store", "service may now call module.store, which it used only as a type "
                                                    "(parts.service.imports.may.types_only)")],
                 id="a mark dropped from an own-instance entry, shown by its word"),
    pytest.param(["module.store", {"parts.shared": "types_only"}], ["module.store"], [], id="the entry dropped with its mark"),
    pytest.param(["module.store", {"parts.shared": "types_only"}], ["module.store", {"parts.shared": "types_only"}], [],
                 id="the mark kept"),
    pytest.param(["module.store", {"parts.shared/x": "types_only"}], ["module.store", {"parts.shared": "types_only"}], [],
                 id="a wider mark covers it"),
    pytest.param(["module.store", {"parts.shared": "types_only"}], "everything",
                 [(MARK, "service", "parts.shared", "service may now call parts.shared, which it used only as a type "
                                                    "(parts.service.imports.may.types_only)")],
                 id="everything over a mark"),
])
def test_a_mark_dropped_while_its_target_stays_allowed_is_looser(base, custom, found):
    assert [(item.key, item.part, item.what, item.sentence)
            for item in loosened(parsed(marked(custom)), parsed(marked(base))) if item.key == MARK] == found


def test_a_mark_dropped_from_an_own_instance_entry_whose_part_lies_in_no_repeating_folder_here_is_shown_with_parts():
    custom = marked("everything")
    custom["parts"]["store/"] = custom["parts"]["src/<module>/"].pop("store/")
    assert [(item.key, item.part, item.what, item.sentence)
            for item in loosened(parsed(custom), parsed(marked([{"module.store": "types_only"}, "parts.shared"])))
            if item.key == MARK] == [
        (MARK, "service", "parts.store", "service may now call parts.store, which it used only as a type "
                                         "(parts.service.imports.may.types_only)")]


def test_a_tier_s_looser_keys_are_those_of_its_group_and_the_old_words_are_gone():
    assert LOOSER.index("imports.types_only") < LOOSER.index("imports.also") < LOOSER.index("uses.apply_never")
    assert not {"types_only", "may_also_import"} & set(LOOSER)


def bare(**paths: str) -> Architecture:
    """A profile of the parts given, each at its path, checking no outside package: one item per part and no more."""
    return replace(parsed({"name": "bare", "parts": {f"{path}/": {"role": "code"} for path in paths.values()}}),
                   imports_libraries=None)


def compared(custom: Architecture, base: Architecture) -> Origin:
    """The origin of custom, based on base."""
    return origin_of("mine.yaml", replace(custom, based_on="base"), False, {"base": base})


def renamed(document: dict, old: str, new: str) -> dict:
    """The document with the part old named new, at the same place in the order and the same path."""
    part_of(document, old)["name"] = new
    return document


def moved(document: dict, name: str, folder: str) -> dict:
    """The document with the part name at another folder, in the same folder of its parent and the same place in the
    order, still named name."""
    def walk(node: dict) -> bool:
        for key, value in node.items():
            if value is part_of(document, name):
                value["name"] = name
                items = [(folder if entry == key else entry, kept) for entry, kept in node.items()]
                node.clear()
                node.update(items)
                return True
            if isinstance(value, dict) and walk(value):
                return True
        return False
    assert walk(document["parts"])
    return document


def test_a_copy_of_a_profile_matches_it_at_100_percent():
    origin = origin_of("mine.yaml", parsed(layered()), False, {"base": parsed(layered())})
    assert (origin.compared, origin.chosen_by, origin.match, origin.low) == ("base", "closest", 1.0, False)
    assert origin.only_here == origin.only_there == origin.elsewhere == ()
    assert origin.higher is None


def test_a_key_one_side_drops_on_a_paired_part_is_comparable_and_listed_looser():
    base = layered()
    part_of(base, "api")["litmus"] = "Does it answer a request?"
    origin = compared(parsed(layered()), parsed(base))
    assert origin.match == 1.0
    assert [item.key for item in origin.looser] == ["litmus"]


def test_the_items_of_an_unpaired_part_are_not_comparable():
    custom = layered()
    custom["parts"]["jobs/"] = {"role": "batch work", "litmus": "Does it run on a schedule?",
                               "imports": {"may": ["parts.shared"]}}
    origin = compared(parsed(custom), parsed(layered()))
    assert origin.counts[:2] == (("parts", 4, 5), ("part_keys", 7, 10))
    assert (origin.only_here, origin.only_there) == (("part jobs",), ())
    assert origin.match == round(12 / 16, 2)


def test_guards_and_profile_keys_are_always_comparable():
    origin = compared(parsed(layered(guards={"no-comments": {}, "closed-tree": {}}, reserved={"ast": "the reader's"})),
                      parsed(layered()))
    assert origin.counts[3:] == (("guards", 2, 2), ("profile", 2, 2))
    assert origin.match == 1.0


def test_each_setting_of_a_held_kind_is_an_item_of_its_own():
    custom = layered()
    part_of(custom, "service")["holds"] = {"classes": {"names": ["*Service"], "immutable": True, "built_by": ["api"]}}
    assert compared(parsed(custom), parsed(layered())).counts[1] == ("part_keys", 11, 11)


def test_a_tier_folder_written_empty_is_an_item_and_no_folder_is_none():
    architecture = parsed(covered())
    unit = architecture.tiers[0]
    empty = replace(architecture, tiers=(replace(unit, imports_may=()), *architecture.tiers[1:]))
    assert unit.imports_may is None
    assert compared(empty, architecture).counts[2] == ("tiers", 6, 6)
    assert compared(architecture, architecture).counts[2] == ("tiers", 5, 5)


OWN = {"read": "call", "may_not": {"path": ["builtins.print"]}, "message": "{where} prints", "fix": "log it",
       "examples": {"flagged": {"src/billing/api/x.py": "print(1)\n"}, "clean": {"src/billing/api/y.py": "pass\n"}}}
"""A check of the profile's own: no part of it prints."""


def test_a_check_of_the_profile_s_own_is_comparable_only_with_the_same_id():
    base = parsed(layered(checks={"no-print": OWN}))
    assert compared(parsed(layered(checks={"no-print": OWN})), base).counts[4] == ("profile", 2, 2)
    assert compared(parsed(layered(checks={"prints": OWN})), base).counts[4] == ("profile", 1, 3)


def test_a_bundled_profile_no_part_pairs_with_is_no_candidate():
    origin = origin_of("mine.yaml", parsed(layered()), False, {"other": bare(web="web")})
    assert (origin.compared, origin.chosen_by, origin.match, origin.counts) == (None, None, None, ())


def test_the_bundled_profile_of_highest_match_is_compared_the_lowest_name_on_a_tie():
    mine = bare(a="a", b="b", c="c")
    bundled = {"far": bare(a="a", x="x", y="y"), "near": bare(a="a", b="b", c="c", d="d"), "mid": bare(a="a", b="b")}
    origin = origin_of("mine.yaml", mine, False, bundled)
    assert (origin.compared, origin.chosen_by, origin.match) == ("near", "closest", 0.75)
    tie = {"zeta": bare(a="a", b="b", c="c", d="d"), "beta": bare(a="a", b="b", c="c", e="e")}
    assert origin_of("mine.yaml", mine, False, tie).compared == "beta"


def test_the_bundled_profile_a_profile_says_it_is_based_on_wins_over_the_one_of_highest_match():
    mine = bare(a="a", b="b", c="c")
    bundled = {"alpha": bare(a="a", b="b", c="c"), "beta": bare(a="a")}
    origin = origin_of("mine.yaml", replace(mine, based_on="beta"), False, bundled)
    assert (origin.compared, origin.chosen_by, origin.match, origin.higher) == ("beta", "based_on", 0.33, ("alpha", 1.0))
    assert origin_of("mine.yaml", mine, False, bundled).higher is None


def test_based_on_a_bundled_profile_sharing_no_part_is_compared_low_with_no_part_in_common():
    other = replace(bare(web="web"), reserved={"ast": "the reader's"})
    origin = origin_of("mine.yaml", replace(parsed(layered()), based_on="other"), False, {"other": other})
    assert (origin.compared, origin.chosen_by, origin.low) == ("other", "based_on", True)
    assert origin.only_here == ("part api", "part service", "part shared", "part store")
    assert origin.only_there == ("part web",)
    assert origin.looser == (Loosened("reserved", "", "ast", "ast is no longer reserved (reserved.ast)"),)


def test_a_match_of_exactly_75_percent_is_not_low_and_just_below_is():
    base = bare(a="a", b="b", c="c", d="d")
    exact = compared(bare(a="a", b="b", c="c"), base)
    assert (LOW, exact.match, exact.low) == (0.75, 0.75, False)
    litmus = replace(base, parts={**base.parts, "d": replace(base.parts["d"], litmus="Is it d?")})
    below = compared(bare(a="a", b="b", c="c"), litmus)
    assert (below.match, below.low) == (0.6, True)


def test_a_match_that_rounds_to_75_percent_from_below_is_still_low():
    origin = compared(bare(**{f"p{n}": f"p{n}" for n in range(50)}), bare(**{f"p{n}": f"p{n}" for n in range(67)}))
    assert (origin.match, origin.low) == (0.75, True)


def test_the_counts_are_by_kind_in_order():
    counts = compared(parsed(covered()), parsed(layered())).counts
    assert [kind for kind, _, _ in counts] == ["parts", "part_keys", "tiers", "guards", "profile"]
    assert counts[2] == ("tiers", 0, 5)


def test_a_pair_by_name_at_another_path_is_named_elsewhere():
    custom = layered()
    moved(custom, "store", "db/")
    origin = compared(parsed(custom), parsed(layered()))
    assert origin.elsewhere == ("store: src/*/store there",)
    assert origin.match == 1.0


def test_a_part_renamed_in_place_pairs_by_its_path_and_is_compared_under_its_own_name():
    custom = renamed(layered(), "api", "routes")
    part_of(custom, "routes")["imports"] = {"may": ["module.service", "module.store"]}
    origin = compared(parsed(custom), parsed(layered()))
    assert (origin.match, origin.only_here, origin.only_there) == (1.0, (), ())
    assert origin.looser == (
        Loosened("imports.may", "routes", "module.store", "routes may also import module.store (parts.routes.imports.may)"),)


def test_a_target_naming_a_part_renamed_in_place_is_read_through_the_pairing():
    base = layered()
    part_of(base, "service")["imports"] = {"may": ["module.store", "parts.shared", "module.api"]}
    custom = renamed(layered(), "api", "routes")
    part_of(custom, "service")["imports"] = {"may": ["module.store", "parts.shared", "module.routes"]}
    origin = compared(parsed(custom), parsed(base))
    assert (origin.match, origin.looser) == (1.0, ())


def test_a_tier_renamed_with_the_same_subject_pairs_by_subject():
    base = covered()
    base["tiers"]["unit"]["uses"] = {"apply_never": True}
    custom = covered()
    custom["tiers"] = {"logic" if name == "unit" else name: tier for name, tier in custom["tiers"].items()}
    part_of(custom, "service")["tests"] = "logic"
    origin = compared(parsed(custom), parsed(base))
    assert (origin.match, origin.only_here, origin.only_there) == (1.0, (), ())
    assert origin.looser == (Loosened("uses.apply_never", "logic", "", "the logic tests are no longer held to their "
                                                                       "part's never list (tiers.logic.uses.apply_never)"),)



def given(document: dict, name: str, **keys) -> dict:
    """The document with its part name given the keys given besides its own."""
    part_of(document, name).update(keys)
    return document


def as_routes(value):
    """value with every "api" in it, as a key or an entry, bare or after a reference's prefix, read as "routes": the
    folder api/ named routes in place."""
    if isinstance(value, dict):
        read = {_routed(key): as_routes(entry) for key, entry in value.items()}
        return read | {"api/": {**read["api/"], "name": "routes"}} if "api/" in read else read
    if isinstance(value, list):
        return [as_routes(entry) for entry in value]
    return _routed(value)


def _routed(value):
    """"api" as "routes", and a reference to api (module.api, parts.api) as one to routes."""
    if not isinstance(value, str):
        return value
    prefix, dot, rest = value.partition(".")
    return "routes" if value == "api" else f"{prefix}.routes" if dot and rest == "api" else value


def holding(**holds) -> dict:
    """layered(), its part service holding the kinds given, each with its settings; no holds, every kind, when none is
    given."""
    return given(layered(), "service", holds=holds) if holds else layered()


def reaching(*parts: str) -> dict:
    """covered(), each test of its integration tier reaching one of the parts given."""
    document = covered()
    document["tiers"]["integration"]["imports"] = {"must": [f"parts.{name}" for name in parts]}
    return document


def plain() -> dict:
    """covered(), its unit tier plain_tables."""
    document = covered()
    document["tiers"]["unit"]["plain_tables"] = True
    return document


def tight() -> dict:
    """covered(), its unit tier plain_tables and each of its tests reaching service."""
    document = covered()
    document["tiers"]["unit"] |= {"plain_tables": True, "imports": {"must": ["parts.service"]}}
    return document


@pytest.mark.parametrize("profile", [
    pytest.param(given(layered(), "api", imports={"may": ["module.service"], "libraries": ["fastapi"]}),
                 id="the outside packages of the part"),
    pytest.param(given(layered(never={"pure": ["socket"]}), "api", uses={"never": "pure"}),
                 id="the never list of the part"),
    pytest.param(given(layered(), "service", imports={"may": ["module.store", "parts.shared", "module.api"], "must": ["module.api"]}),
                 id="a target naming it that a part must import"),
    pytest.param(given(layered(), "api", untested="reached through the service"), id="the part left untested"),
    pytest.param(layered(evals={"placement": {"lines": {"api": 0.2}}}), id="the line of the part"),
    pytest.param(covered(guards={"no-twins": {"translated": ["api"]}}), id="the translations no-twins accepts"),
    pytest.param(marked(["module.store", {"module.api": "types_only"}]), id="a target naming it marked types_only"),
    pytest.param(given(layered(), "service", holds={"classes": {"built_by": ["api"]}}), id="a built_by naming it"),
    pytest.param(given(layered(), "api", holds={"classes": {"names": "*Api", "built_by": ["service"]}}, shared=2),
                 id="the kinds the part holds, their settings and how widely it is shared"),
    pytest.param(reaching("api"), id="a tier's imports.must naming it"),
])
def test_each_key_of_a_part_renamed_in_place_is_compared_with_the_part_it_pairs_with(profile):
    """Each key is read from the part api pairs with, so a copy that only renames api is no looser."""
    assert loosened(parsed(as_routes(deepcopy(profile))), parsed(profile)) == ()


@pytest.mark.parametrize("base, custom, key, part, what", [
    pytest.param(given(layered(never={"pure": ["socket"]}), "api", uses={"never": "pure"}),
                 as_routes(layered(never={"pure": ["socket"]})), "uses.never", "routes", "socket",
                 id="a never list dropped"),
    pytest.param(marked(["module.store", {"module.api": "types_only"}]), as_routes(marked(["module.store", "module.api"])), MARK, "service",
                 "module.routes", id="a types_only mark dropped from a target naming it"),
    pytest.param(given(layered(), "api", holds={"classes": {"built_by": ["service"]}}),
                 as_routes(given(layered(), "api", holds={"classes": {}})), "holds.classes.built_by", "routes", "",
                 id="a built_by dropped from it"),
    pytest.param(given(layered(), "service", holds={"classes": {"built_by": ["api"]}}),
                 as_routes(given(layered(), "service", holds={"classes": {"built_by": ["api", "store"]}})),
                 "holds.classes.built_by", "service", "store", id="a built_by naming it widened, it read as itself"),
    pytest.param(reaching("api"), as_routes(reaching("api", "store")), "tiers.imports.must", "integration", "store",
                 id="a tier's imports.must naming it widened, it read as itself"),
])
def test_a_way_a_copy_renaming_a_part_in_place_is_looser_is_said_under_the_new_name(base, custom, key, part, what):
    assert [(item.key, item.part, item.what) for item in loosened(parsed(custom), parsed(base))] == [(key, part, what)]


@pytest.mark.parametrize("base, custom, kinds", [
    pytest.param(holding(functions={}), holding(functions={}, classes={}), ["classes", "records", "exceptions"],
                 id="classes added allow records and exceptions too, each a kind of its own"),
    pytest.param(holding(classes={}), holding(classes={}, records={"immutable": True}), [],
                 id="records written beside classes were allowed already"),
    pytest.param(holding(classes={}), holding(), ["functions"],
                 id="holds dropped allows the kinds classes did not, records and exceptions coming through classes"),
    pytest.param(holding(), holding(functions={}), [], id="a base with no holds allowed every kind"),
    pytest.param(holding(functions={}, classes={}), holding(functions={}), [], id="a kind dropped is stricter"),
])
def test_a_kind_a_part_may_now_define_at_the_top_level_is_looser(base, custom, kinds):
    assert [item for item in loosened(parsed(custom), parsed(base)) if item.key == "holds"] == [
        Loosened("holds", "service", kind, f"service may also define {kind} at the top level (parts.service.holds)")
        for kind in kinds]


@pytest.mark.parametrize("base, custom, found", [
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={}),
                 [("holds.classes.names", "", "the classes of service may be named anything "
                                              "(parts.service.holds.classes.names)")],
                 id="names dropped"),
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={"names": ["*Service", "*"]}),
                 [("holds.classes.names", "*", "the classes of service may also be named * "
                                               "(parts.service.holds.classes.names)")],
                 id="a pattern no pattern of the base covers"),
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={"names": "FooService"}), [],
                 id="a pattern a pattern of the base covers"),
    pytest.param(holding(classes={"names": ["*Service", "*Store"]}), holding(classes={"names": "*Service"}), [],
                 id="a pattern dropped from a list that keeps others is stricter"),
    pytest.param(holding(functions={"names": "is_*"}), holding(functions={}),
                 [("holds.functions.names", "", "the functions of service may be named anything "
                                                "(parts.service.holds.functions.names)")],
                 id="the names of functions dropped"),
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={"names": "*Service"}, records={"immutable": True}),
                 [("holds.records.names", "", "the records of service may be named anything "
                                              "(parts.service.holds.records.names)")],
                 id="records held to the names of classes, now listed with none"),
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={"names": "*Service"}), [],
                 id="records neither lists are not compared"),
    pytest.param(holding(classes={"names": "*Service"}), holding(exceptions={}),
                 [("holds.exceptions.names", "", "the exceptions of service may be named anything "
                                                 "(parts.service.holds.exceptions.names)")],
                 id="exceptions listed alone, held to the names of classes before"),
    pytest.param(holding(classes={"names": "*"}), holding(classes={"names": ["*Service", "Odd"]}), [],
                 id="a pattern of the base of * covers every pattern"),
    pytest.param(holding(records={"immutable": True}), holding(records={}),
                 [("holds.records.immutable", "", "the records of service need no longer be immutable records "
                                                  "(parts.service.holds.records.immutable)")],
                 id="records no longer immutable"),
    pytest.param(holding(classes={"immutable": True}), holding(classes={}),
                 [("holds.classes.immutable", "", "the classes of service need no longer be immutable records "
                                                  "(parts.service.holds.classes.immutable)")],
                 id="classes no longer immutable"),
    pytest.param(holding(classes={"immutable": True}), holding(classes={"immutable": True}, exceptions={"names": "*Error"}),
                 [], id="exceptions are never held to immutable"),
    pytest.param(holding(classes={"immutable": True}), holding(classes={"immutable": True}, records={"names": "*Record"}),
                 [("holds.records.immutable", "", "the records of service need no longer be immutable records "
                                                  "(parts.service.holds.records.immutable)")],
                 id="records held to immutable through classes, now listed without it"),
    pytest.param(holding(classes={"built_by": ["api"]}), holding(classes={}),
                 [("holds.classes.built_by", "", "the classes of service may be built by any part "
                                                 "(parts.service.holds.classes.built_by)")],
                 id="built_by dropped"),
    pytest.param(holding(classes={"built_by": ["api"]}), holding(classes={"built_by": ["api", "store"]}),
                 [("holds.classes.built_by", "store", "the classes of service may also be built by store "
                                                      "(parts.service.holds.classes.built_by)")],
                 id="a part added to built_by"),
    pytest.param(holding(classes={"built_by": ["api"]}), holding(classes={"built_by": ["api"]}), [],
                 id="built_by kept"),
    pytest.param(holding(classes={}), holding(classes={"built_by": ["api"]}), [], id="built_by newly written"),
])
def test_a_setting_of_a_kind_held_dropped_or_widened_is_looser(base, custom, found):
    assert loosened(parsed(custom), parsed(base)) == tuple(
        Loosened(key, "service", what, sentence) for key, what, sentence in found)


@pytest.mark.parametrize("base, custom, found", [
    pytest.param(given(layered(), "service", shared=3), layered(),
                 [("", "service is no longer held to be shared (parts.service.shared)")], id="dropped"),
    pytest.param(given(layered(), "service", shared=3), given(layered(), "service", shared=2),
                 [("2", "the public names of service need only 2 users, fewer than the profile it is compared with asks "
                        "(parts.service.shared)")], id="lowered"),
    pytest.param(given(layered(), "service", shared=2), given(layered(), "service", shared=3), [], id="raised"),
    pytest.param(given(layered(), "service", shared=3), given(layered(), "service", shared=3), [], id="kept"),
    pytest.param(layered(), given(layered(), "service", shared=2), [], id="newly set"),
])
def test_a_part_held_to_fewer_users_of_its_public_names_is_looser(base, custom, found):
    assert loosened(parsed(custom), parsed(base)) == tuple(
        Loosened("shared", "service", what, sentence) for what, sentence in found)


def test_a_part_that_pairs_with_none_is_compared_neither_on_what_it_holds_nor_on_how_widely_it_is_shared():
    custom = renamed(layered(), "api", "routes")
    moved(custom, "routes", "routes/")
    base = given(layered(), "api", shared=3, holds={"classes": {"names": "*Api"}})
    assert loosened(parsed(custom), parsed(base)) == ()


def tiered(**imports) -> dict:
    """BASE, its tier unit given the imports given besides its types_only."""
    return {**BASE, "tiers": {"unit": {**TIER, "imports": {"types_only": ["parts.store"], **imports}}}}


@pytest.mark.parametrize("base, custom, found", [
    pytest.param(tiered(must=["parts.core"]), tiered(),
                 [("", "the unit tests no longer have to reach any part (tiers.unit.imports.must)")], id="dropped"),
    pytest.param(tiered(must=["parts.core"]), tiered(must=["parts.core", "parts.store"]),
                 [("store", "the unit tests may also meet imports.must by reaching store (tiers.unit.imports.must)")],
                 id="a part added"),
    pytest.param(tiered(must=["parts.core"]), tiered(must=["parts.core"]), [], id="kept"),
    pytest.param(tiered(), tiered(must=["parts.core"]), [], id="newly written"),
])
def test_a_tier_whose_tests_may_reach_more_parts_to_meet_imports_must_is_looser(base, custom, found):
    assert loosened(parsed(custom), parsed(base)) == tuple(
        Loosened("tiers.imports.must", "unit", what, sentence) for what, sentence in found)


def test_a_tier_no_longer_plain_tables_is_looser_and_one_newly_plain_tables_is_not():
    assert loosened(parsed(covered()), parsed(plain())) == (
        Loosened("plain_tables", "unit", "", "the table tests of the unit tests may now branch (tiers.unit.plain_tables)"),)
    assert loosened(parsed(plain()), parsed(covered())) == ()


def test_a_tier_renamed_in_place_no_longer_plain_tables_is_said_under_its_new_name():
    base = plain()
    custom = covered()
    custom["tiers"] = {"logic" if name == "unit" else name: tier for name, tier in custom["tiers"].items()}
    part_of(custom, "service")["tests"] = "logic"
    assert loosened(parsed(custom), parsed(base)) == (
        Loosened("plain_tables", "logic", "", "the table tests of the logic tests may now branch (tiers.logic.plain_tables)"),)


def test_the_ways_a_part_holds_and_a_tier_reaches_are_listed_after_the_other_ways_of_each():
    base = tight()
    part_of(base, "api")["litmus"] = "Does it answer a request?"
    part_of(base, "service").update({"holds": {"classes": {"names": "*Service"}}, "shared": 3})
    base["tiers"]["unit"]["uses"] = {"apply_never": True}
    assert [(item.key, item.part, item.what) for item in loosened(parsed(covered()), parsed(base))] == [
        ("litmus", "api", ""), ("holds", "service", "functions"), ("holds.classes.names", "service", ""),
        ("shared", "service", ""), ("uses.apply_never", "unit", ""), ("tiers.imports.must", "unit", ""),
        ("plain_tables", "unit", "")]


@pytest.mark.parametrize("base, custom, key", [
    pytest.param(holding(classes={}), holding(), "holds", id="holds dropped as a whole"),
    pytest.param(holding(classes={"names": "*Service"}), holding(classes={}), "holds.classes.names",
                 id="a names setting dropped"),
    pytest.param(given(layered(), "service", shared=3), layered(), "shared", id="shared dropped"),
    pytest.param(reaching("api"), covered(), "tiers.imports.must", id="a tier's imports.must dropped"),
    pytest.param(plain(), covered(), "plain_tables", id="a tier's plain_tables dropped"),
])
def test_a_key_of_holds_shared_or_a_tier_one_side_drops_is_comparable_and_listed_looser(base, custom, key):
    origin = compared(parsed(custom), parsed(base))
    assert origin.match == 1.0
    assert [item.key for item in origin.looser] == [key]


def test_a_profile_based_on_a_profile_file_excuses_only_the_guards_the_anchor_and_every_file_of_the_chain_leave_off():
    mine = replace(parsed(layered(guards={"no-comments": {}})), based_on="team.yaml")
    team = parsed(layered(based_on="cli", guards={"private-imports": {}}))
    origin = origin_of("mine.yaml", mine, False, {"cli": parsed(layered(guards={"closed-tree": {}}))}, chain=(team,))
    assert (origin.compared, origin.chosen_by, origin.anchor) == ("team.yaml", "based_on", "cli")
    assert origin.baseline_off == tuple(g for g in ORDER if g not in {"no-comments", "closed-tree", "private-imports"})


def test_a_chain_no_bundled_profile_pairs_with_rests_on_none_and_excuses_no_guard():
    mine = replace(parsed(layered()), based_on="team.yaml")
    origin = origin_of("mine.yaml", mine, False, {"cli": bare(web="web")}, chain=(bare(x="x"),))
    assert (origin.compared, origin.chosen_by, origin.anchor, origin.baseline_off) == ("team.yaml", "based_on", None, ())
    assert origin.low is True


def test_a_part_the_anchor_gives_a_litmus_is_listed_once_after_the_ways_it_is_looser_than_the_file():
    anchor = layered()
    part_of(anchor, "api")["litmus"] = "Does it answer a request?"
    part_of(anchor, "service")["litmus"] = "Does it decide?"
    team = layered(based_on="cli")
    part_of(team, "api")["litmus"] = "Does it answer a request?"
    mine = replace(parsed(layered()), based_on="team.yaml")
    origin = origin_of("mine.yaml", mine, False, {"cli": parsed(anchor)}, chain=(parsed(team),))
    assert origin.looser == (
        Loosened("litmus", "api", "",
                 "api has no litmus, though the profile it is compared with gives it one (parts.api.litmus)"),
        Loosened("litmus", "service", "cli",
                 "service has no litmus, though cli, which --strict rests on, gives the part it pairs with one "
                 "(parts.service.litmus)"))


def test_the_profile_file_based_on_names_is_never_said_to_match_higher_and_a_bundled_one_of_higher_match_is():
    mine = replace(bare(a="a", b="b", c="c"), based_on="team.yaml")
    low = origin_of("mine.yaml", mine, False, {"near": bare(a="a", b="b", c="c")}, chain=(bare(a="a"),))
    assert (low.compared, low.higher) == ("team.yaml", ("near", 1.0))
    high = origin_of("mine.yaml", mine, False, {"far": bare(a="a")}, chain=(bare(a="a", b="b", c="c"),))
    assert (high.compared, high.match, high.higher) == ("team.yaml", 1.0, None)


def test_a_profile_compared_with_a_bundled_one_rests_on_it_and_any_other_rests_on_none():
    mine = bare(a="a", b="b", c="c")
    bundled = {"alpha": bare(a="a", b="b", c="c"), "beta": bare(a="a")}
    assert origin_of("mine.yaml", replace(mine, based_on="beta"), False, bundled).anchor == "beta"
    assert origin_of("mine.yaml", mine, False, bundled).anchor == "alpha"
    assert origin_of("mine.yaml", mine, False, {"other": bare(web="web")}).anchor is None
    assert origin_of("alpha", mine, True, {}).anchor is None
    assert origin_of("mine.yaml", mine, False, {"alpha": bare(a="a")}, against="alpha").anchor is None


BESIDE = Loosened("testing.beside", "", "",
                  "tests may sit beside the code: the mirrored tests tree is no longer checked (testing.beside)")


def near(beside: bool | None) -> Architecture:
    """covered(), its testing saying beside as given (None: not at all)."""
    document = covered()
    if beside is not None:
        document["testing"]["beside"] = beside
    return parsed(document)


def test_a_profile_whose_tests_sit_beside_the_code_is_looser_than_one_whose_tests_mirror_it():
    assert loosened(near(True), near(None)) == (BESIDE,)
    assert loosened(near(True), near(False)) == (BESIDE,)


@pytest.mark.parametrize("custom, base", [
    pytest.param(True, True, id="both beside"),
    pytest.param(False, True, id="beside dropped"),
    pytest.param(None, None, id="neither"),
])
def test_beside_is_looser_only_where_the_compared_profile_leaves_it_out(custom, base):
    assert loosened(near(custom), near(base)) == ()


def test_a_profile_with_no_testing_compared_with_one_beside_is_not_looser_by_beside():
    assert "testing.beside" not in [item.key for item in loosened(parsed(layered()), near(True))]
