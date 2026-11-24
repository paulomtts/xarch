"""The test-tree rule under testing.beside, on plain values: which test files below the tests root lie outside every
folder whose tests stay there."""
from tests.modules.layout.builders import PYTHON_NAMING
from xarch.modules.layout.application.logic.beside import stray
from xarch.modules.layout.domain.structure import Beside

BESIDE = Beside(("test_*.py", "*_test.py"), (("architecture",), ("fakes",)))
MESSAGE = "lies below the tests folder, but testing.beside keeps the tests of a part beside its code"
FIX = "move it beside the code it tests"


def reported(*paths: str) -> list[tuple[str, int, str, str, str]]:
    return [(f"tests/{path}", 0, MESSAGE, "test-tree", FIX) for path in paths]


def found(*paths: str) -> list[tuple[str, int, str, str, str]]:
    files = [tuple(path.split("/")) for path in paths]
    return [(v.file, v.line, v.message, v.rule, v.fix) for v in stray("tests", files, BESIDE, PYTHON_NAMING)]


def test_a_test_left_in_the_mirrored_tree_is_reported():
    assert found("modules/docs/application/test_publish.py") == reported("modules/docs/application/test_publish.py")


def test_tests_in_a_tier_s_folder_or_below_the_fakes_stay_where_they_are():
    assert found("architecture/test_rules.py", "architecture/rules/test_layers.py", "fakes/test_repo.py") == []


def test_a_file_that_is_no_test_is_not_reported():
    assert found("conftest.py", "modules/docs/builders.py", "modules/__init__.py") == []


def test_a_file_in_a_folder_private_in_the_language_is_never_read():
    assert found("modules/docs/__pycache__/test_publish.py", "_private/x/test_y.py") == []


def test_the_findings_are_sorted_by_path_and_every_pattern_names_a_test():
    assert found("web/test_docs.py", "kernel/ids_test.py", "test_top.py") == reported(
        "kernel/ids_test.py", "test_top.py", "web/test_docs.py")


def test_the_text_form_is_one_sentence():
    [violation] = stray("tests", [("modules", "test_x.py")], BESIDE, PYTHON_NAMING)
    assert f"{violation}: {violation.fix}" == f"tests/modules/test_x.py: {MESSAGE}: {FIX}"
