"""The no-twins check on hand-made source files: two public classes in different parts that declare the same fields in
the same order are one type written twice."""
import pytest

from tests.modules.rules.builders import profile, source
from xarch.modules.rules.application.logic.twins import violations
from xarch.modules.rules.domain.values import Class

ON = profile(no_twins=3)
DOMAIN = "modules/docs/domain/values.py"
CONTRACT = "modules/docs/contract/__init__.py"
LOGIC = "modules/docs/application/logic/rule.py"
FIELDS = ("key", "part", "what")


def problems(*files, checked=ON) -> list[str]:
    return [str(v) for v in violations(list(files), checked)]


def test_a_twin_in_another_part_is_reported_naming_both_places_with_what_to_do():
    found = violations([source(CONTRACT, classes=(Class(9, "LoosenedView", fields=FIELDS),)),
                        source(DOMAIN, classes=(Class(5, "Loosened", fields=FIELDS),))], ON)
    assert [(str(v), v.rule, v.fix) for v in found] == [(
        "app/modules/docs/contract/__init__.py:9: LoosenedView declares the fields of Loosened at "
        "app/modules/docs/domain/values.py:5 in the same order (key, part, what): contract/ of modules/docs and "
        "domain/ of modules/docs hold one type written twice (no-twins)", "no-twins",
        "keep one of the two and import it from a part both may import, or give LoosenedView the fields its reader "
        "needs instead of a copy of Loosened's")]


@pytest.mark.parametrize("first, second, reported", [
    pytest.param(Class(5, "A", fields=FIELDS), Class(9, "B", fields=("key", "what", "part")), False,
                 id="the same names in another order"),
    pytest.param(Class(5, "A", fields=FIELDS), Class(9, "B", fields=(*FIELDS, "more")), False,
                 id="one field more"),
    pytest.param(Class(5, "A", fields=FIELDS[:2]), Class(9, "B", fields=FIELDS[:2]), False,
                 id="fewer fields than the minimum"),
    pytest.param(Class(5, "_A", fields=FIELDS), Class(9, "B", fields=FIELDS), False, id="a private class"),
    pytest.param(Class(5, "A", (("typing", "Protocol"),), fields=FIELDS), Class(9, "B", fields=FIELDS), False,
                 id="an interface, whose fields are a requirement"),
    pytest.param(Class(5, "A", fields=FIELDS), Class(9, "B", fields=FIELDS), True, id="the same names in order"),
])
def test_only_classes_with_the_same_fields_in_order_and_at_least_the_minimum_are_twins(first, second, reported):
    files = [source(DOMAIN, classes=(first,)), source(LOGIC, classes=(second,))]
    assert bool(problems(*files)) == reported


def test_two_classes_of_one_part_are_not_twins_in_one_instance_or_two():
    assert problems(source(DOMAIN, classes=(Class(5, "A", fields=FIELDS),)),
                    source("modules/docs/domain/other.py", classes=(Class(3, "B", fields=FIELDS),)),
                    source("modules/billing/domain/values.py", classes=(Class(3, "C", fields=FIELDS),))) == []


def test_two_instances_of_a_repeating_folder_hold_twins_across_their_parts():
    assert problems(source("modules/billing/domain/values.py", classes=(Class(3, "A", fields=FIELDS),)),
                    source(CONTRACT, classes=(Class(5, "B", fields=FIELDS),))) == [
        "app/modules/docs/contract/__init__.py:5: B declares the fields of A at app/modules/billing/domain/values.py:3 "
        "in the same order (key, part, what): contract/ of modules/docs and domain/ of modules/billing hold one type "
        "written twice (no-twins)"]


def test_the_inner_part_comes_first_and_each_copy_names_an_earlier_twin_of_its_own_instance_first():
    found = problems(source(CONTRACT, classes=(Class(5, "A", fields=FIELDS),)),
                     source(DOMAIN, classes=(Class(5, "B", fields=FIELDS),)),
                     source("modules/rules/contract/__init__.py", classes=(Class(5, "C", fields=FIELDS),)),
                     source("modules/rules/domain/values.py", classes=(Class(5, "D", fields=FIELDS),)))
    assert [line.split(" in the same order")[0] for line in found] == [
        "app/modules/docs/contract/__init__.py:5: A declares the fields of B at app/modules/docs/domain/values.py:5",
        "app/modules/rules/contract/__init__.py:5: C declares the fields of D at app/modules/rules/domain/values.py:5"]


def test_a_class_whose_earlier_twins_share_its_part_is_not_reported_but_its_later_twin_in_another_part_is():
    found = problems(source(DOMAIN, classes=(Class(5, "A", fields=FIELDS),)),
                     source("modules/rules/domain/values.py", classes=(Class(5, "B", fields=FIELDS),)),
                     source("modules/billing/contract/__init__.py", classes=(Class(5, "C", fields=FIELDS),)))
    assert [line.split(" in the same order")[0] for line in found] == [
        "app/modules/billing/contract/__init__.py:5: C declares the fields of A at app/modules/docs/domain/values.py:5"]


def test_many_fields_are_shown_by_the_first_four():
    fields = ("a", "b", "c", "d", "e", "f")
    found = problems(source(DOMAIN, classes=(Class(5, "A", fields=fields),)),
                     source(CONTRACT, classes=(Class(9, "B", fields=fields),)))
    assert "in the same order (a, b, c, d and 2 more)" in found[0]


def test_a_class_in_no_part_is_not_read_and_the_check_is_off_without_the_guard():
    files = [source("scripts/seed.py", classes=(Class(5, "A", fields=FIELDS),)),
             source(DOMAIN, classes=(Class(5, "B", fields=FIELDS),))]
    assert problems(*files) == []
    assert problems(source(LOGIC, classes=(Class(5, "A", fields=FIELDS),)), files[1], checked=profile()) == []


def test_the_minimum_is_the_profile_s():
    files = [source(DOMAIN, classes=(Class(5, "A", fields=FIELDS[:2]),)),
             source(CONTRACT, classes=(Class(9, "B", fields=FIELDS[:2]),))]
    assert len(problems(*files, checked=profile(no_twins=2))) == 1
