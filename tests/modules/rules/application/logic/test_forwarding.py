"""Whether a method only passes its arguments on, from the facts the reader records of it: no decorator, no special
name, and a whole body of one call on a chain of at least two attributes of its first parameter, passing each of its
other parameters straight through and nothing else."""
import pytest

from tests.modules.rules.builders import PYTHON
from xarch.modules.rules.application.logic.forwarding import forwards
from xarch.modules.rules.domain.values import Function, Signature, SoleCall

GET = ("self", "repo", "get")
ID = Signature(("self", "id"))


def method(call: SoleCall | None, signature: Signature = ID, name: str = "get", owner: str = "S",
           decorated: bool = False) -> Function:
    return Function(4, name, owner=owner, decorated=decorated, signature=signature, sole_call=call)


@pytest.mark.parametrize("function, callee", [
    pytest.param(method(SoleCall(GET, ("id",))), "self.repo.get", id="one call on a collaborator, its parameter passed"),
    pytest.param(method(SoleCall(GET, (), (("id", "id"),))), "self.repo.get", id="a keyword with the parameter's value"),
    pytest.param(method(SoleCall(GET, (), (("other", "id"),))), "self.repo.get", id="a keyword of another name"),
    pytest.param(method(SoleCall(("self", "a", "b", "get"), ("id",))), "self.a.b.get", id="a deeper chain"),
    pytest.param(method(SoleCall(GET, ("id",), then=("name",))), "self.repo.get", id="a read of the result"),
    pytest.param(method(SoleCall(GET, ("id", ""))), "", id="an extra argument"),
    pytest.param(method(SoleCall(GET, ("",))), "", id="a changed argument"),
    pytest.param(method(SoleCall(GET)), "", id="a parameter that is not passed"),
    pytest.param(method(SoleCall(GET, ("id", "id"))), "", id="a parameter passed twice"),
    pytest.param(method(SoleCall(GET, ("id", ""), then=("name",))), "", id="a read of a call that does not forward"),
    pytest.param(method(None), "", id="no one call"),
    pytest.param(method(SoleCall(("self", "helper"), ("id",))), "", id="a method of the object itself, no collaborator"),
    pytest.param(method(SoleCall(("other", "repo", "get"), ("id",))), "",
                 id="a chain that does not start at the first parameter"),
    pytest.param(method(SoleCall(("self", "r", "a"), ("*args",), (("**", "kwargs"),)),
                        Signature(("self",), (), "args", "kwargs")), "self.r.a", id="starred parameters passed on starred"),
    pytest.param(method(SoleCall(("self", "r", "a"), ("args",)), Signature(("self",), (), "args")), "",
                 id="a starred parameter passed as one argument"),
    pytest.param(method(SoleCall(("self", "r", "a"), ("k",), (("only", "only"),)), Signature(("self", "k"), ("only",))),
                 "self.r.a", id="a keyword-only parameter passed by keyword"),
    pytest.param(method(SoleCall(("self", "r", "a")), Signature(("self",)), decorated=True), "", id="a decorated method"),
    pytest.param(method(SoleCall(("self", "r", "size")), Signature(("self",)), name="__a__"), "", id="a special method"),
    pytest.param(method(SoleCall(("self", "r", "a")), Signature()), "", id="no first parameter to hold it"),
    pytest.param(method(SoleCall(("self", "r", "a")), Signature(("self",)), owner=""), "",
                 id="a function of no class forwards nothing"),
])
def test_a_method_forwards_when_its_one_call_passes_each_parameter_once_to_a_collaborator(function, callee):
    assert forwards(function, PYTHON) == callee
