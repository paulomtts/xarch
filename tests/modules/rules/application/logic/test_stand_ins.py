"""The stand-ins guard on hand-made source files: a port is read or fire-only by its return annotations, a read port
has a fake, a mock in a test that may use the fakes names a spec that is not a read port, and a fake that does not
define every method of its port is weak."""
from dataclasses import replace

import pytest

from tests.modules.rules.builders import AUTOSPEC, MOCK, PROFILE, in_tests, profile, source
from xarch.modules.rules.application.logic.stand_ins import violations, weak
from xarch.modules.rules.domain.values import Call, Class, Method, ParameterCall, Weak

PROTOCOL = ("typing", "Protocol")
PORT_FILE = "modules/docs/application/ports/repo.py"
REPO = ("app", "modules", "docs", "application", "ports", "repo", "Repo")
NOTIFIER = ("app", "modules", "docs", "application", "ports", "repo", "Notifier")
READ = Class(3, "Repo", (PROTOCOL,), (Method(4, "get", "str | None"), Method(5, "save", "None")))
FIRE = Class(8, "Notifier", (PROTOCOL,), (Method(9, "send", "None"),))
PORTS = source(PORT_FILE, classes=(READ, FIRE))
FAKE = in_tests("fakes/repo.py", classes=(Class(1, "FakeRepo", (), (Method(2, "get", None), Method(3, "save", None))),))
INTEGRATION_TEST = "modules/docs/application/test_publish.py"


def problems(app, tests=(FAKE,), checked=PROFILE, has_tests=True) -> list[str]:
    return [str(v) for v in violations(list(app), list(tests), checked, "app", has_tests)]


def ported(*classes: Class, path: str = PORT_FILE):
    return source(path, classes=classes)


@pytest.mark.parametrize("classes, expected", [
    pytest.param([READ, FIRE], [], id="a read port with its fake and a fire-only port pass"),
    pytest.param([Class(3, "Repo", (("typing_extensions", "Protocol"),), (Method(4, "get", "int"),))], [],
                 id="typing_extensions' Protocol makes a port too"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "get", "int"),))],
                 [f"app/{PORT_FILE}:3: Store is a read port with no fake (stand-ins)"],
                 id="a read port with no fake is reported at the port"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "get", "None"), Method(5, "put", "None")))], [],
                 id="a fire-only port needs no fake"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "get", "int"),)),
                  Class(6, "Other", (PROTOCOL,), (Method(7, "get", "None"),))],
                 [f"app/{PORT_FILE}:3: Store is a read port with no fake (stand-ins)"],
                 id="only the read ports of a file need fakes"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "get", None), Method(5, "put", "int")))],
                 [f"app/{PORT_FILE}:4: Store.get has no return annotation, and whether Store is fire-only or read "
                  "follows from it (stand-ins)"],
                 id="a method with no return annotation is reported, and the port then has no kind"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "__init__", None), Method(5, "send", "None")))], [],
                 id="a dunder method is not one of the port's methods"),
    pytest.param([Class(3, "Store", (PROTOCOL,), (Method(4, "__call__", "int"),))],
                 [f"app/{PORT_FILE}:3: Store is a read port with no fake (stand-ins)"],
                 id="__call__ is the method a callable port is"),
    pytest.param([Class(3, "Store", (PROTOCOL,), ())], [], id="a port with no methods is neither kind"),
    pytest.param([Class(3, "Store", (("app", "Base"),), (Method(4, "get", "int"),))], [],
                 id="a class that is not a Protocol is not a port"),
    pytest.param([Class(3, "Store", (None,), (Method(4, "get", "int"),))], [],
                 id="a class whose base is not a name an import binds is not a port"),
])
def test_ports(classes, expected):
    assert problems([ported(*classes)]) == expected


