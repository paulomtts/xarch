"""The top-level `evals` key: the line of each part placement reads a file's answer against
(`evals.placement.lines`), by part as written; the evals of the profile's own, each in its answer form; and every way
of writing either wrong refused at its address."""
import pytest

from tests.modules.spec.profiles import layered, parsed, problems
from xarch.modules.spec.domain.published import CHOICE, SCORE, YES_NO, Eval
from xarch.profile_values.checks import Condition, Scope


def test_a_profile_without_evals_sets_no_line_by_hand():
    assert parsed(layered()).lines == {}


def test_the_line_of_each_part_written_loads_by_part_in_the_order_of_the_file():
    architecture = parsed(layered(evals={"placement": {"lines": {"store": 0.2, "api": 0.45, "shared": 1e-1}}}))
    assert list(architecture.lines.items()) == [("store", 0.2), ("api", 0.45), ("shared", 0.1)]


def test_evals_with_placement_and_placement_with_no_lines_set_no_line():
    assert parsed(layered(evals={})).lines == {}
    assert parsed(layered(evals={"placement": {}})).lines == {}


NOT_A_LINE = "is not a line: write a number above 0 and below 1, such as 0.2"


@pytest.mark.parametrize("evals, problem", [
    pytest.param(["placement"], "evals: must be a mapping of the evals review asks, by id, such as "
                                "{placement: {lines: {documents: 0.2}}}", id="a list instead of a mapping"),
    pytest.param({"placement": {}, "Purity": {}}, "evals: 'Purity' is no id of an eval of your own, lowercase words "
                                                  "joined by - such as rule-outside-entity, nor a key of evals: use "
                                                  "placement", id="an id that is not one"),
    pytest.param({"placement": "on"}, "evals.placement: must be a mapping {lines, examples}: the line of each part, "
                                      "below which a file reads as doubtful there, and the examples it is held to "
                                      "besides the docs'", id="placement not a mapping"),
    pytest.param({"placement": {"line": 0.2}}, "evals.placement: unknown key 'line': use examples, lines",
                 id="an unknown slot"),
    pytest.param({"placement": {True: "x"}}, "evals.placement: unknown key 'yes': use examples, lines",
                 id="a slot of an eval of your own, which YAML reads yes as true, written under placement"),
    pytest.param({"placement": {"examples": {"clean": {"store/a.txt": "x"}}}},
                 "evals.placement.examples.clean: 'store/a.txt' is not a path of a source file below the app, ending in "
                 ".py", id="an example of placement that is no source file"),
    pytest.param({"placement": {"examples": {"flagged": {"stray/x.py": "x = 1\n"}}}},
                 "evals.placement.examples.flagged.stray/x.py: lies in no part of this profile: write the path of a "
                 "file in the part it is an example of", id="a flagged example of placement lying in no part"),
    pytest.param({"placement": {"examples": {"clean": {"stray/x.py": "x = 1\n"}}}},
                 "evals.placement.examples.clean.stray/x.py: lies in no part of this profile: write the path of a "
                 "file in the part it is an example of", id="a clean example of placement lying in no part"),
    pytest.param({"placement": {"lines": [0.2]}}, "evals.placement.lines: must be a mapping of parts to their line, "
                                                  "such as {documents: 0.2}", id="lines not a mapping"),
    pytest.param({"placement": {"lines": {"domain": 0.2}}}, "evals.placement.lines: 'domain' is not a part of this "
                                                            "profile: name a part under parts", id="a name that is no part"),
    pytest.param({"placement": {"lines": {"store": "low"}}}, f"evals.placement.lines.store: 'low' {NOT_A_LINE}",
                 id="a line that is no number"),
    pytest.param({"placement": {"lines": {"store": True}}}, f"evals.placement.lines.store: True {NOT_A_LINE}",
                 id="a boolean is no number"),
    pytest.param({"placement": {"lines": {"store": 0}}}, f"evals.placement.lines.store: 0 {NOT_A_LINE}",
                 id="a line of 0 would doubt nothing"),
    pytest.param({"placement": {"lines": {"store": 1}}}, f"evals.placement.lines.store: 1 {NOT_A_LINE}",
                 id="a line of 1 would doubt everything"),
    pytest.param({"placement": {"lines": {"store": -0.2}}}, f"evals.placement.lines.store: -0.2 {NOT_A_LINE}",
                 id="a line below 0"),
])
def test_evals_written_wrong_is_refused_at_its_address(evals, problem):
    assert f"layered.yaml: {problem}" in problems(layered(evals=evals))


