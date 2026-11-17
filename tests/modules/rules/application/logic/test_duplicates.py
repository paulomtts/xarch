"""The no-duplicates check on hand-made source files: two functions of the app with the same shape and at least the
profile's number of statements, the later one reported against the first."""
from tests.modules.rules.builders import profile, source
from xarch.modules.rules.application.logic.duplicates import violations
from xarch.modules.rules.domain.parsed import Function

ON = profile(no_duplicates=4)


def fn(line: int, name: str, shape: str = "s1", statements: int = 4, owner: str = "") -> Function:
    return Function(line, name, owner=owner, statements=statements, shape=shape if statements else "")


def problems(*files, checked=ON) -> list[str]:
    return [str(v) for v in violations(list(files), checked)]


def test_two_functions_with_one_shape_are_reported_at_the_later_one_naming_the_first():
    one = source("kernel/a.py", functions=(fn(3, "slug"),))
    two = source("modules/docs/domain/b.py", functions=(fn(9, "to_slug"),))
    assert problems(one, two) == ["app/modules/docs/domain/b.py:9: to_slug has the same code as slug at "
                                  "app/kernel/a.py:3, whatever the names (no-duplicates)"]


def test_the_fix_says_to_keep_one_and_where_else_to_put_it():
    [found] = violations([source("kernel/a.py", functions=(fn(3, "a"), fn(8, "b")))], ON)
    assert (found.rule, found.line) == ("no-duplicates", 8)
    assert found.fix == ("keep one of the two and import it where the other is, or move it to a part both may import "
                         "when they cannot import each other")


def test_a_method_is_named_with_its_class_and_two_in_one_file_are_found():
    both = source("kernel/a.py", functions=(fn(3, "load", owner="A"), fn(9, "load", owner="B")))
    assert problems(both) == ["app/kernel/a.py:9: B.load has the same code as A.load at app/kernel/a.py:3, whatever "
                              "the names (no-duplicates)"]


def test_three_copies_are_each_reported_against_the_first_in_order_of_file_and_line():
    files = [source("kernel/c.py", functions=(fn(1, "c"),)), source("kernel/a.py", functions=(fn(1, "a"),)),
             source("kernel/b.py", functions=(fn(1, "b"),))]
    assert problems(*files) == [
        "app/kernel/b.py:1: b has the same code as a at app/kernel/a.py:1, whatever the names (no-duplicates)",
        "app/kernel/c.py:1: c has the same code as a at app/kernel/a.py:1, whatever the names (no-duplicates)"]


def test_functions_of_another_shape_or_below_the_minimum_are_not_duplicates():
    files = [source("kernel/a.py", functions=(fn(1, "a"), fn(5, "b", shape="s2"), fn(9, "c", statements=3),
                                              fn(12, "d", statements=3)))]
    assert problems(*files) == []


def test_the_minimum_is_the_profiles_and_a_function_with_no_statement_never_counts():
    files = [source("kernel/a.py", functions=(fn(1, "a", statements=2), fn(5, "b", statements=2),
                                              fn(9, "c", statements=0), fn(12, "d", statements=0)))]
    assert problems(*files, checked=profile(no_duplicates=2)) == [
        "app/kernel/a.py:5: b has the same code as a at app/kernel/a.py:1, whatever the names (no-duplicates)"]
    assert problems(*files, checked=profile(no_duplicates=1)) == problems(*files, checked=profile(no_duplicates=2))


def test_it_is_off_when_the_profile_does_not_switch_it_on():
    assert problems(source("kernel/a.py", functions=(fn(1, "a"), fn(5, "b"))), checked=profile()) == []
