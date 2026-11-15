"""The built-by check on hand-made source files: only the parts a part lists in `built_by` call the constructor of a
class defined in it."""
import pytest

from tests.modules.rules.application.logic.checks import built_by as violations
from tests.modules.rules.builders import profile, source
from xarch.modules.rules.domain.values import Call, Class

ON = profile(built_by={"services": ("bootstrap",)})
SERVICE_FILE = source("modules/docs/application/services/doc.py", classes=(Class(3, "DocService"),))
DOC_SERVICE = ("app", "modules", "docs", "application", "services", "doc", "DocService")


def problems(path: str, *calls: Call, checked=ON) -> list[str]:
    return [str(v) for v in violations([source(path, calls=calls), SERVICE_FILE], checked, "app")]


def test_a_part_that_is_not_listed_may_not_build_its_classes():
    found = violations([source("modules/docs/application/controller.py", calls=(Call(5, DOC_SERVICE),)),
                        SERVICE_FILE], ON, "app")
    assert [(str(v), v.rule, v.fix) for v in found] == [
        ("app/modules/docs/application/controller.py:5: controller/ of modules/docs builds DocService, a class of "
         "services/ of modules/docs, which only bootstrap/ may build (parts.services.built_by)", "built-by",
         "take DocService as a parameter of the constructor, and build it in bootstrap/")]


@pytest.mark.parametrize("path, call", [
    pytest.param("bootstrap/wiring.py", Call(5, DOC_SERVICE), id="a listed part"),
    pytest.param("modules/docs/application/controller.py",
                 Call(5, ("app", "modules", "docs", "application", "services", "doc", "make")), id="a function"),
    pytest.param("modules/docs/application/controller.py",
                 Call(5, ("app", "modules", "docs", "domain", "doc", "Document")), id="a class of another part"),
    pytest.param("modules/docs/application/controller.py",
                 Call(5, ("app", "modules", "docs", "application", "services", "DocService")),
                 id="a class reached through a package file"),
])
def test_what_is_no_class_of_the_part_or_is_built_by_a_listed_part_is_fine(path, call):
    assert problems(path, call) == []


def test_the_part_itself_counts_as_any_other():
    assert problems("modules/docs/application/services/other.py", Call(5, DOC_SERVICE)) == [
        "app/modules/docs/application/services/other.py:5: services/ of modules/docs builds DocService, a class of "
        "services/ of modules/docs, which only bootstrap/ may build (parts.services.built_by)"]


def test_it_is_off_without_the_key():
    assert problems("modules/docs/application/controller.py", Call(5, DOC_SERVICE), checked=profile()) == []
