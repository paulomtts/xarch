"""The example check on a tier's example tests: one under tests/ is only parsed, one in a part obeys its rules."""


from xarch.modules.spec.application.logic.example_imports import example_problems
from xarch.modules.spec.domain.architecture_file import parse_architecture


def layered(*tiers: dict, **parts: dict) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"api": {}, "service": {}, "store": {}}}, "shared": {}},
        "parts": {"api": {"path": "src/*/api", "role": "HTTP handlers"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "store": {"path": "src/*/store", "role": "database access"},
                  "shared": {"path": "shared", "role": "shared code",
                             "untested": "reached through the parts that use it"}} | parts,
        "rules": {},
        "tiers": list(tiers) or [unit(), integration()],
    }


def unit(**extra) -> dict:
    return {"name": "unit", "subject": ["service", "service/rules"], "proves": "a rule", "may_touch": "nothing",
            "litmus": "Does it decide?\nIf yes, it is a unit test.\n"} | extra


def integration(**extra) -> dict:
    return {"name": "integration", "subject": ["api", "store"], "proves": "a request", "may_touch": "the database",
            "litmus": "Does it need the database?"} | extra


def parsed(document: dict, has_file=lambda relative: True):
    return parse_architecture(document, "layered.yaml", has_file)


def tiered() -> dict:
    example = {"path": "tests/src/billing/service/test_rules.py", "file": "x/unit.py", "note": " (one per rule)"}
    return layered(
        unit(one_file_per="rule", cases_from="the invariants", data="built in the test", example=example),
        integration(subject_text="`src/` but `service/`", one_file_per="route", cases_from="its arguments",
                    data="the seed", example={"path": "tests/src/test_api.py", "file": "x/integration.py"}))


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
