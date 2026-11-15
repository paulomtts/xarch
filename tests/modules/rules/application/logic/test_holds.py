"""The holds check on hand-made source files: a file of a part that holds classes defines no public function at the
top level, and one of a part that holds functions no public class but an exception or a record a function returns;
each one is listed as weak, never as a violation."""
import pytest

from tests.modules.rules.builders import profile, source
from xarch.modules.rules.application.logic.holds import weak
from xarch.modules.rules.domain.values import Class, Function, Method, Weak

ON = profile(holds={"domain": "classes", "logic": "functions"})
DOMAIN = "modules/docs/domain/doc.py"
LOGIC = "modules/docs/application/logic/rule.py"


def listed(*files, checked=ON) -> list[str]:
    return [f"{w.file}:{w.line}: {w.message}" for w in weak(list(files), checked, "app")]


def test_a_public_function_of_a_part_that_holds_classes_is_listed_with_what_to_do():
    file = source(DOMAIN, functions=(Function(3, "clean"), Function(6, "_helper"), Function(9, "size", owner="Doc"),
                                     Function(12, "__getattr__")))
    assert weak([file], ON, "app") == [Weak(
        "holds", f"app/{DOMAIN}", 3, "clean is a function at the top level, but domain/ of modules/docs holds classes "
                                     "(parts.domain.holds)",
        "make clean a method of the class whose rule it is, or move it to a part that holds functions: logic/")]


def test_a_class_of_a_part_that_holds_functions_is_listed_with_what_to_do():
    file = source(LOGIC, classes=(Class(3, "Checker", methods=(Method(4, "run", None),)),))
    assert weak([file], ON, "app") == [Weak(
        "holds", f"app/{LOGIC}", 3, "Checker is a class, but logic/ of modules/docs holds functions "
                                    "(parts.logic.holds)",
        "move Checker to a part that holds classes: domain/, or make what it does functions")]


@pytest.mark.parametrize("cls, function, expected", [
    pytest.param(Class(3, "_Walk", methods=(Method(4, "step", None),)), Function(8, "walk"), ["_Walk"],
                 id="a private class with a method"),
    pytest.param(Class(3, "_Context"), Function(8, "fill"), ["_Context"], id="a private record no function returns"),
    pytest.param(Class(3, "_Found"), Function(8, "_find", returns_named=frozenset({"_Found"})), [],
                 id="a private record a function of the file returns"),
    pytest.param(Class(3, "_Refused", exception=True), Function(8, "walk"), [], id="a private exception"),
])
def test_a_private_class_is_held_to_the_same_rule_as_a_public_one(cls, function, expected):
    file = source(LOGIC, classes=(cls,), functions=(function,))
    assert [w.message.split(" ")[0] for w in weak([file], ON, "app")] == expected


def test_an_exception_class_is_not_listed():
    file = source(LOGIC, classes=(Class(3, "Refused", exception=True),))
    assert listed(file) == []


def test_a_class_deriving_from_an_exception_of_another_file_is_an_exception():
    errors = source("modules/docs/domain/errors.py", classes=(Class(3, "DocError", exception=True),))
    file = source(LOGIC, classes=(Class(3, "Refused", (("app", "modules", "docs", "domain", "errors", "DocError"),)),))
    assert listed(errors, file) == []


@pytest.mark.parametrize("cls, function, expected", [
    pytest.param(Class(3, "Found"), Function(8, "find", returns_named=frozenset({"Found", "None"})), [],
                 id="a record a function of the file returns"),
    pytest.param(Class(3, "Found", methods=(Method(4, "__post_init__", None),)),
                 Function(8, "find", returns_named=frozenset({"Found"})), [], id="a record with a dunder method"),
    pytest.param(Class(3, "Found", methods=(Method(4, "size", None),)),
                 Function(8, "find", returns_named=frozenset({"Found"})), ["Found"], id="a class with a method"),
    pytest.param(Class(3, "Found"), Function(8, "find", owner="X", returns_named=frozenset({"Found"})), ["Found"],
                 id="returned by a method only"),
    pytest.param(Class(3, "Found"), Function(8, "find"), ["Found"], id="returned by no function"),
])
def test_a_record_returned_by_a_function_of_its_file_is_not_listed(cls, function, expected):
    file = source(LOGIC, classes=(cls,), functions=(function,))
    assert [w.message.split(" ")[0] for w in weak([file], ON, "app")] == expected


def test_a_package_file_and_another_part_are_not_read():
    function = (Function(3, "clean"),)
    assert listed(source("modules/docs/domain/__init__.py", functions=function),
                  source("modules/docs/application/services/doc.py", functions=function)) == []


def test_it_is_off_without_the_key():
    assert listed(source(DOMAIN, functions=(Function(3, "clean"),)), checked=profile()) == []
