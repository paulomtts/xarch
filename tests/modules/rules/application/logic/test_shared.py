"""The shared check on hand-made source files: every public name a part declared shared defines at the top level is
used by at least as many users as it says, a user being an instance of a repeating folder or a part outside them."""
import pytest

from tests.modules.rules.builders import imp, profile, source
from xarch.modules.rules.application.logic.shared import violations
from xarch.modules.rules.domain.parsed import Class, Constant, Function, Use

ON = profile(shared={"kernel": 2})
WEAK = source("kernel/violations.py", classes=(Class(40, "Weak"),))


def problems(*files, checked=ON) -> list[str]:
    return [str(v) for v in violations(list(files), checked, "app")]


def user(path: str, *names: str, module: str = "app.kernel.violations") -> object:
    """A file that imports the names from module and mentions them."""
    return source(path, imp(1, module, *names))


def test_a_name_one_user_uses_is_reported_naming_that_user_with_what_to_do():
    found = violations([WEAK, user("modules/rules/domain/values.py", "Weak"),
                        user("modules/rules/application/logic/engine.py", "Weak")], ON, "app")
    assert [(str(v), v.rule, v.fix) for v in found] == [(
        "app/kernel/violations.py:40: the class Weak is used by modules/rules alone, but kernel/ holds only what at "
        "least 2 users share (parts.kernel.shared)", "shared",
        "move Weak to modules/rules, its one user, or to the published types of modules/rules if others read it "
        "through them")]


@pytest.mark.parametrize("users, reported", [
    pytest.param(("modules/rules/domain/values.py", "modules/spec/domain/values.py"), False, id="two instances"),
    pytest.param(("modules/rules/domain/values.py", "web/report.py"), False,
                 id="an instance and a part outside every repeating folder"),
    pytest.param(("web/report.py", "bootstrap/wiring.py"), False, id="two parts outside them"),
    pytest.param(("modules/rules/domain/values.py", "modules/rules/contract/__init__.py"), True,
                 id="two parts of one instance are one user"),
    pytest.param(("modules/rules/domain/values.py", "scripts/seed.py"), True, id="a file in no part is no user"),
])
def test_a_user_is_an_instance_of_a_repeating_folder_or_a_part_outside_them(users, reported):
    assert bool(problems(WEAK, *(user(path, "Weak") for path in users))) == reported


def test_another_file_of_the_shared_part_is_no_user():
    assert problems(WEAK, user("kernel/report.py", "Weak"), user("modules/rules/domain/values.py", "Weak")) == [
        "app/kernel/violations.py:40: the class Weak is used by modules/rules alone, but kernel/ holds only what at "
        "least 2 users share (parts.kernel.shared)"]


def test_a_name_nothing_outside_the_part_uses_is_reported_as_used_by_none():
    found = violations([WEAK], ON, "app")
    assert [(str(v), v.fix) for v in found] == [(
        "app/kernel/violations.py:40: the class Weak is used by nothing outside kernel/, but kernel/ holds only what "
        "at least 2 users share (parts.kernel.shared)",
        "move Weak next to the code that uses it, or delete it if nothing does")]


def test_a_name_fewer_users_than_the_part_asks_for_use_is_reported_naming_them():
    found = violations([WEAK, user("modules/rules/domain/values.py", "Weak"), user("web/report.py", "Weak")],
                       profile(shared={"kernel": 3}), "app")
    assert [(str(v), v.fix) for v in found] == [(
        "app/kernel/violations.py:40: the class Weak is used by modules/rules and web/ only, but kernel/ holds only "
        "what at least 3 users share (parts.kernel.shared)",
        "move Weak to the user that owns it and have the others import it from there")]


def test_a_function_and_a_constant_count_and_a_private_name_or_a_method_does_not():
    kernel = source("kernel/ids.py", functions=(Function(3, "make"), Function(5, "_raw"), Function(7, "get", owner="K")),
                    constants=(Constant(1, "PREFIX"), Constant(2, "_SEP")), module_functions=("make", "_raw"))
    assert problems(kernel) == [
        "app/kernel/ids.py:1: the constant PREFIX is used by nothing outside kernel/, but kernel/ holds only what at "
        "least 2 users share (parts.kernel.shared)",
        "app/kernel/ids.py:3: the function make is used by nothing outside kernel/, but kernel/ holds only what at "
        "least 2 users share (parts.kernel.shared)"]