def test_a_protocol_outside_the_parts_the_fakes_stand_in_for_is_not_a_port():
    store = Class(3, "Store", (PROTOCOL,), (Method(4, "get", None),))
    assert problems([ported(store, path="modules/docs/domain/store.py"), ported(store, path="scripts/store.py")]) == []


@pytest.mark.parametrize("tests", [
    pytest.param([], id="no fakes at all"),
    pytest.param([in_tests("modules/docs/fakes.py", classes=(Class(1, "FakeRepo"),))],
                 id="a class of the fake's name outside the fakes' folder"),
    pytest.param([in_tests("fakes/repo.py", classes=(Class(1, "RepoFake"),))], id="a fake named otherwise"),
])
def test_a_read_port_without_a_fake_below_the_fakes_folder_is_reported(tests):
    assert problems([PORTS], tests) == [
        f"app/{PORT_FILE}:3: Repo is a read port with no fake (stand-ins)"]


def test_without_a_tests_root_missing_fakes_are_not_reported():
    assert problems([PORTS], [], has_tests=False) == []


def test_without_a_tests_root_ports_are_still_held_to_their_annotations():
    bare = Class(3, "Store", (PROTOCOL,), (Method(4, "get", None),))
    assert problems([ported(bare)], [], has_tests=False) == [
        f"app/{PORT_FILE}:4: Store.get has no return annotation, and whether Store is fire-only or read follows from it (stand-ins)"]


@pytest.mark.parametrize("checked", [
    pytest.param(profile(stand_ins=None), id="the guard is off"),
    pytest.param(profile(fakes=None), id="the profile has no fakes"),
])
def test_without_the_guard_or_fakes_nothing_is_checked(checked):
    bare = Class(3, "Store", (PROTOCOL,), (Method(4, "get", None),))
    tests = [in_tests(INTEGRATION_TEST, calls=(Call(5, MOCK),)), in_tests("fakes/x.py", classes=(Class(1, "FakeStore"),))]
    assert (problems([ported(bare)], tests, checked), weak([ported(bare)], tests, checked)) == ([], [])


NO_SPEC = (f"tests/{INTEGRATION_TEST}:5: Mock() names nothing it stands in for (stand-ins)")
AUTOSPEC_NO_SPEC = (f"tests/{INTEGRATION_TEST}:5: create_autospec() names nothing it stands in for (stand-ins)")


@pytest.mark.parametrize("call, expected", [
    pytest.param(Call(5, MOCK), [NO_SPEC], id="a mock with no spec is reported"),
    pytest.param(Call(5, MOCK, keywords=(("name", None),)), [NO_SPEC], id="a keyword that is not a spec names none"),
    pytest.param(Call(5, MOCK, (NOTIFIER,)), [], id="a fire-only port given first is a spec"),
    pytest.param(Call(5, MOCK, keywords=(("spec", NOTIFIER),)), [], id="a fire-only port by spec= is a spec"),
    pytest.param(Call(5, MOCK, keywords=(("spec_set", NOTIFIER),)), [], id="a fire-only port by spec_set= is a spec"),
    pytest.param(Call(5, ("unittest", "mock", "MagicMock")), [NO_SPEC.replace("Mock()", "MagicMock()", 1)],
                 id="every mock the profile lists is checked"),
    pytest.param(Call(5, AUTOSPEC, (NOTIFIER,)), [], id="create_autospec given its spec first passes"),
    pytest.param(Call(5, AUTOSPEC, keywords=(("spec", NOTIFIER),)), [], id="create_autospec by spec= passes"),
    pytest.param(Call(5, AUTOSPEC, keywords=(("spec_set", NOTIFIER),)), [AUTOSPEC_NO_SPEC],
                 id="spec_set is not a keyword create_autospec takes its spec by"),
    pytest.param(Call(5, AUTOSPEC), [AUTOSPEC_NO_SPEC], id="create_autospec with no spec is reported"),
    pytest.param(Call(5, MOCK, keywords=(("spec", REPO),)),
                 [f"tests/{INTEGRATION_TEST}:5: Mock(spec=Repo) stands in for Repo, a read port (stand-ins)"],
                 id="a mock of a read port by keyword is reported, pointing to its fake"),
    pytest.param(Call(5, MOCK, (REPO,)),
                 [f"tests/{INTEGRATION_TEST}:5: Mock(Repo) stands in for Repo, a read port (stand-ins)"],
                 id="a mock of a read port given first is reported as written"),
    pytest.param(Call(5, AUTOSPEC, (REPO,)),
                 [f"tests/{INTEGRATION_TEST}:5: create_autospec(Repo) stands in for Repo, a read port (stand-ins)"],
                 id="an autospec of a read port is reported"),
    pytest.param(Call(5, MOCK, unpacked=True), [], id="a mock that unpacks its arguments is not read"),
    pytest.param(Call(5, MOCK, (None,)), [], id="a spec that is not a name an import binds is not read"),
    pytest.param(Call(5, MOCK, (("app", "modules", "docs", "application", "ports", "Repo"),)), [],
                 id="a read port imported from a package that re-exports it is not followed"),
    pytest.param(Call(5, MOCK, (("other", "modules", "docs", "application", "ports", "repo", "Repo"),)), [],
                 id="a spec outside the app is no port"),
    pytest.param(Call(5, ("unittest", "mock", "patch"), ("x",)), [], id="patch is not one of the mocks"),
])
def test_mocks_in_a_test_that_may_use_the_fakes(call, expected):
    assert problems([PORTS], [FAKE, in_tests(INTEGRATION_TEST, calls=(call,))]) == expected


