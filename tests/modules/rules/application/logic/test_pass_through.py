"""The pass-through check on hand-made source files: a method of a listed part whose whole body forwards to one call is
listed as weak, never as a violation."""
from tests.modules.rules.builders import profile, source
from xarch.modules.rules.application.logic.pass_through import weak
from xarch.modules.rules.domain.values import Function, Weak

ON = profile(pass_through=("services",))
SERVICES = "modules/docs/application/services/doc.py"


def found(path: str = SERVICES, checked=ON, **fields):
    functions = (Function(4, "get", owner="DocService", forwards="self.repo.get"),
                 Function(8, "publish", owner="DocService"), Function(12, "helper", forwards="self.repo.list"))
    return weak([source(path, functions=fields.get("functions", functions))], checked)


def test_a_method_that_forwards_is_listed_with_what_to_do():
    assert found()[0] == Weak(
        "pass-through", f"app/{SERVICES}", 4,
        "DocService.get only passes its arguments on to self.repo.get",
        "have the caller use self.repo.get, or keep it as a deliberate plain forward: it stays listed and fails only "
        "`check --strict`")


def test_a_function_of_no_class_and_a_method_that_does_not_forward_are_not_listed():
    assert [w.message for w in found()] == ["DocService.get only passes its arguments on to self.repo.get"]


def test_only_the_parts_the_profile_lists_are_read():
    assert found(path="modules/docs/application/logic/rule.py") == []
    assert found(path="modules/docs/adapters/db.py") == []


def test_it_is_off_without_a_listed_part():
    assert found(checked=profile()) == []
