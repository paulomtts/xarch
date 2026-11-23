"""A rule holds its own invariants: it is refused when it is made with a word that does not exist, or one that does
not apply to what its slot reads, every problem at once, each named by the slot of the profile's syntax it is in and
with what to write. The rows marked (audit) are the crashes and wrong values a rule could cause before it held them:
a typo that silently listed a finding instead of failing it, a filter that matched nothing, a variable that printed
nothing or crashed."""
import pytest

from xarch.kernel.logic.conditions import condition
from xarch.modules.rules.domain.errors import RuleRefused
from xarch.modules.rules.domain.rule import EXISTING, MAY_NOT, MAY_ONLY, MUST_BE_REACHED, MUST_REACH, Match, Rule
from xarch.profile_values.checks import ALL, APP, TESTS, Condition, Saying, Scope

YAML = (Match("package", words=("yaml",)),)


def c(*texts: str) -> tuple[Condition, ...]:
    return tuple(condition(text) for text in texts)


def say(message: str = "m", fix: str = "f", *when: str, once: tuple[str, ...] = ()) -> tuple[Saying, ...]:
    return (Saying(message, fix, c(*when), once),)


def made(**changes) -> Rule:
    fields = {"id": "mine", "scope": Scope(APP, "store"), "facts": ("import",), "quantifier": MAY_NOT, "targets": YAML,
              "sayings": say("{package}")} | changes
    return Rule(**fields)


REACHED = {"quantifier": MUST_BE_REACHED, "targets": EXISTING, "facts": ("class",), "links": ("names-mentioned",),
           "roots": Scope(TESTS), "sayings": say("{name}")}


