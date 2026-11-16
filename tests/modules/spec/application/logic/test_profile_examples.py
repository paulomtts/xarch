"""The examples a profile names, on hand-made listings: every file below a folder of `docs.examples`, by its path in its
project, with its note; a tier's example by that path; and the part each illustrates."""
from tests.modules.spec.languages import PYTHON
from xarch.modules.spec.application.logic.profile_examples import example_files, example_of, examples_of
from xarch.modules.spec.domain.values import Example, Part, TierExample

FILES = ("ex/core/rules.py", "ex/core/__pycache__/rules.cpython-313.pyc", "ex/tests/core/test_rules.py")
DOCS = {"examples": ["ex"], "example_notes": {"core/rules.py": "the rule itself"}}


def test_every_file_below_an_example_folder_is_an_example_by_its_path_in_its_project_but_what_was_compiled():
    problems: list[str] = []
    found = example_files(DOCS, FILES, problems, PYTHON)
    assert (found.files, found.notes, problems) == (
        {"core/rules.py": "ex/core/rules.py", "tests/core/test_rules.py": "ex/tests/core/test_rules.py"},
        {"core/rules.py": "the rule itself"}, [])


def test_a_tier_names_its_example_by_its_path_in_the_project_and_one_that_is_none_is_refused():
    problems: list[str] = []
    found = example_files(DOCS, FILES, problems, PYTHON)
    assert example_of("core/rules.py", found, "tiers.unit.example", problems, PYTHON) == TierExample(
        ("core", "rules.py"), "ex/core/rules.py", "the rule itself")
    assert example_of("core/gone.py", found, "tiers.unit.example", problems, PYTHON) is None
    assert problems == ["tiers.unit.example: no file 'core/gone.py' in any folder of docs.examples"]


def test_an_example_illustrates_the_part_its_path_lies_in_and_test_code_none():
    found = example_files(DOCS, FILES, [], PYTHON)
    examples = examples_of(found, {"core": {}}, {"core": Part("core", ("core",), "the rules")}, PYTHON)
    assert examples == {
        "core/rules.py": Example("core/rules.py", "core", ("core", "rules.py"), "ex/core/rules.py", "the rule itself"),
        "tests/core/test_rules.py": Example("tests/core/test_rules.py", "", ("tests", "core", "test_rules.py"),
                                            "ex/tests/core/test_rules.py", "")}
