"""A violation always says what to do: its fix is required, and its rule is one of the known ids."""
import pytest

from xarch.kernel.violations import RULES, Violation


def test_a_violation_prints_where_it_is_and_what_was_found_and_leaves_the_fix_to_the_report():
    assert [str(Violation("app/a.py", 3, "a problem", "rules", "do this"),),
            str(Violation("app/a.py", 0, "a problem", "rules", "do this"))] == [
        "app/a.py:3: a problem", "app/a.py: a problem"]


@pytest.mark.parametrize("fix", [
    pytest.param("", id="an empty fix"),
    pytest.param("   ", id="a blank fix"),
    pytest.param("\n", id="a fix that is a line break"),
])
def test_a_violation_without_a_fix_cannot_be_made(fix):
    with pytest.raises(ValueError, match="has no fix") as caught:
        Violation("app/a.py", 3, "a problem", "rules", fix)
    assert str(caught.value) == "a violation of rule 'rules' at app/a.py:3 has no fix: say what to do about it"


def test_a_violation_cannot_be_made_without_giving_a_fix_at_all():
    with pytest.raises(TypeError):
        Violation("app/a.py", 3, "a problem", "rules")


def test_a_violation_of_an_unknown_rule_cannot_be_made():
    with pytest.raises(ValueError, match="unknown rule") as caught:
        Violation("app/a.py", 3, "a problem", "made-up", "do this")
    assert str(caught.value) == "a violation names an unknown rule 'made-up': use one of " + ", ".join(sorted(RULES))


def test_the_rule_ids_are_the_stable_ids_of_every_check():
    assert sorted(RULES) == ["built-by", "closed-tree", "cycles", "dead-code", "forbidden", "holds", "libraries",
                             "must-import", "names", "no-callbacks", "no-comments", "no-duplicates", "no-twins", "package-only",
                             "pass-through", "private-imports", "rules", "scenario-coverage", "shared", "stand-ins",
                             "structure", "syntax", "test-tree", "tiers", "types-only"]
