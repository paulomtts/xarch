"""The top-level `counterparts` key: each entry, by an id of its own, says that what lies at a path (`for`) has
something at another (`has`), optionally only where other paths exist too (`when`), with the sources it accepts one by
one, its message and its fix; placeholders (`<store>`) bind text in `for` and are put back in `has` and `when`; every
way of writing one wrong is refused at its address."""
import pytest

from tests.modules.spec.profiles import SOURCE as FILE
from tests.modules.spec.profiles import layered, parsed
from tests.modules.spec.profiles import problems as refused
from xarch.modules.spec.application.logic.explain import held_by, key_at
from xarch.modules.spec.domain.published import AcceptedPath, Counterpart, PathPattern


def test_a_profile_without_counterparts_has_none():
    assert parsed(layered()).counterparts == ()


def test_each_counterpart_loads_with_its_paths_in_the_order_of_the_file():
    architecture = parsed(layered(counterparts={
        "store-has-contract": {
            "for": "src/<module>/store/", "when": ["tests/fakes/<module>/"], "has": "tests/conformance/<module>/",
            "accepted": [{"path": "src/billing/store/", "why": "billing reads the old store until it is retired"}],
            "message": "{source} has no contract", "fix": "write {expected}"},
        "port-has-file": {"for": "src/<module>/service/<port>_repo.py", "has": "src/<module>/store/<port>_repo.py"},
    }))
    assert architecture.counterparts == (
        Counterpart("store-has-contract", PathPattern(("src", "<module>", "store"), True),
                    PathPattern(("tests", "conformance", "<module>"), True),
                    (PathPattern(("tests", "fakes", "<module>"), True),),
                    (AcceptedPath(("src", "billing", "store"), "billing reads the old store until it is retired"),),
                    "{source} has no contract", "write {expected}"),
        Counterpart("port-has-file", PathPattern(("src", "<module>", "service", "<port>_repo.py"), False),
                    PathPattern(("src", "<module>", "store", "<port>_repo.py"), False)),
    )


def test_a_path_pattern_is_written_as_the_profile_writes_it():
    assert PathPattern(("tests", "conformance", "<store>"), True).written == "tests/conformance/<store>/"
    assert PathPattern(("src", "<port>_repo.py"), False).written == "src/<port>_repo.py"


def problems(document: dict) -> list[str]:
    """The problems of the document, each without the name of the file it is in."""
    return [problem.removeprefix(f"{FILE}: ") for problem in refused(document)]


def one(**entry) -> list[str]:
    """The problems of a profile with one counterpart, `x`, written as given."""
    return problems(layered(counterparts={"x": entry}))


SOURCE = {"for": "src/<module>/store/", "has": "tests/conformance/<module>/"}


@pytest.mark.parametrize("value, problem", [
    pytest.param(["x"], "counterparts: must be a map of counterparts by id, such as {document-has-check: {for: "
                        "documents/<name>/, has: tests/documents/<name>/}}", id="a list instead of a map"),
    pytest.param({"Store": SOURCE}, "counterparts: 'Store' is no id of a counterpart: write lowercase words joined by "
                                    "-, such as document-has-check", id="an id that is not one"),
    pytest.param({"x": "src/"}, "counterparts.x: must be a map {for, has, when, accepted, message, fix}",
                 id="an entry that is no map"),
])
def test_counterparts_written_wrong_are_refused(value, problem):
    assert problem in problems(layered(counterparts=value))


