"""The data file of the language the tests' sources are written in, as the bundled preset says it, and the language it
reads into; and the two test-only languages of tests/fakes/languages/, which no profile names: the builders of every
module's tests share them."""
from __future__ import annotations

import builtins
import keyword
import sys
from dataclasses import replace
from importlib import resources
from pathlib import Path

import yaml

from tests.fakes.runtime import FakeRuntime
from xarch.modules.spec.application.logic.language_file import language_of
from xarch.modules.spec.domain.values import Language


def named(language: Language, standard: frozenset[str], bound: frozenset[str], reserved: frozenset[str]) -> Language:
    """The language with the names of its standard library, the names it binds without an import and its reserved
    words, the standard modules the reader is handed being its standard names, as spec's service fills them."""
    return replace(language, checked=replace(language.checked, standard_modules=standard), standard_names=standard,
                   builtin_names=bound, reserved_names=reserved)


PYTHON_DOCUMENT = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                                 .read_text(encoding="utf-8"))
RUNTIME = FakeRuntime(frozenset(sys.stdlib_module_names), frozenset(dir(builtins)), frozenset(keyword.kwlist))
PYTHON = named(language_of("python", PYTHON_DOCUMENT), RUNTIME.standard_library("interpreter"),
               RUNTIME.builtin_names("interpreter"), RUNTIME.reserved_words("interpreter"))

TEST_LANGUAGES = Path(__file__).resolve().parents[2] / "fakes" / "languages"
BRACE_DOCUMENT = yaml.safe_load((TEST_LANGUAGES / "brace.yaml").read_text(encoding="utf-8"))
BRACE = named(language_of("brace", BRACE_DOCUMENT),
              *(frozenset(BRACE_DOCUMENT["standard"][key]) for key in ("modules", "builtins", "reserved")))
"""The TypeScript-like test-only language, the lists its data file gives filled in as spec's service fills them."""
PERCENT = language_of("percent", yaml.safe_load((TEST_LANGUAGES / "percent.yaml").read_text(encoding="utf-8")))
"""The ObjectScript-like test-only language."""
