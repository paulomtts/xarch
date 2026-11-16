"""The public names a profile accepts as only the tests' (guards.dead-code.known), on hand-made source files: a name
the tests-only check lists that an entry names is accepted and no longer listed, and an entry that no longer holds is
listed itself."""
import pytest

from tests.modules.rules.application.logic.checks import accepting
from tests.modules.rules.builders import profile, source
from xarch.modules.rules.domain.published import KnownName, Weak
from xarch.modules.rules.domain.values import Accepting, Class, Function

LOGIC = "modules/docs/application/logic/rule.py"
DEFINED = source(LOGIC, classes=(Class(3, "Rule"), Class(5, "_Hidden"), Class(7, "Refused", exception=True)),
                 functions=(Function(9, "decide"), Function(11, "_helper"), Function(13, "run", owner="Rule")),
                 named=frozenset({"Rule", "decide", "_helper", "run"}))
USER = source("modules/docs/application/services/doc.py", named=frozenset({"decide"}))
KEY = "guards.dead-code.known"


def listed(name: str, line: int) -> Weak:
    """What the tests-only check lists of a name of LOGIC."""
    return Weak("dead-code", f"app/{LOGIC}", line, f"{name} is public, but no other file of the app names it: only the "
                                                   "tests, or nothing, use it (guards.dead-code.tests_only)",
                f"delete {name} and what tests it alone, or make it private when its own file uses it, or use it where "
                "the app needs it")


def absent(path: str, name: str) -> Weak:
    """An entry whose file defines no public class or top-level function of its name."""
    return Weak("dead-code", f"app/{path}", 0, f"{path} defines no public class or top-level function {name}, which "
                                               f"{KEY} lists ({KEY})",
                f"drop {path}:{name} from {KEY}, or name the file and the name as they are now")


@pytest.mark.parametrize("app, known, then", [
    pytest.param([DEFINED], (), Accepting((listed("Rule", 3), listed("decide", 9)), ()),
                 id="with no entry the check lists what it finds"),
    pytest.param([DEFINED], (f"{LOGIC}:Rule",), Accepting((listed("decide", 9),), (KnownName(f"app/{LOGIC}", 3, "Rule"),)),
                 id="a class an entry names is accepted and no longer listed"),
    pytest.param([DEFINED], (f"{LOGIC}:decide", f"{LOGIC}:Rule"),
                 Accepting((), (KnownName(f"app/{LOGIC}", 9, "decide"), KnownName(f"app/{LOGIC}", 3, "Rule"))),
                 id="a top-level function too, each in the order of the entries"),
    pytest.param([DEFINED], (f"{LOGIC}:Gone",), Accepting((listed("Rule", 3), listed("decide", 9), absent(LOGIC, "Gone")), ()),
                 id="an entry whose file defines no such name is listed after what the check lists"),
    pytest.param([DEFINED], ("modules/docs/gone.py:Rule",),
                 Accepting((listed("Rule", 3), listed("decide", 9), absent("modules/docs/gone.py", "Rule")), ()),
                 id="an entry whose file the app does not hold is listed at that file"),
    pytest.param([DEFINED], (f"{LOGIC}:_helper", f"{LOGIC}:Refused", f"{LOGIC}:run"),
                 Accepting((listed("Rule", 3), listed("decide", 9), absent(LOGIC, "_helper"), absent(LOGIC, "Refused"),
                            absent(LOGIC, "run")), ()),
                 id="a private name, an exception and a method are none of what the check reads"),
    pytest.param([DEFINED, USER], (f"{LOGIC}:decide",),
                 Accepting((listed("Rule", 3), Weak("dead-code", f"app/{LOGIC}", 9,
                                                    f"decide is listed by {KEY} as only the tests', but another file of "
                                                    f"the app names it ({KEY})", f"drop {LOGIC}:decide from {KEY}: the app uses it")), ()),
                 id="an entry whose name another file of the app names is listed at the name"),
])
def test_the_names_a_profile_accepts_as_only_the_tests_are_taken_out_and_those_that_no_longer_are_listed(app, known, then):
    assert accepting(app, profile(dead_code=True, tests_only=True, tests_only_known=known), "app") == then


def test_with_the_tests_only_check_off_nothing_is_listed_or_accepted():
    assert accepting([DEFINED], profile(dead_code=True, tests_only_known=(f"{LOGIC}:Rule",)), "app") == Accepting((), ())
