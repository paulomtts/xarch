"""The holds check on hand-made source files: a file of a part whose `holds` lists the kinds it may define defines at
the top level no public function when it does not list functions, and no class (a private one too) when it does not
list classes, but an exception or a record when it lists that kind; each one is listed as weak, never as a violation,
and said as the narrowest kind it fits. A part whose classes or records are immutable lists each that is not."""
from dataclasses import replace

import pytest

from tests.modules.rules.application.logic.checks import holds as weak
from tests.modules.rules.builders import BRACE, profile, source
from xarch.modules.rules.domain.parsed import Class, Function, Method
from xarch.modules.rules.domain.published import Weak
from xarch.profile_values.capabilities import EXACT, FACTS, Supply
from xarch.profile_values.language import RecordMark

FUNCTIONS = ("functions", "records", "exceptions")
ON = profile(holds={"domain": ("classes",), "logic": FUNCTIONS})
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
        "holds", f"app/{LOGIC}", 3, "Checker is a class, but logic/ of modules/docs holds functions, records and "
                                    "exceptions (parts.logic.holds)",
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


FUNCTION, CLASS = "clean is a function at the top level", "Checker is a class"
SAID = {"functions": [FUNCTION, "find is a function at the top level"], "class": [CLASS],
        "record": ["Found is a record"], "exception": ["Refused is an exception"]}
FILE = source(LOGIC, classes=(Class(3, "Checker", methods=(Method(4, "run", None),)), Class(5, "Found"),
                              Class(7, "Refused", exception=True)),
              functions=(Function(9, "clean"), Function(10, "find", returns_named=frozenset({"Found"})),
                         Function(12, "_helper")))
"""A file of logic that defines a plain class, a record its function find returns, an exception, and two public
top-level functions and a private one."""


@pytest.mark.parametrize("kinds, held, found", [
    pytest.param(("classes",), "classes", ["functions"], id="classes"),
    pytest.param(("functions",), "functions", ["class", "record", "exception"], id="functions alone"),
    pytest.param(("functions", "records"), "functions and records", ["class", "exception"], id="functions and records"),
    pytest.param(FUNCTIONS, "functions, records and exceptions", ["class"], id="what logic holds"),
    pytest.param(("records",), "records", ["functions", "class", "exception"], id="records alone"),
    pytest.param(("classes", "exceptions"), "classes and exceptions", ["functions"], id="classes beside exceptions"),
])
def test_a_part_lists_what_its_holds_does_not_allow_each_as_the_narrowest_kind_it_fits(kinds, held, found):
    messages = listed(FILE, checked=profile(holds={"logic": kinds}))
    assert [message.split(": ", 1)[1] for message in messages] == [
        f"{said}, but logic/ of modules/docs holds {held} (parts.logic.holds)" for kind in found for said in SAID[kind]]


def test_a_class_a_part_does_not_allow_keeps_the_fix_that_moves_it_whatever_kind_it_is():
    found = weak([FILE], profile(holds={"logic": ("functions",), "domain": ("classes",)}), "app")
    assert {w.fix for w in found} == {f"move {name} to a part that holds classes: domain/, or make what it does functions"
                                      for name in ("Checker", "Found", "Refused")}


NO_TOP = replace(profile().language, supplies=tuple(Supply(fact, EXACT) for fact in FACTS
                                                     if fact != "function.top_level"))
SAYS_NOTHING = replace(profile().language, supplies=None)


def test_in_a_language_that_does_not_supply_top_level_functions_no_part_is_held_to_its_functions():
    assert listed(FILE, checked=profile(holds={"logic": ("classes",)}, language=NO_TOP)) == []
    assert len(listed(FILE, checked=profile(holds={"logic": ("classes",)}, language=SAYS_NOTHING))) == 2


IMMUTABLE = profile(holds={"logic": FUNCTIONS}, immutable={"logic": ("records",)})


def test_a_record_of_a_part_whose_records_are_immutable_that_is_not_one_is_listed_with_what_to_do():
    file = source(LOGIC, classes=(Class(3, "Found"),),
                  functions=(Function(8, "find", returns_named=frozenset({"Found"})),))
    assert weak([file], IMMUTABLE, "app") == [Weak(
        "immutable", f"app/{LOGIC}", 3, "Found is a record that is not immutable, but every record of logic/ of "
                                        "modules/docs is one (parts.logic.holds.records.immutable)",
        "make Found an immutable record (the Python data file's `immutable` says how), or move it to a part that "
        "holds classes")]


