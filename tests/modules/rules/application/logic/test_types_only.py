"""The types-only check on hand-made source files: a test of a tier that names parts in `types_only` never calls what
it reaches of them through an absolute import, and may call everything else."""
import pytest

from tests.modules.rules.builders import PROFILE, in_tests, profile
from xarch.modules.rules.application.logic.types_only import violations
from xarch.modules.rules.domain.values import Call

RENDERING_TEST = "web/test_docs.py"
CONTROLLER = ("app", "modules", "docs", "application", "controller", "DocumentController")


def problems(path: str, *calls: Call, checked=PROFILE) -> list[str]:
    return [str(v) for v in violations([in_tests(path, calls=calls)], checked, "app")]


@pytest.mark.parametrize("call", [
    pytest.param(Call(4, ("app", "modules", "docs", "contract", "Published")), id="a Result of contract/"),
    pytest.param(Call(4, ("app", "web", "routes", "router")), id="the tier's own subject"),
    pytest.param(Call(4, ("app", "modules", "docs", "domain", "doc", "Document")), id="a part it may not import"),
    pytest.param(Call(4, ("app", "scripts", "seed", "run")), id="an ungoverned place of the app"),
    pytest.param(Call(4, ("fastapi", "testclient", "TestClient")), id="an outside package"),
    pytest.param(Call(4, ("tests", "web", "conftest", "client")), id="test code"),
    pytest.param(Call(4, ("shop", "modules", "docs", "application", "controller", "DocumentController")),
                 id="another package laid out like the app"),
])
def test_a_call_of_anything_but_a_types_only_part_is_allowed(call):
    assert problems(RENDERING_TEST, call) == []


def test_a_call_of_a_types_only_part_is_reported():
    assert problems(RENDERING_TEST, Call(4, CONTROLLER), Call(7, (*CONTROLLER, "publish"))) == [
        "tests/web/test_docs.py:4: a rendering test uses controller/ of modules/docs only as a type: it may not call "
        "app.modules.docs.application.controller.DocumentController (tiers.rendering.types_only)",
        "tests/web/test_docs.py:7: a rendering test uses controller/ of modules/docs only as a type: it may not call "
        "app.modules.docs.application.controller.DocumentController.publish (tiers.rendering.types_only)"]


@pytest.mark.parametrize("path, checked", [
    pytest.param("modules/docs/application/test_publish.py", PROFILE, id="a tier with no types_only parts"),
    pytest.param("scripts/test_seed.py", PROFILE, id="a test in no tier"),
    pytest.param("fakes/controller.py", PROFILE, id="a fake"),
    pytest.param(RENDERING_TEST, profile(tiers=()), id="a profile with no tiers"),
])
def test_a_test_whose_tier_names_no_types_only_part_may_call_it(path, checked):
    assert problems(path, Call(4, CONTROLLER), checked=checked) == []


def test_a_violation_names_its_rule():
    assert [v.rule for v in violations([in_tests(RENDERING_TEST, calls=(Call(4, CONTROLLER),))], PROFILE, "app")] == [
        "types-only"]
