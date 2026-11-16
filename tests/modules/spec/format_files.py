"""The data files of the profile format, as xarch ships them, and the texts they read into: the builders of the tests
share them."""
from __future__ import annotations

from importlib import resources

import yaml

from xarch.modules.spec.application.logic.key_catalogue import catalogue_of

KEYS_DOCUMENT = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "format", "keys.yaml")
                               .read_text(encoding="utf-8"))
CATALOGUE = catalogue_of(KEYS_DOCUMENT)
