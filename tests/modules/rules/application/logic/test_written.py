"""A rule as the check a profile would write: its slots as the format holds them, its targets as written (places in
the target grammar, dotted names joined), a rule of reach with how it reaches; each under an id of its own; and the
tokens of the language filled into the examples."""
import pytest

from xarch.modules.rules.application.logic.written import check_of, filled, ids, written, written_own
from xarch.modules.rules.domain.rule import EXISTING, MAY_NOT, MUST_BE_REACHED, MUST_REACH, Match, OwnCheck, Rule
from xarch.profile_values.checks import Condition, Quantified, Saying, Scope, WrittenCheck, WrittenTarget
from xarch.profile_values.language import CheckedLanguage
from xarch.profile_values.placement import Target

SAID = (Saying("m", "f"),)


@pytest.mark.parametrize("rule, check", [
    pytest.param(Rule("x", Scope(part="store"), ("import", "import-into-app"), MUST_REACH,
                      (Match("place", places=(Target("core"), Target("api", "any", ("v1",)))), Match("outside")),
                      SAID, links=("import-into-app",), via=(Condition("target-in-own-part"),)),
                 WrittenCheck(("import", "import-into-app"), Scope(part="store"),
                              Quantified(MUST_REACH, (WrittenTarget("place", ("core", "api@any/v1")),
                                                      WrittenTarget("outside")),
                                         ("import-into-app",), (Condition("target-in-own-part"),)), SAID),
                 id="places in the target grammar, and how a rule reaches"),
    pytest.param(Rule("x", Scope(), ("use",), MAY_NOT, (Match("path", names=(("time", "time"), ("", "absolute()"))),),
                      SAID),
                 WrittenCheck(("use",), Scope(), Quantified(MAY_NOT, (WrittenTarget("path", ("time.time", ".absolute()")),)),
                              SAID), id="dotted names joined, a method with its dot"),
    pytest.param(Rule("x", Scope(), ("comment",), MAY_NOT, EXISTING, SAID),
                 WrittenCheck(("comment",), Scope(), Quantified(MAY_NOT, (WrittenTarget("exist"),)), SAID),
                 id="what every fact matches"),
    pytest.param(Rule("x", Scope(part="ports"), ("class",), MUST_BE_REACHED, EXISTING, SAID,
                      links=("names-mentioned",), roots=Scope(where=(Condition("package-file", negated=True),)),
                      spread=("class",), elsewhere=True),
                 WrittenCheck(("class",), Scope(part="ports"),
                              Quantified(MUST_BE_REACHED, (), ("names-mentioned",), (),
                                         Scope(where=(Condition("package-file", negated=True),)), ("class",), True), SAID),
                 id="a reach from roots, which names no target"),
])
def test_a_rule_is_the_check_a_profile_would_write(rule, check):
    assert check_of(rule) == check


def test_rules_written_as_checks_each_take_an_id_of_their_own():
    rule = Rule("names", Scope(part="store"), ("class",), MAY_NOT, EXISTING, SAID)
    other = Rule("names", Scope(), ("class",), MAY_NOT, EXISTING, SAID)
    assert ids([rule, rule, other]) == ["names-store", "names-store-2", "names"]
    assert list(written([rule, other])) == ["names-store", "names"]


def test_a_check_of_one_s_own_is_written_under_its_id_with_its_examples_filled_in():
    own = OwnCheck(Rule("no-todo", Scope(), ("comment",), MAY_NOT, EXISTING, SAID),
                   (("notes%extension%", "%comment% TODO\n"),), (("notes%extension%", "%comment% done\n"),))
    (shown,) = written_own((own,), CheckedLanguage(extension=".py", comment="#")).values()
    assert (shown.flagged, shown.clean) == ((("notes.py", "# TODO\n"),), (("notes.py", "# done\n"),))


@pytest.mark.parametrize("text, importing, written_out", [
    pytest.param("%import app.docs.rules trim%\n", "from {dotted} import {name}", "from app.docs.rules import trim\n",
                 id="the import token is written as the language imports a name"),
    pytest.param("%import app.docs.rules trim%\n", "", "%import app.docs.rules trim%\n",
                 id="a language that does not say how it imports leaves the token as written"),
    pytest.param("%comment% a note in notes%extension%", "", "# a note in notes.py", id="the other tokens as before"),
])
def test_the_tokens_of_the_language_are_filled_in(text, importing, written_out):
    assert filled(text, CheckedLanguage(extension=".py", comment="#", importing=importing)) == written_out