@pytest.mark.parametrize("changes, problems", [
    pytest.param({"mode": "fial"}, ["mode: is 'fial': write fail (a finding fails the check) or list (it is listed as "
                                    "weak and fails only `check --strict`)"], id="(audit) a typo in mode"),
    pytest.param({"keep": c("publc")}, ["keep: no filter is named 'publc': did you mean public or placed?"],
                 id="(audit) a filter no table holds, even when nothing is in scope"),
    pytest.param(REACHED | {"roots": None}, ["must_be_reached.from: is missing: write the files the reach starts from, as "
                                             "`in` writes a scope"], id="(audit) a reach from no roots"),
    pytest.param({"sayings": ()}, ["message: is missing: every check says what it found, and fix what to do about it"],
                 id="(audit) no message"),
    pytest.param({"sayings": say("m", "f", "relative")},
                 ["cases: the message and fix of the check itself hold when no case does, and take no `when`: move it "
                  "into a case"], id="(audit) a last message with a condition"),
    pytest.param({"sayings": (*say(), *say())},
                 ["cases[1].when: is missing: a case is said when its filters hold; write them, or make it the check's "
                  "own message"], id="a case with no condition"),
    pytest.param({"keep": c("target-placed"), "targets": EXISTING},
                 ["keep: target-placed does not apply to import: it reads place, which it does not carry; it applies to "
                  "call, construction, function-reference and import-into-app"],
                 id="(audit) a filter on a kind that lacks its field"),
    pytest.param({"quantifier": MAY_ONLY, "targets": EXISTING},
                 ["may_only: exist matches every fact, so nothing could be a finding under may_only: write it under "
                  "may_not, or name what to match"], id="(audit) every fact matching under may_only"),
    pytest.param({"targets": (Match("exist"), Match("outside"))}, ["may_not: exist matches every fact: write it alone"],
                 id="every fact matching beside another target"),
    pytest.param({"links": ("import-into-app",), "via": c("target-in-own-part")},
                 ["through: only a check under must_reach or must_be_reached reaches through links: drop it",
                  "through_only: only a check under must_reach or must_be_reached reaches through links: drop it"],
                 id="(audit) links on a rule that does not reach"),
    pytest.param({"facts": ("use",), "targets": EXISTING, "sayings": say("{written}")},
                 ["message: {written} prints nothing for use: it reads written; it applies to import and imported-name"],
                 id="(audit) a variable empty for the kind"),
    pytest.param({"facts": ("file",), "targets": EXISTING, "sayings": say("{library_owners}")},
                 ["message: {library_owners} prints nothing for file: it reads path; it applies to import, "
                  "imported-name, use, call, construction and function-reference"],
                 id="(audit) a variable that crashed on a kind with no path"),
    pytest.param({"facts": ("comment",), "targets": EXISTING, "sayings": say("{verb}")},
                 ["message: {verb} prints nothing for comment: it applies to import, imported-name, use, method-call, "
                  "call, construction, function-reference, import-into-app, import-into-tests and callback"],
                 id="(audit) the verb of a kind that names nothing"),
    pytest.param({"facts": ("function",), "targets": EXISTING, "sayings": say("{function}")},
                 ["message: {function} prints nothing for function: it reads function; it applies to callback"],
                 id="(audit) a variable that named the class of a function"),
    pytest.param({"scope": Scope(TESTS), "targets": EXISTING, "sayings": say("{where}")},
                 ["message: {where} applies only to the files of the app: write it in a check whose scope reads them "
                  "(`in: {files: app}`)"], id="(audit) the part of a test"),
    pytest.param({"scope": Scope(ALL), "targets": EXISTING, "sayings": say("{where}")},
                 ["message: {where} applies only to the files of the app: write it in a check whose scope reads them "
                  "(`in: {files: app}`)"], id="a variable of the app in a scope of both"),
    pytest.param({"scope": Scope(APP), "quantifier": MUST_REACH, "links": ("use",), "sayings": say("{file}")},
                 ["must_reach.through: use leads nowhere: write a kind that leads to a file or to names, one of "
                  "function-reference, import-into-app, import-into-tests"],
                 id="(audit) a link that reaches nothing"),
    pytest.param({"facts": ("use",), "quantifier": MUST_BE_REACHED, "targets": EXISTING, "links": ("names-mentioned",),
                  "roots": Scope(TESTS), "sayings": say("{line}")},
                 ["read: under must_be_reached, a fact is reached by its name, which use does not carry: read file, or "
                  "a kind that carries a name"], id="(audit) a reach by a name the kind does not carry"),
    pytest.param({"facts": ("use",), "quantifier": MAY_ONLY, "targets": (Match("path", names=(("a",),)),),
                  "exempt": c("reported-at-import"), "sayings": say()},
                 ["except: reported-at-import reads the target a fact matched, which only a check under may_not has"],
                 id="(audit) a filter of the hit under may_only"),
    pytest.param({"sayings": say(once=("weather",))},
                 ["once_per: no variable is named 'weather': did you mean where or tier or path?"],
                 id="(audit) a variable to say once by that does not exist"),
    pytest.param({"quantifier": MAY_ONLY, "sayings": say("{hit}")},
                 ["message: {hit} is the target a fact matched, which only a check under may_not has"],
                 id="(audit) the hit under may_only"),
    pytest.param({"targets": EXISTING, "sayings": say("{key}")},
                 ["message: {key} is the key the check comes from, and this one has none"], id="(audit) no key"),
    pytest.param({"scope": Scope(APP), "sayings": say("{scope_part}")},
                 ["message: {scope_part} is the part the scope names, and this scope names none: write "
                  "`in: {part: <part>}`"], id="(audit) no part"),
    pytest.param({"targets": EXISTING, "sayings": say("{targets}")},
                 ["message: {targets} prints the values of the targets, and no target of this check lists any"],
                 id="targets with no values"),
    pytest.param({"facts": ("imported-name",), "targets": EXISTING, "sayings": say("{name}")},
                 ["message: {name} prints something for imported-name only when takes-a-name holds: keep it "
                  "(`keep: [takes-a-name]`), or say it in a case `when: [takes-a-name]`"],
                 id="a field the kind carries only sometimes"),
    pytest.param({"sayings": say("{part}")}, ["message: {part} is no variable: it is called {where} now: write that"],
                 id="a variable that was called otherwise"),
    pytest.param({"sayings": say(once=("part",))},
                 ["once_per: no variable is named 'part': it is called {where} now: write that"],
                 id="a variable to say once by that was called otherwise"),
    pytest.param({"sayings": say("{weather}")}, ["message: {weather} is no variable: did you mean where or tier or path?"],
                 id="a variable no table holds"),
    pytest.param({"sayings": say("{line:>4}")}, ["message: {line:>4} is no variable: did you mean line or tier or name?"],
                 id="a format of a variable"),
    pytest.param({"sayings": say("{line")}, ["message: expected '}' before end of string: write each variable as {<name>}, "
                                             "and a brace of the text as {{ or }}"], id="a brace left open"),
    pytest.param({"sayings": say("m", " ")}, ["fix: is empty: say what to do about it"], id="an empty fix"),
    pytest.param({"facts": ("imports",)}, ["read: no kind of fact is named 'imports': did you mean import or "
                                           "imported-name or import-into-tests?"], id="a kind no table holds"),
    pytest.param({"facts": ("import-into-tests",), "targets": EXISTING, "sayings": say()},
                 ["read: import-into-tests is a fact of the tests only, and the scope reads the files of the app: write "
                  "`in: {files: tests}`"], id="a kind of the other side"),
    pytest.param({"scope": Scope(APP, where=c("public"))},
                 ["in.where: public is a filter about the fact, and `where` takes filters about the file: move it to "
                  "`keep` or `except`"], id="a filter of a fact in the scope"),
    pytest.param({"scope": Scope("everything")}, ["in.files: is 'everything': write app, tests or all"],
                 id="files no list holds"),
    pytest.param({"scope": Scope(APP, where=c("test"))},
                 ["in.where: test applies only to the files of the tests: write it in a check whose scope reads them "
                  "(`in: {files: tests}`)"], id="a filter of the other side"),
    pytest.param({"facts": ("class",), "keep": c("named"), "targets": EXISTING, "sayings": say()},
                 ["keep: named needs a value (pattern): write {named: <pattern>}"], id="a value missing"),
    pytest.param({"facts": ("class",), "keep": c("public x"), "targets": EXISTING, "sayings": say()},
                 ["keep: public takes no value: write it alone"], id="a value given to a filter that takes none"),
    pytest.param({"scope": Scope(APP, where=c("below ../x"))},
                 ["in.where: below '../x': write a folder below the root, such as fakes or units/docs"],
                 id="a folder that is no folder below the root"),
    pytest.param({"keep": c("of-kind imprt")}, ["keep: of-kind 'imprt': no kind of fact is named so: did you mean import "
                                                "or imported-name or import-into-app?"], id="a kind no table holds as a value"),
    pytest.param({"facts": ("construction",), "keep": c("target-allows-under may_import"), "targets": EXISTING,
                  "sayings": say()}, ["keep: target-allows-under 'may_import': write one of built_by"],
                 id="a key of a part that lists no parts"),
    pytest.param({"targets": (Match("packages", words=("yaml",)),)},
                 ["may_not: no kind of target is named 'packages': did you mean package or place?"],
                 id="a target no table holds"),
    pytest.param({"targets": (Match("path"),)},
                 ["may_not: path lists no values, so it matches nothing: write its values (dotted names) as "
                  "{path: [...]}"], id="a target with no values under may_not"),
    pytest.param({"targets": (Match("outside", words=("x",)),)}, ["may_not: outside takes no values: write it alone"],
                 id="values for a target that takes none"),
    pytest.param({"facts": ("comment",), "targets": YAML, "sayings": say()},
                 ["may_not: package does not apply to comment: it compares path; it applies to import, imported-name, "
                  "use, call, construction and function-reference",
                  "may_not: no target applies to comment, so a fact of it would never be a finding: add a target that "
                  "compares what it carries, or drop it from `read`"], id="a target that applies to no kind read"),
    pytest.param({"quantifier": "maybe"}, ["quantifier: no quantifier is named 'maybe': write one of may_not, may_only, "
                                           "must_be_reached, must_reach"], id="a quantifier no table holds"),
    pytest.param(REACHED | {"targets": YAML},
                 ["must_be_reached: takes no targets: what must be reached is what the check keeps"],
                 id="targets of a reach from roots"),
    pytest.param({"quantifier": MUST_REACH, "links": ("import-into-app",), "roots": Scope(TESTS), "sayings": say()},
                 ["must_reach.from: only a check under must_be_reached has it: drop it"], id="roots of a reach to targets"),
    pytest.param(REACHED | {"links": ()}, ["must_be_reached.through: names no kind of fact: write the kinds that link a "
                                           "root onwards, such as names-mentioned or import-into-app"], id="a reach through nothing"),
    pytest.param(REACHED | {"spread": ("use",)},
                 ["must_be_reached.then_through: use leads nowhere: write a kind that leads to a file or to names, one of "
                  "names-mentioned, function-reference, import-into-app, import-into-tests, class"], id="then_through through nothing"),
    pytest.param({"quantifier": MUST_REACH, "links": ("import-into-app",), "exempt": c("relative"), "sayings": say()},
                 ["except: relative does not apply to file: it reads relative, which it does not carry; it applies to "
                  "import and imported-name"], id="an exception of a reach to targets excuses a file"),
    pytest.param({"facts": ("import", "use"), "keep": c("standard"), "targets": EXISTING, "sayings": say("{line}")},
                 ["keep: standard drops every use, which never carries standard: read it in another check, or drop it "
                  "from `read`"], id="(audit) a filter kept that applies to only some of the kinds read"),
    pytest.param({"facts": ("import", "use", "comment"), "keep": c("relative"), "targets": EXISTING,
                  "sayings": say("{line}")},
                 ["keep: relative drops every use and comment, which never carries relative: read them in another "
                  "check, or drop them from `read`"], id="several kinds a filter kept drops"),
    pytest.param({"scope": Scope(APP), "facts": ("import", "import-into-app"), "quantifier": MUST_REACH,
                  "targets": (Match("outside"), Match("part", words=("store",))),
                  "links": ("import-into-app", "function-reference"), "via": c("takes-a-name"), "sayings": say()},
                 ["must_reach.through_only: takes-a-name drops every function-reference, which never carries name: "
                  "read it in another check, or drop it from `must_reach.through`"],
                 id="a filter a link passes that applies to only some of the kinds of link"),
    pytest.param({"keep": c("sunny"), "mode": "fial", "sayings": say("{weather}")},
                 ["keep: no filter is named 'sunny': write one of test, tiered, placed, package-file, mirrors-a-part, "
                  "may-import-everything, below, relative, standard, reserved, "
                  "listed-by-another-part, app-package, own-code, takes-a-name, on-own-object, public, special, named, top-level, "
                  "forwards, returns-an-attribute, exception, record, interface, immutable, receiver, annotated-callable, unreadable, "
                  "directive, no-statements, exceptions-only, reported-at-import, names-restricted, of-kind, target-placed, "
                  "target-inside-part, target-in-own-part, target-in-own-tier, target-test, target-below, "
                  "target-allows-under",
                  "mode: is 'fial': write fail (a finding fails the check) or list (it is listed as weak and fails only "
                  "`check --strict`)",
                  "message: {weather} is no variable: did you mean where or tier or path?"],
                 id="every problem at once"),
])
def test_a_rule_that_names_what_does_not_exist_or_does_not_apply_is_refused_with_every_problem(changes, problems):
    with pytest.raises(RuleRefused) as refused:
        made(**changes)
    assert (refused.value.rule, list(refused.value.problems)) == ("mine", problems)


