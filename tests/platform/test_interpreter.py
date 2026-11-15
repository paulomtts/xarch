"""What only the running interpreter knows: the standard library's top-level names and the names bound without an
import."""
import sys

from xarch.platform.interpreter import builtin_names, reserved_words, standard_library


def test_the_standard_library_is_the_top_level_names_of_the_running_interpreter():
    assert standard_library() == frozenset(sys.stdlib_module_names)
    assert {"os", "sys", "json"} <= standard_library()


def test_the_builtin_names_are_what_the_running_interpreter_binds_without_an_import():
    assert {"open", "print", "len", "ValueError"} <= builtin_names()
    assert "os" not in builtin_names()


def test_the_reserved_words_are_the_keywords_of_the_running_interpreter():
    assert {"class", "def", "import"} <= reserved_words()
    assert "print" not in reserved_words()
