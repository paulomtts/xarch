"""An eval of the profile's own as rules reads it: made into a rule that lists each fact it reads (a filter that is no
word of the vocabulary refused at the eval's address), the facts it reads in a small project of files, how each is
named, and an example file in which it reads nothing named at its address."""
from tests.modules.rules.builders import profile
from xarch.modules.rules.application.logic.asked import made, named, project, span, unread
from xarch.modules.rules.application.logic.engine import kept
from xarch.modules.rules.domain.published import Piece
from xarch.modules.rules.domain.rule import Fact
from xarch.modules.rules.domain.values import Asked, Class, Function, SourceFile
from xarch.profile_values.checks import APP, Condition, Scope

DOMAIN = "modules/docs/domain/x.py"
CODE = SourceFile("", (), (), functions=(Function(2, "publish", owner="Document"), Function(5, "_check")),
                  classes=(Class(1, "Document"),))


def test_an_eval_is_made_into_a_rule_of_its_kind_scope_and_filters():
    rule, problems = made("rule", Asked("function", Scope(APP, "domain"), (Condition("public"),)))
    assert problems == [] and rule is not None
    assert (rule.facts, rule.scope, rule.keep, rule.key) == (("function",), Scope(APP, "domain"),
                                                            (Condition("public"),), "evals.rule")


def test_a_filter_that_is_no_word_of_the_vocabulary_is_a_problem_at_the_eval_address():
    rule, problems = made("rule", Asked("class", Scope(), (Condition("publc"),)))
    assert rule is None and problems == ["evals.rule.keep: no filter is named 'publc': did you mean public or placed?"]


def test_the_facts_an_eval_reads_in_a_small_project_are_those_of_its_kind_that_pass_its_filters():
    rule, _ = made("rule", Asked("function", Scope(APP, "domain"), (Condition("public"),)))
    assert rule is not None
    facts = project([(DOMAIN, CODE)], profile(), "app", (rule,))
    assert [(fact.line, named(fact)) for _, fact in kept(rule, facts, profile())] == [(2, "Document.publish")]


def test_a_method_is_named_by_its_class_and_its_name_a_file_whole_by_nothing():
    assert named(Fact("function", 2, ("Document", "publish"), "publish")) == "Document.publish"
    assert named(Fact("class", 1, (), "Document")) == "Document"
    assert named(Fact("file", 0)) == ""


def test_an_example_file_in_which_the_eval_reads_nothing_is_named_at_its_address():
    rule, _ = made("rule", Asked("class", Scope(APP, "domain")))
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