def test_a_rule_whose_words_all_apply_is_made():
    assert made(sayings=say("{where} imports {package} at {line}")).problems() == []


@pytest.mark.parametrize("changes", [
    pytest.param({"facts": ("import", "use"), "keep": c("not standard")}, id="a filter kept negated"),
    pytest.param({"facts": ("import", "use"), "keep": c("placed")}, id="a filter about the file"),
    pytest.param({"facts": ("import", "use"), "exempt": c("standard")}, id="an exception, which only fails to excuse"),
    pytest.param({"facts": ("import", "use"), "sayings": (*say("a", "b", "standard"), *say("{line}"))},
                 id="a case, which only fails to be said"),
    pytest.param({"facts": ("import", "imported-name"), "keep": c("standard")}, id="a filter both kinds carry"),
])
def test_a_filter_that_applies_to_only_some_kinds_is_made_where_it_drops_no_kind_whole(changes):
    assert made(**({"targets": EXISTING, "sayings": say("{line}")} | changes)).problems() == []


def test_a_rule_needs_the_facts_of_its_kinds_and_of_the_fields_its_words_read():
    assert made(keep=c("not relative")).needs == ("import", "import.relative")
    assert made(facts=("class",), targets=EXISTING, exempt=c("exception"), sayings=say("{name}")).needs == (
        "class", "class.exception")


def test_a_filter_about_the_package_file_needs_the_language_to_have_one_unless_it_is_negated():
    assert made(exempt=c("package-file")).needs == ("import", "file.package")
    assert made(scope=Scope(APP, "store", where=c("not package-file"))).needs == ("import",)
    assert "file.package" in made(facts=("import-into-app",), targets=EXISTING, sayings=say("m"),
                                  keep=c("target-placed", "target-inside-part")).needs


def test_a_rule_names_every_filter_and_every_variable_it_is_written_with_in_slot_order():
    rule = made(scope=Scope(APP, "store", where=c("placed")), keep=c("not relative"), exempt=c("standard"),
                sayings=(*say("{package} in {line}", "drop {package}", "standard", once=("package",)), *say("{line}")))
    assert ([x.name for x in rule.conditions], rule.variables) == (
        ["placed", "relative", "standard", "standard"], ("package", "line", "package", "line", "package"))