def test_immutable_on_records_reads_no_plain_class_which_holds_lists_once():
    file = source(LOGIC, classes=(Class(3, "Checker", methods=(Method(4, "run", None),)),))
    assert [w.rule for w in weak([file], IMMUTABLE, "app")] == ["holds"]


def test_immutable_on_classes_reads_every_class_but_an_exception():
    classes = profile(holds={"domain": ("classes",)}, immutable={"domain": ("classes",)})
    file = source(DOMAIN, classes=(Class(3, "Doc"), Class(5, "Refused", exception=True), Class(7, "Kept", immutable=True)))
    assert weak([file], classes, "app") == [Weak(
        "immutable", f"app/{DOMAIN}", 3, "Doc is a class that is no immutable record, but every class of domain/ of "
                                         "modules/docs is one (parts.domain.holds.classes.immutable)",
        "make Doc an immutable record (the Python data file's `immutable` says how), or move it to a part that holds "
        "classes: domain/")]


def test_immutable_on_classes_beside_records_reads_no_record_which_its_own_kind_holds():
    both = profile(holds={"domain": ("classes", "records")}, immutable={"domain": ("classes",)})
    file = source(DOMAIN, classes=(Class(3, "Doc"), Class(5, "Found")),
                  functions=(Function(8, "_find", returns_named=frozenset({"Found"})),))
    assert [w.message.split(" ")[0] for w in weak([file], both, "app")] == ["Doc"]


@pytest.mark.parametrize("cls", [
    pytest.param(Class(3, "_Found", immutable=True), id="an immutable record"),
    pytest.param(Class(3, "_Refused", exception=True), id="an exception"),
])
def test_an_immutable_record_or_an_exception_is_not_listed(cls):
    file = source(LOGIC, classes=(cls,), functions=(Function(8, "_find", returns_named=frozenset({cls.name})),))
    assert listed(file, checked=IMMUTABLE) == []


def test_a_package_file_and_a_part_that_does_not_ask_for_immutable_records_are_not_read():
    loose = Class(3, "_Found")
    returned = Function(8, "_find", returns_named=frozenset({"_Found"}))
    package = source("modules/docs/application/logic/__init__.py", classes=(loose,), functions=(returned,))
    assert listed(package, checked=IMMUTABLE) == []
    assert listed(source(LOGIC, classes=(loose,), functions=(returned,)), checked=profile(holds={"logic": FUNCTIONS})) == []


@pytest.mark.parametrize("function, expected", [
    pytest.param(Function(3, "helper", public=False), [], id="a function the reader says is not public"),
    pytest.param(Function(3, "_helper"), ["_helper is a function at the top level, but domain/ of modules/docs holds "
                                          "classes (parts.domain.holds)"],
                 id="one it says is public, whatever its spelling"),
])
def test_under_a_language_with_no_private_prefix_the_reader_alone_says_which_functions_are_public(function, expected):
    braced = profile(holds={"domain": ("classes",)}, language=BRACE)
    file = source("modules/docs/domain/doc.ts", functions=(function,), language=BRACE)
    assert [w.message for w in weak([file], braced, "app")] == expected


@pytest.mark.parametrize("record, expected", [
    pytest.param(True, [], id="a class the reader says is a record"),
    pytest.param(False, ["Point"], id="the same class, said to be none"),
])
def test_under_brace_the_reader_alone_says_which_classes_are_records(record, expected):
    braced = profile(holds={"logic": FUNCTIONS}, language=BRACE)
    file = source("modules/docs/application/logic/point.ts", classes=(Class(3, "Point", record=record),), language=BRACE)
    assert [w.message.split(" ")[0] for w in weak([file], braced, "app")] == expected


@pytest.mark.parametrize("immutable, expected", [
    pytest.param(True, [], id="a class the reader says is an immutable record"),
    pytest.param(False, ["immutable"], id="one it says is not"),
])
def test_under_brace_the_reader_alone_says_which_classes_are_immutable_records(immutable, expected):
    assert BRACE.immutable == (RecordMark(fields="readonly"),)
    braced = profile(holds={"logic": ("classes",)}, immutable={"logic": ("classes",)}, language=BRACE)
    file = source("modules/docs/application/logic/point.ts", classes=(Class(3, "Point", immutable=immutable),),
                  language=BRACE)
    assert [w.rule for w in weak([file], braced, "app")] == expected
