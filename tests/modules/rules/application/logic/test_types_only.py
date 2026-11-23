"""The types-only check on hand-made source files: a test of a tier that names parts in `types_only` never calls what
it reaches of them through an import, however written, and may call everything else."""
from dataclasses import replace

import pytest

from tests.modules.rules.application.logic.checks import types_only as violations
from tests.modules.rules.application.logic.checks import types_only_parts as part_violations
from tests.modules.rules.builders import GUARD, PROFILE, RENDERING, in_tests, profile, source
from xarch.modules.rules.domain.parsed import Call, Use

RENDERING_TEST = "web/test_docs.py"
CONTROLLER = ("app", "modules", "docs", "application", "controller", "DocumentController")


CONTROLLER_FILE = source("modules/docs/application/controller.py", module_functions=("make_controller",))
APP = [CONTROLLER_FILE, source("modules/docs/domain/doc.py", module_functions=("clean",)),
       source("web/routes.py", module_functions=("render",))]
MAKE = ("app", "modules", "docs", "application", "controller", "make_controller")


def problems(path: str, *calls: Call, checked=PROFILE, app=APP, uses: tuple[Use, ...] = ()) -> list[str]:
    return [str(v) for v in violations([in_tests(path, calls=calls, uses=uses)], app, checked, "app")]


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
    assert [v.rule for v in violations([in_tests(RENDERING_TEST, calls=(Call(4, CONTROLLER),))], APP, PROFILE, "app")] == [
        "types-only"]


@pytest.mark.parametrize("path, checked, fix", [
    pytest.param(RENDERING_TEST, PROFILE, "use controller/ here only as a type, and drive what you test through web/",
                 id="a tier whose subject is driven instead"),
    pytest.param(RENDERING_TEST, profile(tiers=(replace(RENDERING, may_touch="a fake controller, injected"),)),
                 "use controller/ here only as a type, and drive what you test through web/ (rendering tests may "
                 "touch: a fake controller, injected)", id="the tier's own words for what it may touch"),
    pytest.param("architecture/test_rules.py", profile(tiers=(replace(GUARD, types_only=("controller",)),)),
                 "use controller/ here only as a type, and test what it does from a tier that may call it",
                 id="a tier with no subject to drive"),
])
def test_a_violation_says_what_to_do(path, checked, fix):
    found = violations([in_tests(path, calls=(Call(4, CONTROLLER),))], APP, checked, "app")
    assert [(v.rule, v.fix) for v in found] == [("types-only", fix)]


def reported(line: int, name: str = "app.modules.docs.application.controller.make_controller") -> str:
    return (f"tests/web/test_docs.py:{line}: a rendering test uses controller/ of modules/docs only as a type: it may "
            f"not reference {name}, a function (tiers.rendering.types_only)")


@pytest.mark.parametrize("uses, calls, expected", [
    pytest.param((Use(5, MAKE, 6),), (), [reported(5)],
                 id="a function of a types-only part referenced by the name an import binds"),
    pytest.param((Use(5, MAKE, 5),), (), [reported(5)],
                 id="a function referenced through a module alias the import binds"),
    pytest.param((Use(5, MAKE, 1),), (), [reported(5)],
                 id="a function referenced through a plain import of the package root"),
    pytest.param((Use(5, MAKE, 6), Use(8, MAKE, 6)), (), [reported(5), reported(8)],
                 id="each reference is reported where it is"),
    pytest.param((Use(5, (*MAKE, "cache_clear"), 6),), (), [reported(5)],
                 id="an attribute of the function is a reference to the function"),
    pytest.param((Use(5, MAKE, 6),), (Call(5, MAKE),),
                 ["tests/web/test_docs.py:5: a rendering test uses controller/ of modules/docs only as a type: it may "
                  "not call app.modules.docs.application.controller.make_controller (tiers.rendering.types_only)"],
                 id="a call is reported as a call, once, not again as a reference"),
    pytest.param((Use(5, MAKE, 6), Use(5, MAKE, 6)), (Call(5, MAKE),),
                 ["tests/web/test_docs.py:5: a rendering test uses controller/ of modules/docs only as a type: it may "
                  "not call app.modules.docs.application.controller.make_controller (tiers.rendering.types_only)",
                  reported(5)],
                 id="a reference beside the call on its line is still reported"),
    pytest.param((Use(5, (*CONTROLLER[:-1], "DocumentController"), 6),), (), [],
                 id="a class of a types-only part may be referenced: isinstance, exception matching, enum members"),
    pytest.param((Use(5, ("app", "modules", "docs", "domain", "doc", "clean"), 6),), (), [],
                 id="a function of a part that is not types-only"),
    pytest.param((Use(5, ("app", "web", "routes", "render"), 4),), (), [], id="a function of the tier's own subject"),
    pytest.param((Use(5, ("app", "modules", "docs", "application", "make_controller"), 5),), (), [],
                 id="a name from a package that re-exports it is not followed"),
    pytest.param((Use(5, ("app", "modules", "docs", "application", "controller", "other"), 6),), (), [],
                 id="a name the file does not define as a function"),
    pytest.param((Use(5, ("app", "scripts", "seed", "run"), 4),), (), [], id="a name of an ungoverned file of the app"),
    pytest.param((Use(5, ("other", "modules", "docs", "application", "controller", "make_controller"), 6),), (), [],
                 id="another package laid out like the app"),
    pytest.param((Use(5, ("app",), 1),), (), [], id="the package root alone"),
    pytest.param((Use(5, ("app", "modules", "docs", "application", "controller"), 5),), (), [],
                 id="a module referenced as a whole"),
])
def test_a_function_of_a_types_only_part_may_not_be_referenced_at_all(uses, calls, expected):
    assert problems(RENDERING_TEST, *calls, uses=uses) == expected


