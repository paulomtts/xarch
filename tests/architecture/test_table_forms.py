"""The scenario-coverage checks word a row from the slots of its form and the language's templates, never from the
kind of form: their module holds no string literal that names a holder of a table form."""
import ast
from pathlib import Path

SCENARIOS = Path(__file__).resolve().parents[2] / "xarch" / "modules" / "rules" / "application" / "logic" / "scenarios.py"
HOLDERS = {"decorator", "call", "loop"}


def test_the_checks_of_scenario_coverage_name_no_kind_of_table_form():
    tree = ast.parse(SCENARIOS.read_text(encoding="utf-8"))
    literals = {node.value for node in ast.walk(tree) if isinstance(node, ast.Constant) and isinstance(node.value, str)}
    assert literals & HOLDERS == set()
