"""The data file of the language the tests' sources are written in, as the bundled preset says it, and the language it
reads into: the builders of every module's tests share it."""
from __future__ import annotations

import builtins
import keyword
import sys
from dataclasses import replace
from importlib import resources

import yaml

from tests.fakes.runtime import FakeRuntime
from xarch.modules.spec.application.logic.language_file import language_of

PYTHON_DOCUMENT = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                                 .read_text(encoding="utf-8"))
RUNTIME = FakeRuntime(frozenset(sys.stdlib_module_names), frozenset(dir(builtins)), frozenset(keyword.kwlist))
PYTHON = replace(language_of("python", PYTHON_DOCUMENT), standard_names=RUNTIME.standard_library("interpreter"),
                 builtin_names=RUNTIME.builtin_names("interpreter"),
                 reserved_names=RUNTIME.reserved_words("interpreter"))
