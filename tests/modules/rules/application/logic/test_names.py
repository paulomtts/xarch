"""The names check on hand-made source files: every public class of a part that lists `names` matches a pattern."""
import pytest

from tests.modules.rules.application.logic.checks import names as violations
from tests.modules.rules.builders import BRACE, profile, source
from xarch.modules.rules.domain.parsed import Class

ON = profile(names={"services": ("*Service", "*Step")})
SERVICES = "modules/docs/application/services/doc.py"


def problems(*classes: Class, path: str = SERVICES, checked=ON) -> list[str]:
    return [str(v) for v in violations([source(path, classes=classes)], checked)]


def test_a_class_whose_name_matches_no_pattern_is_reported_with_what_to_do():
    found = violations([source(SERVICES, classes=(Class(3, "Publisher"),))], ON)
    assert [(str(v), v.rule, v.fix) for v in found] == [
        (f"app/{SERVICES}:3: Publisher does not match *Service or *Step, as every class of services/ of modules/docs "
         "must (parts.services.names)", "names",
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
                                      "of modules/docs must (parts.services.names)"], id="one it says is public"),
    pytest.param(Class(3, "_Shown"), [f"app/{BRACED}:3: _Shown does not match *Service, as every class of services/ "
                                      "of modules/docs must (parts.services.names)"],
                 id="one it says is public, spelled as a private name of another language"),
])
def test_under_a_language_with_no_private_prefix_the_reader_alone_says_which_classes_are_public(cls, expected):
    braced = profile(names={"services": ("*Service",)}, language=BRACE)
    assert [str(v) for v in violations([source(BRACED, classes=(cls,), language=BRACE)], braced)] == expected
