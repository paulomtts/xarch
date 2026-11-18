"""Where else a file could lie by the profile's `holds`: each file asked of read as if it lay in each part that lists
`holds`, by the rule `check` runs there, on the facts of a small project; a file of another part, a test and a file
not asked of are not answered."""
import pytest

from tests.modules.rules.builders import profile
from xarch.modules.rules.application.logic.asked import project
from xarch.modules.rules.application.logic.elsewhere import broken, reading
from xarch.modules.rules.domain.parsed import Class, Function, SourceFile
from xarch.profile_values.checks import ANY

HOLDS = profile(holds={"domain": "classes", "logic": "functions"})
FUNCTIONS = SourceFile("", (), (), functions=(Function(1, "validate"),))
PRIVATE = SourceFile("", (), (), functions=(Function(1, "_validate"),))
CLASSES = SourceFile("", (), (), classes=(Class(1, "Document"),))
EXCEPTION = SourceFile("", (), (), classes=(Class(1, "Refused", exception=True),))
DOMAIN, LOGIC, KERNEL = "modules/docs/domain/x.py", "modules/docs/application/logic/x.py", "kernel/x.py"


def test_the_facts_a_file_is_read_with_are_those_of_each_holds_rule_in_every_part():
    assert [(rule.scope.part, rule.facts) for rule in reading(HOLDS)] == [(ANY, ("function",)), (ANY, ("class",))]


@pytest.mark.parametrize("path, file, parts", [
    pytest.param(KERNEL, FUNCTIONS, ("domain",), id="a public function breaks a part of classes, from any part"),
    pytest.param(KERNEL, PRIVATE, (), id="a private function breaks no part"),
    pytest.param(LOGIC, CLASSES, ("logic",), id="a class breaks a part of functions, its own too"),
    pytest.param(DOMAIN, EXCEPTION, (), id="an exception breaks no part of functions"),
])
def test_a_file_breaks_the_holds_of_each_part_it_would_break_were_it_there(path, file, parts):
    facts = project([(path, file)], HOLDS, "app", reading(HOLDS))
    assert broken(facts, HOLDS, frozenset({path})) == {path: parts}


def test_only_the_files_asked_of_are_answered():
    facts = project([(DOMAIN, CLASSES), (LOGIC, FUNCTIONS)], HOLDS, "app", reading(HOLDS))
    assert broken(facts, HOLDS, frozenset({LOGIC})) == {LOGIC: ("domain",)}