@pytest.mark.parametrize("path, checked", [
    pytest.param("modules/docs/application/test_publish.py", PROFILE, id="a tier with no types_only parts"),
    pytest.param("scripts/test_seed.py", PROFILE, id="a test in no tier"),
    pytest.param("fakes/controller.py", PROFILE, id="a fake"),
    pytest.param(RENDERING_TEST, profile(tiers=()), id="a profile with no tiers"),
])
def test_a_test_whose_tier_names_no_types_only_part_may_reference_its_functions(path, checked):
    assert problems(path, uses=(Use(5, MAKE, 6),), checked=checked) == []


def test_the_source_tree_has_to_say_the_name_is_a_function_else_the_check_stays_silent():
    unknown = [source("modules/docs/application/controller.py")]
    assert problems(RENDERING_TEST, uses=(Use(5, MAKE, 6),), app=unknown) == []
    assert problems(RENDERING_TEST, uses=(Use(5, MAKE, 6),), app=[]) == []


PARTS_ON = profile(types_only={"services": ("contract",)})
SERVICE = "modules/docs/application/services/doc.py"
RESULT = ("app", "modules", "docs", "contract", "Published")
CONTRACT_FILE = source("modules/docs/contract/results.py", module_functions=("published",))


def part_problems(path: str = SERVICE, *calls: Call, checked=PARTS_ON, uses: tuple[Use, ...] = (),
                  others=(CONTRACT_FILE,)) -> list[str]:
    return [str(v) for v in part_violations([source(path, calls=calls, uses=uses), *others], checked, "app")]


def test_a_part_that_uses_a_part_only_as_a_type_may_not_call_it():
    assert part_problems(SERVICE, Call(4, RESULT), Call(5, (*RESULT, "of"))) == [
        f"app/{SERVICE}:4: services/ of modules/docs uses contract/ of modules/docs only as a type: it may not call "
        "app.modules.docs.contract.Published (parts.services.imports.may.types_only)",
        f"app/{SERVICE}:5: services/ of modules/docs uses contract/ of modules/docs only as a type: it may not call "
        "app.modules.docs.contract.Published.of (parts.services.imports.may.types_only)"]


def test_the_fix_names_the_parts_that_may_call_it():
    found = part_violations([source(SERVICE, calls=(Call(4, RESULT),))], PARTS_ON, "app")
    assert [v.fix for v in found] == [
        "use contract/ here only as a type, and leave the call to controller/, adapters/ or web/, which may make it"]


def test_a_part_may_not_reference_a_function_of_a_types_only_part():
    use = Use(6, ("app", "modules", "docs", "contract", "results", "published"), 6)
    assert part_problems(SERVICE, uses=(use,)) == [
        f"app/{SERVICE}:6: services/ of modules/docs uses contract/ of modules/docs only as a type: it may not "
        "reference app.modules.docs.contract.results.published, a function (parts.services.imports.may.types_only)"]


@pytest.mark.parametrize("path, call", [
    pytest.param("modules/docs/application/controller.py", Call(4, RESULT), id="a part that does not list it"),
    pytest.param(SERVICE, Call(4, ("app", "modules", "docs", "domain", "doc", "Document")), id="another part"),
    pytest.param(SERVICE, Call(4, ("shop", "modules", "docs", "contract", "Published")), id="another package"),
])
def test_only_the_listed_parts_of_a_listing_part_are_held(path, call):
    assert part_problems(path, call) == []


def test_it_is_off_without_the_key():
    assert part_problems(SERVICE, Call(4, RESULT), checked=PROFILE) == []
