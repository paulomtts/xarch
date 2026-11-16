"""How the language the tests' sources are written in names a folder, as the bundled preset says it: the scaffold's
tests share it."""
from __future__ import annotations

from importlib import resources

import yaml

_PYTHON = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                         .read_text(encoding="utf-8"))
PYTHON_NAMES, PYTHON_PRIVATE = _PYTHON["name"], _PYTHON["private"]
"""What a name of Python may be, and how a private one starts, read from its data file."""
