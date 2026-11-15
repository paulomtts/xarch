"""The example check on a tier's example tests: one under tests/ is only parsed, one in a part obeys its rules."""
from tests.modules.spec.profiles_v2 import covered, parsed
from xarch.modules.spec.application.logic.example_imports import example_problems

UNIT = "tests/src/billing/service/test_rules.py"
INTEGRATION = "src/billing/service/test_api.py"


def test_a_tier_example_under_tests_is_only_parsed_and_one_in_a_part_obeys_its_rules():
    document = covered(docs={"examples": ["ex"]})
    document["parts"]["service"]["may_import"] = []
    document["tiers"]["unit"]["docs"] = {"example": UNIT}
    document["tiers"]["integration"]["docs"] = {"example": INTEGRATION}
    architecture = parsed(document, folder_files={"ex": (UNIT, INTEGRATION)}.get)
    texts = {UNIT: "from app.src.tax.store import anything\n", INTEGRATION: "from app.src.tax.store import x\n"}
    assert example_problems(architecture, texts) == [
        "example (src/billing/service/test_api.py): imports app.src.tax.store which service may not import "
        "(parts.service.may_import)"]
    assert example_problems(architecture, {**texts, UNIT: "def f(:\n"}) == [
        "example (tests/src/billing/service/test_rules.py): is not valid Python: invalid syntax (line 1)",
        "example (src/billing/service/test_api.py): imports app.src.tax.store which service may not import "
        "(parts.service.may_import)"]
