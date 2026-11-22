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

PYTHON_DOCUMENT = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                                 .read_text(encoding="utf-8"))
RUNTIME = FakeRuntime(frozenset(sys.stdlib_module_names), frozenset(dir(builtins)), frozenset(keyword.kwlist))
PYTHON = replace(language_of("python", PYTHON_DOCUMENT), standard_names=RUNTIME.standard_library("interpreter"),
                 builtin_names=RUNTIME.builtin_names("interpreter"),
                 reserved_names=RUNTIME.reserved_words("interpreter"))

TEST_LANGUAGES = Path(__file__).resolve().parents[2] / "fakes" / "languages"
BRACE = replace(language_of("brace", yaml.safe_load((TEST_LANGUAGES / "brace.yaml").read_text(encoding="utf-8"))),
                builtin_names=frozenset({"fetch"}))
"""The TypeScript-like test-only language; `fetch` is its one builtin, for the hint a bare builtin is given."""
PERCENT = language_of("percent", yaml.safe_load((TEST_LANGUAGES / "percent.yaml").read_text(encoding="utf-8")))
"""The ObjectScript-like test-only language."""
