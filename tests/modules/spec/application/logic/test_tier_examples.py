"""The example check on a tier's example tests: one under tests/ is only parsed, one in a part obeys its rules."""
from tests.modules.spec.builders import parsed, tiered
from xarch.modules.spec.application.logic.example_imports import example_problems


def test_a_tier_example_under_tests_is_only_parsed_and_one_in_a_part_obeys_its_rules():
    """A tier example whose path lies in a part (here service) obeys that part's rules."""
    document = tiered()
    document["rules"] = {"service": ["service@own"]}
    document["tiers"][1]["example"]["path"] = "src/billing/service/test_api.py"
    architecture = parsed(document)
    texts = {"unit": "from app.src.tax.store import anything\n", "integration": "from app.src.tax.store import x\n"}
    assert example_problems(architecture, {}, texts) == [
        "tier integration's example (src/billing/service/test_api.py): imports app.src.tax.store which service may "
        "not import (rules.service)"]
    assert example_problems(architecture, {}, {"unit": "def f(:\n"}) == [
        "tier unit's example (tests/src/billing/service/test_rules.py): is not valid Python: invalid syntax (line 1)"]