CODE = "def run(doc):\n    return doc\n"
EXAMPLES = {"flagged": {"store/a.py": CODE, "store/b.py": CODE}, "clean": {"store/c.py": CODE, "store/d.py": CODE}}


def own(**changes) -> dict:
    """An eval of the profile's own, yes-no, reading functions of store, with what changes changed (None: left out)."""
    body = {"ask": "Does this function decide a rule of the document itself?", "answer": "yes-no",
            "reads": "function", "in": {"part": "store"}, "message": "{name} may decide it ({value})",
            "fix": "read it against the litmus of store", "examples": EXAMPLES} | changes
    return {"rule": {key: value for key, value in body.items() if value is not None}}


def test_a_yes_no_eval_loads_with_what_yes_and_no_mean_its_scope_and_its_examples_in_order():
    architecture = parsed(layered(evals=own(yes="it tests the fields", no="it asks the document", keep=["public"])))
    assert architecture.evals == {"rule": Eval(
        "Does this function decide a rule of the document itself?", YES_NO,
        (("yes", "it tests the fields"), ("no", "it asks the document")), ("yes",), "function", Scope(part="store"),
        (Condition("public"),), None, "{name} may decide it ({value})", "read it against the litmus of store",
        (("store/a.py", CODE), ("store/b.py", CODE)), (("store/c.py", CODE), ("store/d.py", CODE)))}


def test_a_yes_no_eval_that_does_not_say_what_yes_and_no_mean_sends_them_undescribed():
    assert parsed(layered(evals=own())).evals["rule"].options == (("yes", ""), ("no", ""))


def test_a_score_has_five_levels_named_0_to_4_and_flags_the_levels_from_flagged_from():
    levels = ["none", "a constant of its own", "a constant of another", "the clock", "it writes"]
    found = parsed(layered(evals=own(answer={"score": levels, "flagged_from": 3}, line=0.7))).evals["rule"]
    assert (found.form, found.options, found.flagged, found.line) == (
        SCORE, tuple((str(level), text) for level, text in enumerate(levels)), ("3", "4"), 0.7)


def test_a_choice_of_three_options_or_more_flags_the_options_listed():
    options = {"decides": "it decides the rule", "asks": "it asks the document", "none": "no rule is involved"}
    found = parsed(layered(evals=own(answer={"choice": options, "flagged": ["decides"]}))).evals["rule"]
    assert (found.form, found.options, found.flagged) == (CHOICE, tuple(options.items()), ("decides",))


def test_placement_is_no_eval_of_the_profile_own_and_an_eval_written_wrong_is_left_out():
    assert parsed(layered(evals={"placement": {"lines": {"store": 0.2}}})).evals == {}


LEVELS = ["a", "b", "c", "d", "e"]
VARIABLES = "use {file}, {line}, {name}, {value}"


