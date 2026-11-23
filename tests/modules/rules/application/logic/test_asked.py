"""An eval of the profile's own as rules reads it: made into a rule that lists each fact it reads (a filter that is no
word of the vocabulary, or a fact the language's reader does not supply, refused at the eval's address), the facts it
reads in a small project of files, how each is named, and an example file in which it reads nothing named at its
address."""
import pytest

from tests.modules.rules.builders import PYTHON, profile
from xarch.modules.rules.application.logic.asked import made, named, project, span, unread
from xarch.modules.rules.application.logic.engine import kept
from xarch.modules.rules.domain.parsed import Class, Function, SourceFile
from xarch.modules.rules.domain.profile import Asked
from xarch.modules.rules.domain.published import Piece
from xarch.modules.rules.domain.rule import Fact
from xarch.profile_values.capabilities import EXACT, Supply
from xarch.profile_values.checks import APP, Condition, Scope
from xarch.profile_values.language import CheckedLanguage

DOMAIN = "modules/docs/domain/x.py"
CODE = SourceFile("", (), (), functions=(Function(2, "publish", owner="Document"), Function(5, "_check", public=False)),
                  classes=(Class(1, "Document"),))


def test_an_eval_is_made_into_a_rule_of_its_kind_scope_and_filters():
    rule, problems = made("rule", Asked("function", Scope(APP, "domain"), (Condition("public"),)), PYTHON)
    assert problems == [] and rule is not None
    assert (rule.facts, rule.scope, rule.keep, rule.key) == (("function",), Scope(APP, "domain"),
                                                            (Condition("public"),), "evals.rule")


def test_a_filter_that_is_no_word_of_the_vocabulary_is_a_problem_at_the_eval_address():
    rule, problems = made("rule", Asked("class", Scope(), (Condition("publc"),)), PYTHON)
    assert rule is None and problems == ["evals.rule.keep: no filter is named 'publc': did you mean public or placed?"]


TOPPED = Asked("function", Scope(APP, "domain"), (Condition("top-level"),))
UNTOPPED = ("evals.rule: needs function.top_level (whether a function is defined at the top level of its file, in no "
            "class), which the reader of Toy does not supply: read another kind of fact, or drop the eval")
UNSAID = ("evals.rule: needs public (whether a name a file defines, or takes by an import, is for other files to use, "
          "as the language decides it), which the reader of Toy does not supply: read another kind of fact, or drop "
          "the eval")


def toy(*supplies: Supply) -> CheckedLanguage:
    return CheckedLanguage("Toy", supplies=(Supply("function", EXACT), *supplies), member=".")


@pytest.mark.parametrize("asked, language, problems", [
    pytest.param(TOPPED, toy(), [UNTOPPED], id="a fact the reader does not supply is refused at the eval's address"),
    pytest.param(Asked("function", Scope(APP, "domain"), (Condition("public"),)), toy(), [UNSAID],
                 id="any fact the eval reads, not only function.top_level"),
])
def test_an_eval_that_reads_a_fact_the_language_does_not_supply_is_not_made(asked, language, problems):
    assert made("rule", asked, language) == (None, problems)


@pytest.mark.parametrize("language", [
    pytest.param(toy(Supply("function.top_level", EXACT)), id="supplied exactly"),
    pytest.param(toy(Supply("function.top_level", "partial", "a function defined in a branch is not read")),
                 id="supplied partly: no problem"),
    pytest.param(CheckedLanguage("Toy", member="."), id="a language whose data file says nothing of its reader"),
])
def test_an_eval_whose_facts_the_language_supplies_or_does_not_grade_is_made(language):
    rule, problems = made("rule", TOPPED, language)
    assert problems == [] and rule is not None and "function.top_level" in rule.needs


def test_the_facts_an_eval_reads_in_a_small_project_are_those_of_its_kind_that_pass_its_filters():
    rule, _ = made("rule", Asked("function", Scope(APP, "domain"), (Condition("public"),)), PYTHON)
    assert rule is not None
    facts = project([(DOMAIN, CODE)], profile(), "app", (rule,))
    assert [(fact.line, named(fact)) for _, fact in kept(rule, facts, profile())] == [(2, "Document.publish")]


def test_a_method_is_named_by_its_class_and_its_name_a_file_whole_by_nothing():
    assert named(Fact("function", 2, ("Document", "publish"), "publish")) == "Document.publish"
    assert named(Fact("class", 1, (), "Document")) == "Document"
    assert named(Fact("file", 0)) == ""


def test_an_example_file_in_which_the_eval_reads_nothing_is_named_at_its_address():
    rule, _ = made("rule", Asked("class", Scope(APP, "domain")), PYTHON)
    assert rule is not None
    files = ((DOMAIN, ""), ("modules/docs/domain/y.py", ""))
    facts = project([(DOMAIN, CODE), ("modules/docs/domain/y.py", SourceFile("", (), ()))], profile(), "app", (rule,))
    assert unread("rule", "clean", files, kept(rule, facts, profile()), "class") == [
        "evals.rule.examples.clean.modules/docs/domain/y.py: holds no class the eval reads (in its scope, passing "
        "keep): give it one"]


def test_what_an_eval_reads_spans_the_lines_of_the_piece_of_its_name_around_its_line():
    pieces = (Piece("class", "Document", 1, 9), Piece("method", "publish", 2, 5, "Document"),
              Piece("function", "publish", 11, 14))
    assert span(Fact("function", 3, ("Document", "publish"), "publish"), pieces) == (2, 5)
    assert span(Fact("function", 12, ("publish",), "publish"), pieces) == (11, 14)
    assert span(Fact("class", 1, (), "Document"), pieces) == (1, 9)
    assert span(Fact("function", 20, ("lost",), "lost"), pieces) == (20, 20)
    assert span(Fact("file", 0), pieces) == (0, 0)
