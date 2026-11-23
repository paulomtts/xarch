"""The names check on hand-made source files: every public definition held to a kind of a part's `holds` that gives
`names` matches one of its patterns: a class held to classes, a top-level function, a record held to records and an
exception; a class is held to the narrowest kind listed that it fits, and to no other's names."""
import pytest

from tests.modules.rules.application.logic.checks import names as violations
from tests.modules.rules.builders import BRACE, profile, source
from xarch.modules.rules.domain.parsed import Class, Function, Method

ON = profile(holds={"services": ("classes",)}, holds_names={"services": {"classes": ("*Service", "*Step")}})
SERVICES = "modules/docs/application/services/doc.py"


def problems(*classes: Class, path: str = SERVICES, checked=ON) -> list[str]:
    return [str(v) for v in violations([source(path, classes=classes)], checked)]


def test_a_class_whose_name_matches_no_pattern_is_reported_with_what_to_do():
    found = violations([source(SERVICES, classes=(Class(3, "Publisher"),))], ON)
    assert [(str(v), v.rule, v.fix) for v in found] == [
        (f"app/{SERVICES}:3: Publisher does not match *Service or *Step, as every class of services/ of modules/docs "
         "must (parts.services.holds.classes.names)", "names",
         "rename Publisher to match *Service or *Step, or move it to the part whose kind of class it is")]


@pytest.mark.parametrize("name", [
    pytest.param("DocService", id="a name that matches"),
    pytest.param("PublishStep", id="a name that matches another pattern"),
    pytest.param("_Helper", id="a private class"),
])
def test_a_class_that_matches_or_is_private_is_fine(name):
    assert problems(Class(3, name)) == []


def test_only_the_listed_parts_are_read():
    assert problems(Class(3, "Publisher"), path="modules/docs/application/logic/rule.py") == []
    assert problems(Class(3, "Publisher"), checked=profile()) == []


BRACED = "modules/docs/application/services/doc.ts"


@pytest.mark.parametrize("cls, expected", [
    pytest.param(Class(3, "helper", public=False), [], id="a class the reader says is not public"),
    pytest.param(Class(3, "helper"), [f"app/{BRACED}:3: helper does not match *Service, as every class of services/ "
                                      "of modules/docs must (parts.services.holds.classes.names)"],
                 id="one it says is public"),
    pytest.param(Class(3, "_Shown"), [f"app/{BRACED}:3: _Shown does not match *Service, as every class of services/ "
                                      "of modules/docs must (parts.services.holds.classes.names)"],
                 id="one it says is public, spelled as a private name of another language"),
])
def test_under_a_language_with_no_private_prefix_the_reader_alone_says_which_classes_are_public(cls, expected):
    braced = profile(holds={"services": ("classes",)}, holds_names={"services": {"classes": ("*Service",)}}, language=BRACE)
    assert [str(v) for v in violations([source(BRACED, classes=(cls,), language=BRACE)], braced)] == expected


LOGIC = "modules/docs/application/logic/rule.py"
CLASSES = (Class(3, "Checker", methods=(Method(4, "run", None),)), Class(5, "Found"), Class(7, "Refused", exception=True))
FILE = source(SERVICES, classes=CLASSES, functions=(Function(9, "clean"), Function(10, "find", returns_named=frozenset(
    {"Found"})), Function(12, "_helper"), Function(14, "check", owner="Checker")))
"""A file of services that defines a plain class, a record its function find returns, an exception, two public
top-level functions, a private one and a method."""


def named(holds: dict[str, tuple[str, ...]], file=FILE) -> list[str]:
    """What the names check says of the file in a part whose holds lists the kinds given, each held to `X*`."""
    checked = profile(holds={"services": tuple(holds)}, holds_names={"services": {kind: ("X*",) for kind in holds}})
    return [str(v).split(": ", 1)[1] for v in violations([file], checked)]


def test_names_of_classes_reads_every_public_class_records_and_exceptions_too_when_no_narrower_kind_is_listed():
    assert named({"classes": ()}) == [
        f"{name} does not match X*, as every class of services/ of modules/docs must (parts.services.holds.classes.names)"
        for name in ("Checker", "Found", "Refused")]


def test_beside_exceptions_an_exception_is_held_to_their_names_alone_and_every_other_class_to_those_of_classes():
    checked = profile(holds={"services": ("classes", "exceptions")},
                      holds_names={"services": {"classes": ("*Service",), "exceptions": ("*Error",)}})
    assert [str(v).split(": ", 1)[1] for v in violations([FILE], checked)] == [
        "Checker does not match *Service, as every class of services/ of modules/docs must "
        "(parts.services.holds.classes.names)",
        "Found does not match *Service, as every class of services/ of modules/docs must "
        "(parts.services.holds.classes.names)",
        "Refused does not match *Error, as every exception of services/ of modules/docs must "
        "(parts.services.holds.exceptions.names)"]


def test_names_of_functions_reads_every_public_top_level_function_and_no_method_nor_private_one():
    found = violations([FILE], profile(holds={"services": ("functions",)}, holds_names={"services": {"functions": ("is_*",)}}))
    assert [(str(v).split(": ", 1)[1], v.fix) for v in found] == [
        (f"{name} does not match is_*, as every function of services/ of modules/docs must "
         "(parts.services.holds.functions.names)",
         f"rename {name} to match is_*, or move it to the part whose kind of function it is")
        for name in ("clean", "find")]


def test_names_of_records_and_of_exceptions_read_their_kind_alone():
    assert named({"records": ()}) == [
        "Found does not match X*, as every record of services/ of modules/docs must (parts.services.holds.records.names)"]
    assert named({"exceptions": ()}) == [
        "Refused does not match X*, as every exception of services/ of modules/docs must "
        "(parts.services.holds.exceptions.names)"]


def test_a_class_that_fits_both_narrower_kinds_is_read_as_an_exception():
    both = source(SERVICES, classes=(Class(3, "Refused", exception=True),),
                  functions=(Function(8, "refuse", returns_named=frozenset({"Refused"})),))
    assert named({"records": (), "exceptions": ()}, both) == [
        "Refused does not match X*, as every exception of services/ of modules/docs must "
        "(parts.services.holds.exceptions.names)"]
    assert named({"classes": (), "records": ()}, both) == [
        "Refused does not match X*, as every record of services/ of modules/docs must "
        "(parts.services.holds.records.names)"]