@pytest.mark.parametrize("changes, problem", [
    pytest.param({"ask": None}, "evals.rule: missing `ask`", id="a slot it needs left out"),
    pytest.param({"colour": "red"}, "evals.rule: unknown key 'colour': use answer, ask, examples, fix, in, keep, line, "
                                    "message, no, reads, yes", id="an unknown slot"),
    pytest.param({"ask": "Is it? Or is it?"}, "evals.rule.ask: must be one short question about what the text shows: "
                 "one line, at most 400 characters and one question mark", id="a question of two questions"),
    pytest.param({"ask": "Does it decide the rule itself."}, "evals.rule.ask: must be one short question about what "
                 "the text shows: one line, at most 400 characters and one question mark", id="a question with no mark"),
    pytest.param({"ask": "x" * 401}, "evals.rule.ask: must be one short question about what the text shows: one line, "
                 "at most 400 characters and one question mark", id="a question over 400 characters"),
    pytest.param({"answer": "maybe"}, "evals.rule.answer: write yes-no, {score: [<5 levels>], flagged_from: <1 to 4>} "
                 "or {choice: {<option>: <description>, ...}, flagged: [<option>, ...]}", id="no answer form"),
    pytest.param({"answer": {"score": LEVELS[:4], "flagged_from": 2}}, "evals.rule.answer.score: must be five levels, "
                 "from 0 to 4, each a sentence saying what that level means, the worst last", id="a score of 4 levels"),
    pytest.param({"answer": {"score": LEVELS, "flagged_from": 0}}, "evals.rule.answer.flagged_from: must be the level "
                 "from which a reading counts as flagged, 1 to 4", id="flagged from level 0 flags everything"),
    pytest.param({"answer": {"choice": {"a": "x", "b": "y"}, "flagged": ["a"]}}, "evals.rule.answer.choice: two "
                 "options are a yes or no: write answer: yes-no, with yes: and no:", id="a choice of two options"),
    pytest.param({"answer": {"choice": {"a": "x", "b": "y", "c": "z"}, "flagged": ["a", "b", "c"]}},
                 "evals.rule.answer.flagged: must list the options that count as flagged: some of the options, not "
                 "all", id="every option flagged"),
    pytest.param({"answer": {"choice": {"a": "x", "b": "y", "c": "z"}, "flagged": ["d"]}},
                 "evals.rule.answer.flagged: must list the options that count as flagged: some of the options, not "
                 "all", id="a flagged option that is no option"),
    pytest.param({"answer": {"score": LEVELS, "flagged_from": 2}, "yes": "it does"},
                 "evals.rule.yes: only a yes-no answer says what yes means", id="yes said of a score"),
    pytest.param({"reads": "import"}, "evals.rule.reads: must be file, class or function: what one question is asked "
                                      "of", id="a kind of fact the eval does not read"),
    pytest.param({"in": {"part": "nowhere"}}, "evals.rule.in.part: no part named 'nowhere': write one of api, service, "
                                              "shared, store, or structure", id="a scope naming no part"),
    pytest.param({"in": {"files": "tests"}}, "evals.rule.in: review reads the app's files only: write part and where",
                 id="a scope of the tests"),
    pytest.param({"in": {"part": "structure"}}, "evals.rule.in.part: review reads the files of a part only: name a "
                                                "part", id="a scope of the structure"),
    pytest.param({"line": 1.5}, f"evals.rule.line: 1.5 {NOT_A_LINE.replace('0.2', '0.6')}", id="a line above 1"),
    pytest.param({"message": "{name} reads {score}"}, f"evals.rule.message: {{score}} is not a variable of an eval: "
                 f"{VARIABLES}", id="a variable an eval has none of"),
    pytest.param({"fix": ""}, "evals.rule.fix: must be a sentence, with {file}, {line}, {name}, {value} for what it "
                              "names", id="an empty fix"),
    pytest.param({"examples": {"flagged": {"store/a.py": CODE}, "clean": EXAMPLES["clean"]}},
                 "evals.rule.examples.flagged: must be a map of at least 2 files, {<path>: <code>}: the code the eval "
                 "must read as flagged", id="one flagged example"),
    pytest.param({"examples": {"flagged": EXAMPLES["flagged"], "clean": {"store/c.py": CODE, "store/notes.txt": CODE}}},
                 "evals.rule.examples.clean: 'store/notes.txt' is not a path of a source file below the app, ending "
                 "in .py", id="an example that is no source file"),
])
def test_an_eval_of_the_profile_own_written_wrong_is_refused_at_its_address(changes, problem):
    assert f"layered.yaml: {problem}" in problems(layered(evals=own(**changes)))


def test_yes_and_no_written_bare_in_a_profile_file_are_read_as_the_yes_and_no_slots():
    written = own()
    written["rule"] |= {True: "it tests the fields", False: "it asks the document"}
    assert parsed(layered(evals=written)).evals["rule"].options == (("yes", "it tests the fields"),
                                                                    ("no", "it asks the document"))


def test_placement_is_held_to_examples_of_its_own_besides_the_docs_flagged_or_clean_either_left_out():
    placed = {"flagged": {"src/documents/store/api.py": "def handle(request): ...\n"}}
    assert parsed(layered(evals={"placement": {"examples": placed}})).placed == (
        (("src/documents/store/api.py", "def handle(request): ...\n"),), ())
    assert parsed(layered()).placed == ((), ())
