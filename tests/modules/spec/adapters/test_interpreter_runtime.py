"""Spec's Runtime port answered by the interpreter running xarch."""
import pytest

from xarch.modules.spec.adapters.interpreter_runtime import InterpreterRuntime
from xarch.modules.spec.domain.errors import InvalidArchitecture


def test_the_standard_library_is_known_from_the_interpreter_and_the_builtins_are_its_own():
    runtime = InterpreterRuntime()
    assert {"os", "sys"} <= runtime.standard_library("interpreter")
    assert {"open", "print"} <= runtime.builtin_names()
    assert "class" in runtime.reserved_words()


def test_a_source_of_names_that_is_not_the_interpreter_is_refused():
    with pytest.raises(InvalidArchitecture) as caught:
        InterpreterRuntime().standard_library("registry")
    assert caught.value.problems == (
        "presets/language: standard: 'registry' is not a source of names xarch reads: use interpreter",)
