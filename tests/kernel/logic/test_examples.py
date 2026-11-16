"""Which file of an example project is test code: one whose path starts with the folder of the tests."""
from xarch.kernel.logic.examples import is_test_example


def test_a_file_whose_path_starts_with_the_tests_folder_is_test_code_and_any_other_is_the_app_s():
    assert is_test_example(("tests", "docs", "test_x.py"), "tests")
    assert not is_test_example(("docs", "tests", "x.py"), "tests")
    assert not is_test_example((), "tests")
