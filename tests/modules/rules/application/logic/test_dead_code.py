"""The dead-code check on hand-made source files: a port no other file of the app names, and a fake no test names."""
import pytest

from tests.modules.rules.builders import in_tests, profile, source
from xarch.modules.rules.application.logic.dead_code import violations
from xarch.modules.rules.domain.values import Class, Method

PROTOCOL = ("typing", "Protocol")
PORT_FILE = "modules/docs/application/ports/repo.py"
REPO = Class(3, "Repo", (PROTOCOL,), (Method(4, "get", "int"),))
NOTIFIER = Class(8, "Notifier", (PROTOCOL,), (Method(9, "send", "None"),))
ON = profile(dead_code=True)
PORTS = source(PORT_FILE, classes=(REPO, NOTIFIER), named=frozenset({"Repo", "Notifier", "Protocol"}))
SERVICE = "modules/docs/application/services/doc.py"
DEAD_PORT = "app/{path}:{line}: {name} is a port that nothing else in the app names (dead-code)"


def uses(path: str, *names: str):
    return source(path, named=frozenset(names))


def fake(name: str, line: int = 1, *names: str) -> Class:
    return Class(line, name, (), (), (), frozenset(names))


def problems(app, tests=(), checked=ON, has_tests=True) -> list[str]:
    return [str(v) for v in violations(list(app), list(tests), checked, has_tests)]


def dead_port(name: str, line: int) -> str:
    return DEAD_PORT.format(path=PORT_FILE, line=line, name=name)


@pytest.mark.parametrize("other, expected", [
    pytest.param(uses(SERVICE, "Repo", "Notifier"), [], id="a service that names both"),
    pytest.param(uses(SERVICE, "Repo"), ["Notifier"], id="a port no one names is reported"),
    pytest.param(uses("modules/docs/adapters/db.py", "Repo", "Notifier"), [],
                 id="an adapter that names a port uses it"),
    pytest.param(uses("bootstrap/app.py", "Repo", "Notifier"), ["Repo", "Notifier"],
                 id="the part that may import everything only wires, and is no use"),
    pytest.param(uses("modules/docs/application/ports/__init__.py", "Repo", "Notifier"), ["Repo", "Notifier"],
                 id="a package file that re-exports is no use"),
    pytest.param(uses("modules/docs/domain/doc.py", "Other"), ["Repo", "Notifier"], id="a name that is another"),
])
def test_a_port_is_used_when_another_file_of_the_app_names_it(other, expected):
    lines = {"Repo": 3, "Notifier": 8}
    assert problems([PORTS, other]) == [dead_port(name, lines[name]) for name in expected]


def test_the_port_s_own_file_does_not_use_it_and_another_port_file_does():
    other = source("modules/docs/application/ports/more.py", named=frozenset({"Repo"}))
    assert problems([PORTS, other]) == [dead_port("Notifier", 8)]


def test_only_the_ports_of_the_parts_the_fakes_stand_in_for_are_read():
    elsewhere = source("modules/docs/domain/thing.py", classes=(REPO,), named=frozenset({"Repo"}))
    assert problems([elsewhere]) == []


@pytest.mark.parametrize("tests, expected", [
    pytest.param([in_tests("fakes/repo.py", classes=(fake("FakeRepo"),)),
                  in_tests("modules/docs/application/test_doc.py", named=frozenset({"FakeRepo"}))], [],
                 id="a fake a test names"),
    pytest.param([in_tests("fakes/repo.py", classes=(fake("FakeRepo"),))], ["FakeRepo"], id="a fake no test names"),
    pytest.param([in_tests("fakes/repo.py", classes=(fake("FakeRepo"), fake("Recorder", 5)))], ["FakeRepo"],
                 id="a class of the fakes folder that does not start with the prefix is no fake"),
    pytest.param([in_tests("fakes/repo.py", classes=(fake("FakeRepo", 1, "FakeNotifier"), fake("FakeNotifier", 6))),
                  in_tests("conftest.py", named=frozenset({"FakeRepo"}))], [],
                 id="a fake a used fake names is used"),
    pytest.param([in_tests("fakes/repo.py", classes=(fake("FakeRepo", 1, "FakeNotifier"), fake("FakeNotifier", 6)))],
                 ["FakeRepo", "FakeNotifier"], id="a fake only an unused fake names is not used"),
    pytest.param([in_tests("fakes/repo.py", classes=(fake("FakeA", 1, "FakeB"), fake("FakeB", 6, "FakeA")))],
                 ["FakeA", "FakeB"], id="two fakes that name each other are not used"),
    pytest.param([in_tests("fakes/repo.py", classes=(fake("FakeRepo"),)),
                  in_tests("fakes/__init__.py", named=frozenset({"FakeRepo"}))], ["FakeRepo"],
                 id="a file of the fakes folder with no class does not use a fake"),
    pytest.param([in_tests("fakes/repo.py", classes=(fake("FakeRepo"),)),
                  in_tests("builders.py", named=frozenset({"FakeRepo"}))], [], id="a helper of the tests uses it"),
])
def test_a_fake_is_used_when_a_test_file_outside_the_fakes_names_it_or_a_fake_that_is_used_does(tests, expected):
    names = {"FakeRepo": ("fakes/repo.py", 1), "FakeNotifier": ("fakes/repo.py", 6), "FakeA": ("fakes/repo.py", 1),
             "FakeB": ("fakes/repo.py", 6)}
    used = uses(SERVICE, "Repo", "Notifier")
    assert problems([PORTS, used], tests) == [
        f"tests/{names[name][0]}:{names[name][1]}: {name} is a fake that no test names (dead-code)"
        for name in expected]


def test_without_tests_the_fakes_are_not_looked_for_and_with_the_check_off_nothing_is():
    assert problems([PORTS], has_tests=False) == [dead_port("Repo", 3), dead_port("Notifier", 8)]
    assert problems([PORTS], checked=profile()) == []


def test_the_violations_say_what_to_do():
    port, = [v for v in violations([PORTS, uses(SERVICE, "Notifier")], [], ON, True)]
    assert (port.rule, port.fix) == ("dead-code", "delete Repo and its fake, or add the code that uses it")
    gone = in_tests("fakes/repo.py", classes=(fake("FakeRepo"),))
    [unused] = violations([PORTS, uses(SERVICE, "Repo", "Notifier")], [gone], ON, True)
    assert unused.fix == "delete FakeRepo, or write the test that uses it"
