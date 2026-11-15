"""The data file of the language the tests' sources are written in, as the bundled preset says it, and the language it
reads into: the builders of every module's tests share it."""
from __future__ import annotations

import builtins
import keyword
import sys
from dataclasses import replace

from tests.fakes.runtime import FakeRuntime
from xarch.modules.spec.application.logic.language_file import language_of

PYTHON_DOCUMENT = {"title": "Python", "extension": ".py", "package_file": "__init__.py",
                   "interface": ["typing.Protocol", "typing_extensions.Protocol"],
                   "dynamic": ["importlib.import_module", "importlib.__import__", "builtins.__import__"],
                   "namespace": "builtins", "cache": "__pycache__", "standard": "interpreter"}
RUNTIME = FakeRuntime(frozenset(sys.stdlib_module_names), frozenset(dir(builtins)), frozenset(keyword.kwlist))
PYTHON = replace(language_of("python", PYTHON_DOCUMENT), standard_names=RUNTIME.standard_library("interpreter"),
                 builtin_names=RUNTIME.builtin_names(), reserved_names=RUNTIME.reserved_words())
