"""The data files of the profile format, as xarch ships them, and the texts they read into: the builders of the tests
share them."""
from __future__ import annotations

from importlib import resources

import yaml

from xarch.modules.spec.application.logic.file_types import file_types_of
from xarch.modules.spec.application.logic.key_catalogue import catalogue_of

FORMAT = resources.files("xarch").joinpath("architectures", "presets", "format")
KEYS_DOCUMENT = yaml.safe_load(FORMAT.joinpath("keys.yaml").read_text(encoding="utf-8"))
CATALOGUE = catalogue_of(KEYS_DOCUMENT)
FILE_TYPES_DOCUMENT = yaml.safe_load(FORMAT.joinpath("file_types.yaml").read_text(encoding="utf-8"))
FILE_TYPES = file_types_of(FILE_TYPES_DOCUMENT)
