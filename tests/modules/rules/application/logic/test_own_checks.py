"""The checks a profile writes itself, made into rules: each target resolved by its kind (a place by the target grammar,
a dotted name into its steps, a part checked against the profile), the check refused with every problem at once when
a word does not apply, a place or a part is not the profile's, or the language lacks a fact it needs, while each that
can be made is made all the same when every problem of the others is listed; listed as approximate when the language
supplies one of its facts only partly; and what is wrong with how one holds to its examples."""
from dataclasses import replace

import pytest

from tests.modules.rules.builders import profile
from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic.own_checks import held_problems, made, placed, resolved
from xarch.modules.rules.domain.errors import ChecksRefused
from xarch.modules.rules.domain.rule import MAY_NOT, MadeChecks, Match, OwnCheck, Rule
from xarch.profile_values.capabilities import EXACT, Shortfall, Supply
from xarch.profile_values.checks import APP, Condition, Quantified, Saying, Scope, WrittenCheck, WrittenTarget
from xarch.profile_values.language import CheckedLanguage
from xarch.profile_values.placement import Target

SUPPLIES = CheckedLanguage("Toy", supplies=(Supply("call", EXACT), Supply("import.resolved", EXACT),
                                            Supply("import", "partial", "no star imports"), Supply("file", EXACT)),
                           member=".")
PROFILE = profile(language=SUPPLIES)
CHECK = WrittenCheck(("call",), Scope(APP, "kernel"),
                     Quantified(MAY_NOT, (WrittenTarget("path", ("app.api", ".run()")), WrittenTarget("part", ("web",)))),
                     (Saying("c", "f", (Condition("of-kind", "call"),)), Saying("{where} calls {path}", "do not",
                                                                              once=("line",))),
                     keep=(Condition("target-placed"),), flagged=(("kernel/a.py", "x()\n"),), clean=(("kernel/b.py", "\n"),))


def test_a_check_the_profile_writes_becomes_a_rule_with_its_examples_and_its_key():
    rule = Rule("no-api", Scope(APP, "kernel"), ("call",), MAY_NOT,
                (Match("path", names=(("app", "api"), ("", "run()"))), Match("part", words=("web",))),
                (Saying("c", "f", (Condition("of-kind", "call"),)), Saying("{where} calls {path}", "do not", once=("line",))),
                keep=(Condition("target-placed"),), key="checks.no-api")
    assert resolved(profile(language=SUPPLIES, written={"no-api": CHECK})).checks == (
        OwnCheck(rule, (("kernel/a.py", "x()\n"),), (("kernel/b.py", "\n"),)),)


def test_a_place_in_an_old_form_is_refused_with_the_reference_the_part_the_scope_names_would_write():
    placed = WrittenCheck(("import-into-app",), Scope(APP, "services"),
                          Quantified(MAY_NOT, (WrittenTarget("place", ("domain/values", "kernel@any")),)),
                          (Saying("m", "f"),))
    with pytest.raises(ChecksRefused) as refused:
        resolved(profile(written={"placed": placed}))
    assert refused.value.problems == (
        "checks.placed.may_not.place: 'domain/values': a bare part name was removed in 0.3.0: write "
        "module.domain/values (this module's) or parts.domain/values (any module's)",
        "checks.placed.may_not.place: 'kernel@any': @any was removed in 0.3.0: write parts.kernel")


def test_a_place_reads_a_reference_with_the_words_of_the_profile_s_repeating_folders():
    placed = WrittenCheck(("import-into-app",), Scope(APP, "services"),
                          Quantified(MAY_NOT, (WrittenTarget("place", ("parts.kernel", "module.domain/values")),)),
                          (Saying("m", "f"),))
    (check,) = resolved(profile(written={"placed": placed})).checks
    assert check.rule.targets == (Match("place", places=(Target("kernel"), Target("domain", "own", ("values",)))),)


