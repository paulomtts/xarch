"""How the language the tests' sources are written in names a folder, as the bundled preset says it: the layout's
tests share it."""
from __future__ import annotations

from importlib import resources

import yaml

from xarch.modules.layout.domain.structure import Allowed, Beside, Counterpart, Naming, Pattern, Word

_PYTHON = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))
PYTHON_NAMING = Naming(_PYTHON["name"], _PYTHON["private"])
"""How Python names a folder, read from its data file."""
BESIDE = Beside(("test_*.py",), (("architecture",), ("fakes",)))
"""Where the tests sit when every test of a part sits beside its code, and each tier's folder and the fakes stay below
the tests root."""
CONFORMANCE = Counterpart("fakes-have-conformance", Pattern(("adapters", "sql", "<store>"), False, True),
                          Pattern(("conformance", "<store>"), True, True), (Pattern(("fakes", "<store>"), True, True),),
                          (Allowed(("adapters", "sql", "old"), False, "adapters/sql/old/", "retired soon"),))
"""A counterpart: each store below adapters/sql/ with fakes below tests/fakes/ has a contract below
tests/conformance/, but adapters/sql/old/, accepted with none."""
STORE = Word("store", ("adapters", "sql"), frozenset({"models"}))
"""The repeating folder adapters/sql/<store>/, with the folder models/ the layout names beside its instances."""