NO_SPEC_FIXTURE = (f"tests/{INTEGRATION_TEST}:5: mocker.Mock() names nothing it stands in for (stand-ins)")
AUTOSPEC_NO_SPEC_FIXTURE = (f"tests/{INTEGRATION_TEST}:5: mocker.create_autospec() names nothing it stands in for (stand-ins)")


@pytest.mark.parametrize("call, expected", [
    pytest.param(ParameterCall(5, "mocker", "Mock"), [NO_SPEC_FIXTURE], id="a fixture's mock with no spec is reported"),
    pytest.param(ParameterCall(5, "mocker", "MagicMock"), [NO_SPEC_FIXTURE.replace("mocker.Mock()", "mocker.MagicMock()", 1)],
                 id="every mock method the fixture lists is checked"),
    pytest.param(ParameterCall(5, "mocker", "Mock", keywords=(("name", None),)), [NO_SPEC_FIXTURE],
                 id="a keyword that is not a spec names none"),
    pytest.param(ParameterCall(5, "mocker", "Mock", (NOTIFIER,)), [], id="a fire-only port given first is a spec"),
    pytest.param(ParameterCall(5, "mocker", "Mock", keywords=(("spec", NOTIFIER),)), [],
                 id="a fire-only port by spec= is a spec"),
    pytest.param(ParameterCall(5, "mocker", "Mock", keywords=(("spec_set", NOTIFIER),)), [],
                 id="a fire-only port by spec_set= is a spec"),
    pytest.param(ParameterCall(5, "mocker", "create_autospec", (NOTIFIER,)), [],
                 id="the fixture's autospec given its spec first passes"),
    pytest.param(ParameterCall(5, "mocker", "create_autospec", keywords=(("spec_set", NOTIFIER),)),
                 [AUTOSPEC_NO_SPEC_FIXTURE], id="spec_set is not a keyword the fixture's autospec takes its spec by"),
    pytest.param(ParameterCall(5, "mocker", "create_autospec"), [AUTOSPEC_NO_SPEC_FIXTURE],
                 id="the fixture's autospec with no spec is reported"),
    pytest.param(ParameterCall(5, "mocker", "Mock", keywords=(("spec", REPO),)),
                 [f"tests/{INTEGRATION_TEST}:5: mocker.Mock(spec=Repo) stands in for Repo, a read port (stand-ins)"],
                 id="a fixture's mock of a read port by keyword is reported, pointing to its fake"),
    pytest.param(ParameterCall(5, "mocker", "Mock", (REPO,)),
                 [f"tests/{INTEGRATION_TEST}:5: mocker.Mock(Repo) stands in for Repo, a read port (stand-ins)"],
                 id="a fixture's mock of a read port given first is reported as written"),
    pytest.param(ParameterCall(5, "mocker", "create_autospec", (REPO,)),
                 [f"tests/{INTEGRATION_TEST}:5: mocker.create_autospec(Repo) stands in for Repo, a read port (stand-ins)"],
                 id="a fixture's autospec of a read port is reported"),
    pytest.param(ParameterCall(5, "mocker", "Mock", unpacked=True), [], id="a fixture's mock that unpacks is not read"),
    pytest.param(ParameterCall(5, "mocker", "Mock", (None,)), [], id="a spec that is not a name an import binds is not read"),
    pytest.param(ParameterCall(5, "mocker", "create_autospec", (None,)), [],
                 id="an autospec of something that is not a name is not read"),
    pytest.param(ParameterCall(5, "mocker", "create_autospec", unpacked=True), [],
                 id="an autospec that unpacks is not read"),
    pytest.param(ParameterCall(5, "mocker", "patch", ("x",)), [], id="a method the fixture does not list is not a mock"),
    pytest.param(ParameterCall(5, "other", "Mock"), [], id="a parameter the profile does not list is not a fixture"),
    pytest.param(ParameterCall(5, "mocker", "Mock", (NOTIFIER,), unpacked=True), [],
                 id="a spec given first is enough even when the call also unpacks"),
])
def test_mocks_a_fixture_builds_follow_the_rules_of_the_imported_ones(call, expected):
    assert problems([PORTS], [FAKE, in_tests(INTEGRATION_TEST, parameter_calls=(call,))]) == expected


