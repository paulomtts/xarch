"""How the language the tests' sources are written in names a folder, as the bundled preset says it: the layout's
tests share it."""
from __future__ import annotations

from importlib import resources

import yaml

from xarch.modules.layout.domain.structure import Naming

_PYTHON = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))
PYTHON_NAMING = Naming(_PYTHON["name"], _PYTHON["private"])
"""How Python names a folder, read from its data file."""
