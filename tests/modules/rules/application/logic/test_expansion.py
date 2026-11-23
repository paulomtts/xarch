"""What each key of a profile expands to, as rules as data: one row per group of the book, each rule by its id, its
scope (files, part, tier, filters about the file), the kinds it reads, its quantifier and its kinds of target; a key
left out expands to no rule. Every rule is made, so none names a word the vocabulary does not hold or that does not
apply to what it reads."""
from dataclasses import replace

import pytest

from tests.modules.rules.builders import PROFILE
from xarch.modules.rules.application.logic import expansion
from xarch.modules.rules.domain.rule import Rule
from xarch.profile_values.checks import Condition
from xarch.profile_values.placement import Target

ON = replace(PROFILE, private_imports=True, closed_tree=True, dead_code=True, untested=True, tests_only=True,
             immutable={"logic": ("records",)},
             built_by={"services": ("bootstrap",)}, names={"services": {"classes": ("*Service",)}},
             no_callbacks=("domain",), holds={"domain": ("classes",), "logic": ("functions", "records", "exceptions")},
             must_import={"adapters": (Target("platform"),)},
             pass_through=("services",), types_only={"services": ("contract",)},
             tiers=tuple(replace(t, must_import=("domain",)) if t.name == "unit" else t for t in PROFILE.tiers))
OFF = replace(PROFILE, libraries=None, uses_never={}, tiers=(), package_only=(), no_comments=False, dead_code=False)


def written(condition: Condition) -> str:
    return " ".join(filter(None, ("not" if condition.negated else "", condition.name, condition.value)))


def shape(rule: Rule) -> str:
    scope = rule.scope
    where = f" where {', '.join(map(written, scope.where))}" if scope.where else ""
    tier = f"/{scope.tier}" if scope.tier else ""
    return (f"{rule.id}: {scope.files}/{scope.part or 'structure'}{tier}{where} read {', '.join(rule.facts)} "
            f"{rule.quantifier} {', '.join(m.kind for m in rule.targets)}")


@pytest.mark.parametrize("group, shapes", [
    pytest.param("syntax", ["syntax: all/* read syntax-error may_not exist"], id="syntax"),
    pytest.param("may-import", [*(f"may-import: app/{p} read import-into-app may_only permitted" for p in PROFILE.parts),
                                "may-import: app/structure read import-into-app may_only permitted"], id="may-import"),
    pytest.param("libraries", [f"libraries: app/{p} read import may_only package" for p in PROFILE.parts for _ in (0, 1)],
                 id="libraries"),
    pytest.param("never-use", ["never-use: app/domain read imported-name, use, method-call may_not path",
                               "never-use: tests/domain/unit where not below fakes read imported-name, use, method-call "
                               "may_not path"], id="never-use"),
    pytest.param("tiers", ["tiers: tests/* where not tiered, test, not below fakes read file may_not exist",
                           "tiers: tests/* where tiered read import-into-app may_only permitted",
                           "tiers: tests/* where tiered read import-into-tests may_only permitted"], id="tiers"),
    pytest.param("types-only tiers", ["types-only: tests/*/rendering read call, function-reference may_not part"],
                 id="types-only tiers"),
    pytest.param("package-only", ["package-only: all/* read import-into-app may_not part"], id="package-only"),
    pytest.param("types-only parts", ["types-only: app/services read call, function-reference may_not part"],
                 id="types-only parts"),
    pytest.param("no-callbacks", ["no-callbacks: app/domain read callback may_not exist"], id="no-callbacks"),
    pytest.param("names", ["names: app/services read class may_only name"], id="names"),
    pytest.param("built-by", ["built-by: app/* read construction may_not part"], id="built-by"),
    pytest.param("private-imports", ["private-imports: all/* read imported-name may_not exist"], id="private-imports"),
    pytest.param("no-comments", ["no-comments: all/* read comment may_not exist"], id="no-comments"),
    pytest.param("closed-tree", ["closed-tree: app/* where not placed read file may_not exist"], id="closed-tree"),
    pytest.param("holds", ["holds: app/domain where not package-file read function may_not exist",
                           "holds: app/logic where not package-file read class may_not exist"], id="holds"),
    pytest.param("immutable", ["immutable: app/logic where not package-file read class may_not exist"], id="immutable"),
    pytest.param("must-import", ["must-import: app/adapters read import, import-into-app must_reach place, outside"],
                 id="must-import"),
    pytest.param("must-import tiers", ["must-import: tests/*/unit where test read import-into-app must_reach part"],
                 id="must-import tiers"),
    pytest.param("dead-code", ["dead-code: app/ports read class must_be_reached exist",
                               "dead-code: tests/* where below fakes read class must_be_reached exist"], id="dead-code"),
    pytest.param("untested", ["dead-code: app/* where tiered read file must_be_reached exist"], id="untested"),
    pytest.param("tests-only", ["dead-code: app/* read class must_be_reached exist",
                                "dead-code: app/* read function must_be_reached exist"], id="tests-only"),
    pytest.param("pass-through", ["pass-through: app/services read function may_not exist"], id="pass-through"),
])
def test_each_group_of_the_book_expands_to_the_rules_its_keys_mean(group, shapes):
    assert [shape(rule) for rule in expansion.book(ON)[group]] == shapes


def test_a_profile_that_sets_no_key_of_a_check_expands_to_the_rules_every_profile_has_alone():
    assert {group for group, rules in expansion.book(OFF).items() if rules} == {"syntax", "may-import"}


def test_every_group_of_the_book_has_a_row():
    rows = {param.values[0] for param in
            test_each_group_of_the_book_expands_to_the_rules_its_keys_mean.pytestmark[0].args[1]}
    assert rows == set(expansion.book(ON))


def test_the_rules_that_read_whether_a_name_is_public_need_the_fact_and_those_of_ports_fakes_and_files_do_not():
    book = expansion.book(ON)
    assert {group: ["public" in rule.needs for rule in book[group]]
            for group in ("private-imports", "names", "holds", "tests-only")} == {
        "private-imports": [True], "names": [True], "holds": [True, False], "tests-only": [True, True]}
    assert book["dead-code"] and book["untested"]
    assert not any("public" in rule.needs for rule in (*book["dead-code"], *book["untested"]))


def test_the_rules_of_no_callbacks_are_keyed_by_the_guard_for_every_part():
    rules = expansion.book(replace(ON, no_callbacks=("domain", "logic")))["no-callbacks"]
    assert [(rule.scope.part, rule.key) for rule in rules] == [("domain", "guards.no-callbacks"),
                                                               ("logic", "guards.no-callbacks")]