def test_a_fixture_is_no_import_so_a_call_named_like_its_method_is_read_as_a_call_only():
    assert problems([PORTS], [FAKE, in_tests(INTEGRATION_TEST, calls=(Call(5, ("mocker", "Mock")),))]) == []


def test_without_fixtures_in_the_profile_a_parameter_call_is_not_read():
    checked = profile(stand_ins=replace(PROFILE.stand_ins, fixtures=()))
    assert problems([PORTS], [FAKE, in_tests(INTEGRATION_TEST, parameter_calls=(ParameterCall(5, "mocker", "Mock"),))],
                    checked) == []


@pytest.mark.parametrize("path", [
    pytest.param("modules/docs/domain/test_doc.py", id="a unit test"),
    pytest.param("web/test_page.py", id="a rendering test"),
    pytest.param("scripts/test_x.py", id="a test in no tier"),
    pytest.param("fakes/helpers.py", id="a fake"),
])
def test_mocks_in_a_test_that_may_not_use_the_fakes_are_not_checked(path):
    assert problems([PORTS], [FAKE, in_tests(path, calls=(Call(5, MOCK),),
                                             parameter_calls=(ParameterCall(5, "mocker", "Mock"),))]) == []


def fakes(*classes: Class, path: str = "fakes/repo.py"):
    return in_tests(path, classes=classes)


SHORT = f"FakeRepo does not define save, which Repo declares (app/{PORT_FILE})"