def test_a_dotted_name_of_code_written_as_a_place_is_told_it_goes_under_path():
    dotted = WrittenCheck(("import-into-app",), Scope(APP, "services"),
                          Quantified(MAY_NOT, (WrittenTarget("place", ("os.environ",)),)), (Saying("m", "f"),))
    with pytest.raises(ChecksRefused) as refused:
        resolved(profile(written={"dotted": dotted}))
    assert refused.value.problems == (
        "checks.dotted.may_not.place: 'os.environ': 'os' is neither parts nor a word of this profile (module): a "
        "profile names no instance; write parts.<part> or <word>.<part>; a dotted name of code goes under path",)


def test_a_check_whose_words_do_not_apply_or_whose_places_and_parts_are_not_the_profile_s_is_refused_at_once():
    bad = WrittenCheck(("call",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("m", "f"),),
                       keep=(Condition("publc"),), mode="fial")
    nowhere = WrittenCheck(("import",), Scope(), Quantified(MAY_NOT, (WrittenTarget("place", ("nowhere",)),
                                                                     WrittenTarget("part", ("ghost",)))),
                           (Saying("m", "f"),))
    lacking = WrittenCheck(("class",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("{name}", "f"),))
    with pytest.raises(ChecksRefused) as refused:
        resolved(profile(language=SUPPLIES, written={"no-api": bad, "nowhere": nowhere, "named": lacking}))
    assert refused.value.problems == (
        "checks.no-api.keep: no filter is named 'publc': did you mean public or placed?",
        "checks.no-api.mode: is 'fial': write fail (a finding fails the check) or list (it is listed as weak and fails "
        "only `check --strict`)",
        "checks.nowhere.may_not.place: 'nowhere' names no part 'nowhere'",
        "checks.nowhere.may_not.part: no part named 'ghost'",
        "checks.named: needs class (the classes a file defines at the top level: name, bases, line), which the reader "
        "of Toy does not supply: read another kind of fact, or drop the check")


CALLS = WrittenCheck(("call",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("m", "f"),),
                     flagged=(("a.py", "x()\n"),))
CALLS_RULE = Rule("calls", Scope(), ("call",), MAY_NOT, (Match("exist"),), (Saying("m", "f"),), key="checks.calls")
MISSPELT = WrittenCheck(("call",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("m", "f"),),
                        keep=(Condition("publc"),))
NAMED = WrittenCheck(("class",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("{name}", "f"),))
LACKING = ("checks.named: needs class (the classes a file defines at the top level: name, bases, line), which the "
           "reader of Toy does not supply: read another kind of fact, or drop the check")


@pytest.mark.parametrize("written, then", [
    pytest.param({}, MadeChecks((), ()), id="a profile with no check of its own makes none"),
    pytest.param({"calls": CALLS}, MadeChecks((OwnCheck(CALLS_RULE, (("a.py", "x()\n"),)),), ()),
                 id="a check written in words that apply is made, with its examples"),
    pytest.param({"misspelt": MISSPELT, "calls": CALLS},
                 MadeChecks((OwnCheck(CALLS_RULE, (("a.py", "x()\n"),)),),
                            ("checks.misspelt.keep: no filter is named 'publc': did you mean public or placed?",)),
                 id="a check that cannot be made is listed with its problems, and the others are made all the same"),
    pytest.param({"named": NAMED, "calls": CALLS}, MadeChecks((OwnCheck(CALLS_RULE, (("a.py", "x()\n"),)),), (LACKING,)),
                 id="a check that needs a fact the reader does not supply is not made"),
    pytest.param({"named": NAMED, "misspelt": MISSPELT},
                 MadeChecks((), (LACKING, "checks.misspelt.keep: no filter is named 'publc': did you mean public or "
                                          "placed?")),
                 id="the problems of the checks that cannot be made are in the profile's order"),
])
def test_made_makes_each_check_it_can_and_lists_the_problems_of_the_others(written, then):
    assert made(written, PROFILE) == then


def test_a_check_that_reads_a_fact_the_language_supplies_partly_is_approximate_after_the_profile_s_own_keys():
    importing = WrittenCheck(("import",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)),
                             (Saying("{package}", "f"),))
    keyed = Shortfall("parts.kernel.names", "class", "a class defined in a branch is not read")
    done = resolved(profile(language=SUPPLIES, approximate=(keyed,), written={"imports": importing}))
    assert done.approximate == (keyed, Shortfall("checks.imports", "import", "no star imports"))


