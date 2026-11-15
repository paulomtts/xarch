"""Every violation xarch can report says what to do: a Violation cannot be made without a fix (see tests/kernel), and
no place in xarch's own code that makes one leaves the fix out, so a check path no test reaches cannot either."""
import ast
from pathlib import Path

import pytest

import xarch
from xarch.kernel.violations import RULES, Violation

SRC = Path(xarch.__file__).parent
FIX_POSITION = 5


def constructions(path: Path) -> list[tuple[int, bool]]:
    """Each call of Violation in the file, by its line, and whether it gives the fix: five positional arguments, or
    a keyword called fix."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return [(node.lineno, len(node.args) >= FIX_POSITION or any(k.arg == "fix" for k in node.keywords))
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Violation"]


def test_every_place_in_xarch_that_makes_a_violation_gives_it_a_fix():
    found = {f"{path.relative_to(SRC).as_posix()}:{line}": gives
             for path in sorted(SRC.rglob("*.py")) if "architectures" not in path.relative_to(SRC).parts
             for line, gives in constructions(path)}
    assert found and [place for place, gives in found.items() if not gives] == []


@pytest.mark.parametrize("text, expected", [
    pytest.param("Violation(f, 1, m, 'rules', 'do this')", [(1, True)], id="a fix given as the fifth argument"),
    pytest.param("Violation(f, 1, m, 'rules', fix='do this')", [(1, True)], id="a fix given by keyword"),
    pytest.param("Violation(f, 1, m, 'rules')", [(1, False)], id="no fix"),
    pytest.param("x = [Violation(f, 1, m, r, fix) for f in fs]", [(1, True)], id="a construction in a comprehension"),
    pytest.param("replace(Violation, 3)\nViolation.fix", [], id="a mention that is no construction"),
])
def test_constructions(tmp_path, text, expected):
    (tmp_path / "x.py").write_text(text)
    assert constructions(tmp_path / "x.py") == expected


def test_no_rule_id_can_make_a_violation_with_a_blank_fix():
    for rule in RULES:
        for fix in ("", " ", "\t\n"):
            with pytest.raises(ValueError, match="has no fix"):
                Violation("app/a.py", 1, "found", rule, fix)
