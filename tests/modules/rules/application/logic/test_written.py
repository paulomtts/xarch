"""A rule written in the syntax a profile writes its checks in: each slot as the format writes it, a default left out,
a word quoted only where the format would read it otherwise, and the sayings but the last as cases."""
import pytest

from xarch.kernel.logic.language import LanguageView
from xarch.kernel.placement import Target
from xarch.modules.rules.application.logic.written import check, filled, written
from xarch.modules.rules.domain.rule import (
    EXISTING,
    LIST,
    MAY_NOT,
    MAY_ONLY,
    MUST_BE_REACHED,
    MUST_REACH,
    STRUCTURE,
    TESTS,
    Condition,
    Match,
    Rule,
    Saying,
    Scope,
)


def c(*texts: str) -> tuple[Condition, ...]:
    return tuple(Condition.of(text) for text in texts)


@pytest.mark.parametrize("rule, lines", [
    pytest.param(Rule("names", Scope(part="store"), ("class",), MAY_ONLY, (Match("name", words=("*Store",)),),
                      (Saying("{name} is not {targets}", "rename {name}"),), keep=c("public")),
                 ["read: class", "in: {part: store}", "keep: [public]", 'may_only: {name: ["*Store"]}',
                  'message: "{name} is not {targets}"', 'fix: "rename {name}"'], id="a check of a part"),
    pytest.param(Rule("x", Scope(TESTS, where=c("not tiered", "below fakes")), ("file",), MAY_NOT, EXISTING,
                      (Saying("m", "f"),), mode=LIST),
                 ["read: file", "in: {files: tests, where: [not tiered, {below: fakes}]}", "may_not: exist",
                  "mode: list", 'message: "m"', 'fix: "f"'], id="a scope of the tests, its filters and a mode"),
    pytest.param(Rule("x", Scope(part=STRUCTURE), ("use", "method-call"), MAY_NOT,
                      (Match("path", names=(("time", "time"), ("", "absolute()"))),),
                      (Saying("{where} reads {hit}", "f", c("of-kind use"), ("line",)), Saying("m", "f"))),
                 ["read: [use, method-call]", "in: {part: structure}", 'may_not: {path: [time.time, ".absolute()"]}',
                  "cases:", "  - when: [{of-kind: use}]", '    message: "{where} reads {hit}"', '    fix: "f"',
                  "    once_per: [line]", 'message: "m"', 'fix: "f"'], id="dotted names, a method, and a case"),
    pytest.param(Rule("x", Scope(part="store"), ("import", "import-into-app"), MUST_REACH,
                      (Match("place", places=(Target("core"), Target("api", "any", ("v1",)))), Match("outside")),
                      (Saying("m", "f"),), links=("import-into-app",), via=c("target-in-own-part")),
                 ["read: [import, import-into-app]", "in: {part: store}", "must_reach:",
                  "  targets: [{place: [core, api@any/v1]}, outside]", "  through: import-into-app",
                  "  through_only: [target-in-own-part]", 'message: "m"', 'fix: "f"'], id="a reach to targets"),
    pytest.param(Rule("x", Scope(part="ports"), ("class",), MUST_BE_REACHED, EXISTING, (Saying("{name}", "f"),),
                      keep=c("interface"), links=("names-mentioned",), roots=Scope(where=c("not package-file")),
                      spread=("class",), elsewhere=True),
                 ["read: class", "in: {part: ports}", "keep: [interface]", "must_be_reached:",
                  "  from: {files: app, where: [not package-file]}", "  through: names-mentioned", "  then_through: class",
                  "  by_another_file: true", 'message: "{name}"', 'fix: "f"'], id="a reach from roots"),
])
def test_a_rule_is_written_slot_by_slot_as_a_profile_writes_a_check(rule, lines):
    assert check(rule) == lines


def test_rules_are_written_as_the_checks_of_a_profile_each_under_its_id():
    rule = Rule("x", Scope(), ("comment",), MAY_NOT, EXISTING, (Saying('a "comment"', "f"),))
    assert written((rule, rule), ("one", "two")) == (
        'checks:\n  one:\n    read: comment\n    may_not: exist\n    message: "a \\"comment\\""\n    fix: "f"\n'
        '  two:\n    read: comment\n    may_not: exist\n    message: "a \\"comment\\""\n    fix: "f"\n')


@pytest.mark.parametrize("text, importing, written_out", [
    pytest.param("%import app.docs.rules trim%\n", "from {dotted} import {name}", "from app.docs.rules import trim\n",
                 id="the import token is written as the language imports a name"),
    pytest.param("%import app.docs.rules trim%\n", "", "%import app.docs.rules trim%\n",
                 id="a language that does not say how it imports leaves the token as written"),
    pytest.param("%comment% a note in notes%extension%", "", "# a note in notes.py", id="the other tokens as before"),
])
def test_the_tokens_of_the_language_are_filled_in(text, importing, written_out):
    assert filled(text, LanguageView(extension=".py", comment="#", importing=importing)) == written_out