def test_a_name_read_through_an_import_of_its_file_is_used():
    kernel = source("kernel/ids.py", functions=(Function(3, "make"),), module_functions=("make",))
    users = [source(path, imp(1, "app.kernel", "ids"), uses=(Use(4, ("app", "kernel", "ids", "make", "now"), 3),))
             for path in ("modules/rules/domain/values.py", "web/report.py")]
    assert problems(kernel, *users, source("kernel/__init__.py")) == []


def test_an_import_of_a_name_the_file_never_mentions_is_a_re_export_and_no_use():
    passing = source("modules/rules/domain/values.py", imp(1, "app.kernel.violations", "Weak"),
                     unmentioned=frozenset({(1, "Weak")}))
    assert problems(WEAK, passing, user("web/report.py", "Weak")) == [
        "app/kernel/violations.py:40: the class Weak is used by web/ alone, but kernel/ holds only what at least 2 "
        "users share (parts.kernel.shared)"]


def test_a_name_imported_through_a_re_export_is_used_by_whoever_imports_it_from_there():
    passing = source("modules/rules/domain/values.py", imp(1, "app.kernel.violations", "Weak"),
                     unmentioned=frozenset({(1, "Weak")}))
    through = user("modules/spec/domain/values.py", "Weak", module="app.modules.rules.domain.values")
    assert problems(WEAK, passing, through, user("web/report.py", "Weak")) == []


def test_a_name_another_name_of_the_part_mentions_is_used_by_that_name_s_users():
    kernel = source("kernel/origin.py", classes=(Class(5, "Loosened"), Class(12, "Origin", named=frozenset({"Loosened"}))))
    users = [user(path, "Origin", module="app.kernel.origin") for path in ("modules/rules/domain/values.py",
                                                                          "modules/spec/domain/values.py")]
    assert problems(kernel, *users) == []


def test_the_mention_is_followed_through_the_imports_of_the_part_s_own_files_and_its_private_names():
    helpers = source("kernel/steps.py", functions=(Function(3, "steps"),), module_functions=("steps",))
    place = source("kernel/place.py", imp(1, "app.kernel.steps", "steps"),
                   functions=(Function(5, "_walk", named=frozenset({"steps"})),
                              Function(9, "place_of", named=frozenset({"_walk"}))),
                   module_functions=("_walk", "place_of"))
    users = [user(path, "place_of", module="app.kernel.place") for path in ("modules/rules/domain/values.py",
                                                                           "web/report.py")]
    assert problems(helpers, place, *users) == []


def test_the_check_is_off_for_a_part_that_is_not_shared():
    assert problems(WEAK, checked=profile()) == []
    assert problems(source("modules/rules/domain/values.py", classes=(Class(3, "Only"),))) == []


def test_a_file_of_another_shared_part_is_no_user_but_passes_on_the_users_of_its_names_that_mention_the_name():
    both = profile(shared={"kernel": 2, "web": 2})
    helper = source("kernel/steps.py", functions=(Function(3, "steps"),), module_functions=("steps",))
    plain = source("web/report.py", imp(1, "app.kernel.steps", "steps"))
    assert problems(helper, plain, user("modules/rules/domain/values.py", "steps", module="app.kernel.steps"),
                    checked=both)[0].startswith("app/kernel/steps.py:3: the function steps is used by modules/rules alone")
    mentioning = source("web/report.py", imp(1, "app.kernel.steps", "steps"),
                        functions=(Function(5, "report", named=frozenset({"steps"})),), module_functions=("report",))
    users = [user(path, "report", module="app.web.report") for path in ("modules/rules/domain/values.py",
                                                                       "modules/spec/domain/values.py")]
    assert problems(helper, mentioning, *users, checked=both) == []
