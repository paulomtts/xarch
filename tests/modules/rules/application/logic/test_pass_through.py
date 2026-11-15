"""The pass-through check on hand-made source files: a method of a listed part whose whole body forwards to one call is
listed as weak, never as a violation."""
import pytest

from tests.modules.rules.builders import profile, source
from xarch.modules.rules.application.logic.pass_through import forwards, weak
from xarch.modules.rules.domain.values import Function, Signature, SoleCall, Weak

ON = profile(pass_through=("services",))
SERVICES = "modules/docs/application/services/doc.py"


TAKES_ID = Signature(("self", "id"))


def forwarding(line: int, name: str, callee: tuple[str, ...], owner: str = "") -> Function:
    """A function whose whole body passes its one parameter on to callee."""
    return Function(line, name, owner=owner, signature=TAKES_ID, sole_call=SoleCall(callee, ("id",)))


def found(path: str = SERVICES, checked=ON, **fields):
    functions = (forwarding(4, "get", ("self", "repo", "get"), "DocService"),
                 Function(8, "publish", owner="DocService"), forwarding(12, "helper", ("self", "repo", "list")))
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


def test_a_part_that_is_a_file_and_a_folder_part_are_read_alike():
    wide = profile(pass_through=("controller", "adapters"))
    method = (forwarding(4, "get", ("self", "_fs", "get"), "X"),)
    assert [w.file for w in weak([source("modules/docs/application/controller.py", functions=method),
                                  source("modules/docs/adapters/fs_repo.py", functions=method),
                                  source(SERVICES, functions=method)], wide)] == [
        "app/modules/docs/application/controller.py", "app/modules/docs/adapters/fs_repo.py"]


@pytest.mark.parametrize("call, callee", [
    pytest.param(SoleCall(('self', 'repo', 'get'), ('id',)), "self.repo.get", id="a return of one call on a collaborator"),
    pytest.param(SoleCall(('self', 'repo', 'save'), ('id',)), "self.repo.save", id="a bare call"),
    pytest.param(SoleCall(('self', 'repo', 'get'), ('id',)), "self.repo.get", id="an awaited call"),
    pytest.param(SoleCall(('self', 'repo', 'get'), (), (('id', 'id'),)), "self.repo.get", id="a keyword with the parameter's value"),
    pytest.param(SoleCall(('self', 'repo', 'get'), (), (('other', 'id'),)), "self.repo.get", id="a keyword of another name"),
    pytest.param(SoleCall(('self', 'a', 'b', 'get'), ('id',)), "self.a.b.get", id="a deeper chain"),
    pytest.param(SoleCall(('self', 'repo', 'get'), ('id',)), "self.repo.get", id="a docstring is no statement"),
    pytest.param(SoleCall(('self', 'repo', 'get'), ('id', '')), "", id="an extra argument"),
    pytest.param(SoleCall(('self', 'repo', 'get'), ('',)), "", id="a changed argument"),
    pytest.param(SoleCall(('self', 'repo', 'get'), ('',)), "", id="a transformed argument"),
    pytest.param(SoleCall(('self', 'repo', 'get')), "", id="a parameter that is not passed"),
    pytest.param(SoleCall(('self', 'repo', 'get'), ('id', 'id')), "", id="a parameter passed twice"),
    pytest.param(None, "", id="a changed result"),
    pytest.param(None, "", id="two statements"),
    pytest.param(None, "", id="a condition"),
    pytest.param(SoleCall(('self', 'helper'), ('id',)), "", id="a method of the object itself, no collaborator"),
    pytest.param(SoleCall(('other', 'repo', 'get'), ('id',)), "", id="a chain that does not start at the first parameter"),
    pytest.param(None, "", id="a read of the result"),
    pytest.param(SoleCall(('self', 'repo', 'get'), ('', 'id')), "", id="a call inside the arguments"),
])
def test_a_method_forwards_when_its_one_call_passes_each_parameter_once_to_a_collaborator(call, callee):
    assert forwards(Function(1, "get", owner="S", signature=TAKES_ID, sole_call=call)) == callee


@pytest.mark.parametrize("function, callee", [
    pytest.param(Function(1, "a", signature=Signature(("self",), (), "args", "kwargs"),
                          sole_call=SoleCall(("self", "r", "a"), ("*args",), (("**", "kwargs"),))), "self.r.a",
                 id="starred parameters passed on starred"),
    pytest.param(Function(1, "b", signature=Signature(("self",), (), "args"), sole_call=SoleCall(("self", "r", "b"),
                                                                                              ("args",))), "",
                 id="a starred parameter passed as one argument"),
    pytest.param(Function(1, "c", decorated=True, signature=Signature(("self",)), sole_call=SoleCall(("self", "r", "c"))),
                 "", id="a decorated method"),
    pytest.param(Function(1, "__len__", signature=Signature(("self",)), sole_call=SoleCall(("self", "r", "size"))), "",
                 id="a dunder method"),
    pytest.param(Function(1, "d", signature=Signature(("self", "k"), ("only",)),
                          sole_call=SoleCall(("self", "r", "d"), ("k",), (("only", "only"),))), "self.r.d",
                 id="a keyword-only parameter passed by keyword"),
    pytest.param(Function(1, "e", sole_call=SoleCall(("self", "r", "e"))), "", id="no first parameter to hold it"),
])
def test_a_decorator_a_dunder_or_a_starred_parameter_passed_whole_decides_too(function, callee):
    assert forwards(function) == callee