@pytest.mark.parametrize("tests, expected", [
    pytest.param([FAKE], [], id="a fake defining every method of its port is not weak"),
    pytest.param([fakes(Class(1, "FakeRepo", (), (Method(2, "get", None),)))],
                 [Weak("stand-ins", "tests/fakes/repo.py", 1, SHORT)], id="a fake missing a method is weak"),
    pytest.param([fakes(Class(1, "FakeRepo", (), (Method(2, "get", None),), ("save",)))], [],
                 id="an attribute of the method's name counts as defined"),
    pytest.param([fakes(Class(1, "FakeRepo", (REPO,)))],
                 [Weak("stand-ins", "tests/fakes/repo.py", 1,
                       f"FakeRepo does not define get, save, which Repo declares (app/{PORT_FILE})")],
                 id="a fake that only subclasses its port is weak, since inherited methods are not followed"),
    pytest.param([fakes(Class(1, "FakeRepo", (), (Method(2, "get", None),)), path="modules/docs/fakes.py")], [],
                 id="a class outside the fakes' folder is not a fake"),
    pytest.param([fakes(Class(1, "FakeOther", ()))], [], id="a fake of no port is not weak"),
    pytest.param([fakes(Class(1, "FakeNotifier", ()))],
                 [Weak("stand-ins", "tests/fakes/repo.py", 1,
                       f"FakeNotifier does not define send, which Notifier declares (app/{PORT_FILE})")],
                 id="a fake of a fire-only port is held to its methods too"),
])
def test_weak(tests, expected):
    assert weak([PORTS], tests, PROFILE) == expected


OTHER_FILE = "modules/other/application/ports/repo.py"
OTHER_REPO = Class(3, "Repo", (PROTOCOL,), (Method(4, "get", "int"), Method(5, "list", "int"),
                                            Method(6, "drop", "None")))


@pytest.mark.parametrize("defined, expected", [
    pytest.param(("get", "save"), [], id="a fake meeting one of the ports of its name is not weak"),
    pytest.param(("get",), [Weak("stand-ins", "tests/fakes/repo.py", 1, SHORT)],
                 id="a fake short of every port of its name is shown against the closest"),
])
def test_a_fake_serves_every_port_of_its_name(defined, expected):
    fake = fakes(Class(1, "FakeRepo", (), tuple(Method(2, m, None) for m in defined)))
    assert weak([PORTS, ported(OTHER_REPO, path=OTHER_FILE)], [fake], PROFILE) == expected


def test_one_fake_serves_read_ports_of_the_same_name_in_two_instances():
    assert problems([PORTS, ported(OTHER_REPO, path=OTHER_FILE)]) == []


@pytest.mark.parametrize("app, tests, fix", [
    pytest.param([PORTS], [], "write FakeRepo under tests/fakes/", id="a read port with no fake"),
    pytest.param([ported(Class(3, "Store", (PROTOCOL,), (Method(4, "get", None),)))], [FAKE],
                 "annotate what Store.get returns", id="a method with no return annotation"),
    pytest.param([PORTS], [FAKE, in_tests(INTEGRATION_TEST, calls=(Call(5, MOCK),))],
                 "give it a spec, such as Mock(spec=<port>)", id="a mock with no spec"),
    pytest.param([PORTS], [FAKE, in_tests(INTEGRATION_TEST, calls=(Call(5, AUTOSPEC),))],
                 "give it a spec, such as Mock(spec=<port>)", id="an autospec with no spec"),
    pytest.param([PORTS], [FAKE, in_tests(INTEGRATION_TEST, parameter_calls=(ParameterCall(5, "mocker", "Mock"),))],
                 "give it a spec, such as mocker.Mock(spec=<port>)", id="a fixture's mock with no spec"),
    pytest.param([PORTS], [FAKE, in_tests(INTEGRATION_TEST, calls=(Call(5, MOCK, (REPO,)),))],
                 "use its fake FakeRepo", id="a mock of a read port"),
    pytest.param([PORTS], [FAKE, in_tests(INTEGRATION_TEST, parameter_calls=(ParameterCall(5, "mocker", "Mock",
                                                                                           (REPO,)),))],
                 "use its fake FakeRepo", id="a fixture's mock of a read port"),
])
def test_a_violation_names_its_rule_and_says_what_to_do(app, tests, fix):
    assert [(v.rule, v.fix) for v in violations(app, tests, PROFILE, "app")] == [("stand-ins", fix)]
