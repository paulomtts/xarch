"""The checks a profile writes itself, made into rules: each target resolved by its kind (a place by the target grammar,
a dotted name into its steps, a part checked against the profile), the check refused with every problem at once when
a word does not apply, a place or a part is not the profile's, or the language lacks a fact it needs; and listed as
approximate when the language supplies one of its facts only partly."""
import pytest

from tests.modules.rules.builders import profile
from xarch.modules.rules.application.logic.own_checks import approximate, own, resolved
from xarch.modules.rules.domain.errors import ChecksRefused
from xarch.modules.rules.domain.rule import MAY_NOT, Match, Rule
from xarch.profile_values.capabilities import EXACT, Shortfall, Supply
from xarch.profile_values.checks import APP, Condition, Quantified, Saying, Scope, WrittenCheck, WrittenTarget
from xarch.profile_values.language import CheckedLanguage
from xarch.profile_values.placement import Target

SUPPLIES = CheckedLanguage("Toy", supplies=(Supply("call", EXACT), Supply("import", "partial", "no star imports"),
                                            Supply("file", EXACT)))
PROFILE = profile(language=SUPPLIES)
CHECK = WrittenCheck(("call",), Scope(APP, "kernel"),
                     Quantified(MAY_NOT, (WrittenTarget("path", ("app.api", ".run()")), WrittenTarget("part", ("web",)))),
                     (Saying("c", "f", (Condition("of-kind", "call"),)), Saying("{where} calls {path}", "do not",
                                                                              once=("line",))),
                     keep=(Condition("target-placed"),), flagged=(("kernel/a.py", "x()\n"),), clean=(("kernel/b.py", "\n"),))


def test_a_check_the_profile_writes_becomes_a_rule_with_its_examples_and_its_key():
    (check,) = own({"no-api": CHECK}, PROFILE)
    assert check.rule == Rule("no-api", Scope(APP, "kernel"), ("call",), MAY_NOT,
                              (Match("path", names=(("app", "api"), ("", "run()"))), Match("part", words=("web",))),
                              (Saying("c", "f", (Condition("of-kind", "call"),)),
                               Saying("{where} calls {path}", "do not", once=("line",))),
                              keep=(Condition("target-placed"),), key="checks.no-api")
    assert (check.flagged, check.clean) == ((("kernel/a.py", "x()\n"),), (("kernel/b.py", "\n"),))


def test_a_place_is_read_by_the_target_grammar_from_the_part_the_scope_names():
    placed = WrittenCheck(("import-into-app",), Scope(APP, "services"),
                          Quantified(MAY_NOT, (WrittenTarget("place", ("domain/values", "kernel")),)),
                          (Saying("m", "f"),))
    (check,) = own({"placed": placed}, profile())
    assert check.rule.targets == (Match("place", places=(Target("domain", "own", ("values",)), Target("kernel"))),)


def test_a_check_whose_words_do_not_apply_or_whose_places_and_parts_are_not_the_profile_s_is_refused_at_once():
    bad = WrittenCheck(("call",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("m", "f"),),
                       keep=(Condition("publc"),), mode="fial")
    nowhere = WrittenCheck(("import",), Scope(), Quantified(MAY_NOT, (WrittenTarget("place", ("nowhere",)),
                                                                     WrittenTarget("part", ("ghost",)))),
                           (Saying("m", "f"),))
    lacking = WrittenCheck(("class",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("{name}", "f"),))
    with pytest.raises(ChecksRefused) as refused:
        own({"no-api": bad, "nowhere": nowhere, "named": lacking}, PROFILE)
    assert refused.value.problems == (
        "checks.no-api.keep: no filter is named 'publc': did you mean public or placed?",
        "checks.no-api.mode: is 'fial': write fail (a finding fails the check) or list (it is listed as weak and fails "
        "only `check --strict`)",
        "checks.nowhere.may_not.place: 'nowhere' names no part 'nowhere'",
        "checks.nowhere.may_not.part: no part named 'ghost'",
        "checks.named: needs class (the classes a file defines at the top level: name, bases, line), which the reader "
        "of Toy does not supply: read another kind of fact, or drop the check")


def test_a_check_that_reads_a_fact_the_language_supplies_partly_is_approximate():
    importing = WrittenCheck(("import",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)),
                             (Saying("{package}", "f"),))
    checks = own({"imports": importing}, PROFILE)
    assert approximate(checks, SUPPLIES) == (Shortfall("checks.imports", "import", "no star imports"),)


def test_a_profile_resolved_holds_its_checks_as_rules_and_their_approximate_keys():
    importing = WrittenCheck(("import",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)),
                             (Saying("{package}", "f"),))
    done = resolved(profile(language=SUPPLIES, written={"imports": importing}))
    assert ([check.rule.id for check in done.checks], done.approximate) == (
        ["imports"], (Shortfall("checks.imports", "import", "no star imports"),))
