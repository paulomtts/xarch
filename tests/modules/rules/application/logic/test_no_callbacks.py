"""The no-callbacks check on hand-made source files: code of a listed part never calls one of its own parameters."""
from tests.modules.rules.application.logic.checks import no_callbacks as violations
from tests.modules.rules.builders import profile, source
from xarch.modules.rules.domain.parsed import Callback

ON = profile(no_callbacks=("logic",))
LOGIC = "modules/docs/application/logic/rule.py"


def problems(path: str = LOGIC, *callbacks: Callback, checked=ON) -> list[str]:
    return [str(v) for v in violations([source(path, callbacks=callbacks)], checked)]


def test_a_call_of_a_parameter_is_reported_with_what_to_do():
    found = violations([source(LOGIC, callbacks=(Callback(4, "resolve", "exists", annotated=True),))], ON)
    assert [(str(v), v.rule, v.fix) for v in found] == [
        (f"app/{LOGIC}:4: resolve calls its parameter exists: logic/ of modules/docs takes no callback "
         "(guards.no-callbacks)", "no-callbacks",
         "have the caller call exists first and pass resolve the answer as a value")]


def test_the_receiver_of_a_method_is_no_callback():
    assert problems(LOGIC, Callback(4, "make", "cls", receiver=True, annotated=True)) == []


def test_a_parameter_not_annotated_as_a_callable_is_not_read():
    assert problems(LOGIC, Callback(4, "first", "wanted")) == []


def test_only_the_listed_parts_are_read():
    assert problems("modules/docs/application/services/doc.py", Callback(4, "run", "step", annotated=True)) == []


def test_it_is_off_without_a_listed_part():
    assert problems(LOGIC, Callback(4, "resolve", "exists", annotated=True), checked=profile()) == []


def test_every_listed_part_s_finding_names_the_guard_and_not_the_part():
    domain = "modules/docs/domain/rule.py"
    found = violations([source(LOGIC, callbacks=(Callback(4, "resolve", "exists", annotated=True),)),
                        source(domain, callbacks=(Callback(7, "check", "has", annotated=True),))],
                       profile(no_callbacks=("logic", "domain")))
    assert sorted(str(v) for v in found) == [
        f"app/{LOGIC}:4: resolve calls its parameter exists: logic/ of modules/docs takes no callback "
        "(guards.no-callbacks)",
        f"app/{domain}:7: check calls its parameter has: domain/ of modules/docs takes no callback (guards.no-callbacks)"]