def test_a_profile_resolved_holds_its_checks_as_rules_and_their_approximate_keys():
    importing = WrittenCheck(("import",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)),
                             (Saying("{package}", "f"),))
    done = resolved(profile(language=SUPPLIES, written={"imports": importing}))
    assert ([check.rule.id for check in done.checks], done.approximate) == (
        ["imports"], (Shortfall("checks.imports", "import", "no star imports"),))


FOUND = Violation("app/a.py", 3, "a finding", "names", "f")


@pytest.mark.parametrize("flagged, clean, problems", [
    pytest.param([FOUND], [], [], id="something found in the flagged code, nothing in the clean code"),
    pytest.param([], [], ["checks.mine.examples.flagged: the check finds nothing in it: make the code hold what the "
                          "check is written to find, or correct the check"], id="nothing found in the flagged code"),
    pytest.param([FOUND], [FOUND, FOUND], ["checks.mine.examples.clean: the check finds 2 in it, the first app/a.py:3: "
                                           "a finding: make the code clean, or correct the check"],
                 id="something found in the clean code, said by the first"),
])
def test_a_check_holds_to_its_examples_when_it_finds_something_flagged_and_nothing_clean(flagged, clean, problems):
    assert held_problems("mine", flagged, clean) == problems


@pytest.mark.parametrize("path, placement", [
    pytest.param("kernel/x.py", (("app", "kernel", "x.py"), ("kernel", "x.py"), False),
                 id="a file of the app is shown below the app folder"),
    pytest.param("tests/kernel/test_x.py", (("tests", "kernel", "test_x.py"), ("kernel", "test_x.py"), True),
                 id="a file below the folder of the tests is test code, its steps below that folder"),
])
def test_a_file_of_a_checks_example_is_placed_in_the_app_or_the_tests(path, placement):
    assert placed(path, "app", "tests") == placement


def test_a_path_target_is_split_at_the_member_of_the_language_and_a_method_stays_a_method():
    hashed = replace(CHECK, quantified=Quantified(MAY_NOT, (WrittenTarget("path", ("node:fs#readFileSync", ".run()")),
                                                            WrittenTarget("part", ("web",)))))
    (own,) = resolved(profile(language=replace(SUPPLIES, member="#"), written={"no-api": hashed})).checks
    assert own.rule.targets[0].names == (("node:fs", "readFileSync"), ("", "run()"))


def test_an_own_check_that_reads_the_package_file_as_written_needs_the_language_to_have_one_and_negated_does_not():
    exempting = WrittenCheck(("import",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("m", "f"),),
                             exempt=(Condition("package-file"),))
    negated = replace(exempting, exempt=(Condition("package-file", negated=True),))
    rule = Rule("negated", Scope(), ("import",), MAY_NOT, (Match("exist"),), (Saying("m", "f"),),
                exempt=(Condition("package-file", negated=True),), key="checks.negated")
    assert made({"exempting": exempting, "negated": negated}, PROFILE) == MadeChecks(
        (OwnCheck(rule),),
        ("checks.exempting: needs file.package (a file stands for the folder that holds it), which the reader of Toy "
         "does not supply: read another kind of fact, or drop the check",))


TOPPING = WrittenCheck(("function",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), (Saying("{name}", "f"),),
                       keep=(Condition("top-level"),))
TOPPING_RULE = Rule("topping", Scope(), ("function",), MAY_NOT, (Match("exist"),), (Saying("{name}", "f"),),
                    keep=(Condition("top-level"),), key="checks.topping")


def test_an_own_check_that_reads_whether_a_function_is_at_the_top_level_needs_the_reader_to_say_it():
    untopped = CheckedLanguage("Toy", supplies=(Supply("function", EXACT),), member=".")
    topped = replace(untopped, supplies=(Supply("function", EXACT), Supply("function.top_level", EXACT)))
    assert made({"topping": TOPPING}, profile(language=untopped)) == MadeChecks((), (
        "checks.topping: needs function.top_level (whether a function is defined at the top level of its file, in no "
        "class), which the reader of Toy does not supply: read another kind of fact, or drop the check",))
    assert made({"topping": TOPPING}, profile(language=topped)) == MadeChecks((OwnCheck(TOPPING_RULE),), ())