@pytest.mark.parametrize("entry, problem", [
    pytest.param({"has": "src/"}, "counterparts.x: missing `for`", id="no for"),
    pytest.param({"for": "src/"}, "counterparts.x: missing `has`", id="no has"),
    pytest.param({**SOURCE, "needs": []}, "counterparts.x: unknown key 'needs': use accepted, fix, for, has, message, "
                                          "when", id="an unknown key"),
    pytest.param({**SOURCE, "for": "src/../x/"}, "counterparts.x.for: 'src/../x/': must be a path below the app, or "
                                                 "tests/<path> below the tests, such as documents/<name>/",
                 id="a path that leaves the app"),
    pytest.param({**SOURCE, "for": "tests/"}, "counterparts.x.for: 'tests/': must be a path below the app, or "
                                              "tests/<path> below the tests, such as documents/<name>/",
                 id="the tests root itself"),
    pytest.param({**SOURCE, "has": 3}, "counterparts.x.has: 3: must be a path below the app, or tests/<path> below "
                                       "the tests, such as documents/<name>/", id="no text"),
    pytest.param({**SOURCE, "for": "src/<Mod ule>/"}, "counterparts.x.for: 'src/<Mod ule>/': a placeholder holds a "
                                                      "name, such as <name>", id="a placeholder holding no name"),
    pytest.param({**SOURCE, "for": "src/<module/"}, "counterparts.x.for: 'src/<module/': a placeholder holds a name, "
                                                    "such as <name>", id="a placeholder left open"),
    pytest.param({**SOURCE, "for": "src/<a><b>.py"}, "counterparts.x.for: 'src/<a><b>.py': the step '<a><b>.py' puts "
                                                     "two placeholders, or a placeholder and `*`, side by side, which "
                                                     "bind text more ways than one: write text between them",
                 id="two placeholders side by side"),
    pytest.param({**SOURCE, "for": "src/<a>*.py"}, "counterparts.x.for: 'src/<a>*.py': the step '<a>*.py' puts two "
                                                   "placeholders, or a placeholder and `*`, side by side, which bind "
                                                   "text more ways than one: write text between them",
                 id="a placeholder beside a star"),
    pytest.param({**SOURCE, "has": "tests/conformance/<store>/"}, "counterparts.x.has: <store> is bound by no step of "
                                                                  "for", id="has names a placeholder for does not bind"),
    pytest.param({**SOURCE, "when": ["tests/fakes/<port>/"]}, "counterparts.x.when.0: <port> is bound by no step of "
                                                              "for", id="when names a placeholder for does not bind"),
    pytest.param({**SOURCE, "has": "src/<module>/store/"}, "counterparts.x.has: is the path of for: a counterpart "
                                                           "lies elsewhere", id="has is for"),
    pytest.param({**SOURCE, "when": "tests/fakes/<module>/"}, "counterparts.x.when: must be a list of paths, such as "
                                                              "[tests/fakes/<name>/]", id="when no list"),
    pytest.param({**SOURCE, "message": "a\nb"}, "counterparts.x.message: must be one line of text", id="a message of "
                                                                                                       "two lines"),
    pytest.param({**SOURCE, "fix": "write {file}"}, "counterparts.x.fix: {file} is no variable: use {source}, "
                                                    "{expected}, {when}, {key} or a placeholder of for ({module})",
                 id="a variable that is none"),
    pytest.param({**SOURCE, "accepted": [{"path": "src/billing/store/"}]}, "counterparts.x.accepted.0: missing `why`",
                 id="an accepted entry with no reason"),
    pytest.param({**SOURCE, "accepted": {"src/billing/store/": "why"}}, "counterparts.x.accepted: must be a list of "
                                                                        "{path, why}, such as [{path: <a path for "
                                                                        "matches>, why: <the reason>}]",
                 id="accepted no list"),
])
def test_a_counterpart_written_wrong_is_refused_at_its_address(entry, problem):
    assert problem in one(**entry)


def test_a_counterpart_written_right_loads_with_every_variable_of_its_message():
    architecture = parsed(layered(counterparts={"x": {**SOURCE, "when": ["tests/fakes/<module>/"],
                                                      "message": "{source} {expected} {when} {key} {module}",
                                                      "fix": "write {expected}"}}))
    assert architecture.counterparts[0].message == "{source} {expected} {when} {key} {module}"


def test_profile_explain_counterparts_shows_every_slot_and_finds_one_under_any_id():
    shown = [slot.address for slot in held_by(key_at("counterparts"))]
    assert shown == [f"counterparts.<id>.{slot}" for slot in ("for", "has", "when", "accepted", "message", "fix")]
    assert key_at("counterparts.store-has-contract.has").address == "counterparts.<id>.has"
    assert key_at("counterparts.<id>.when").rules == ("counterpart",)
