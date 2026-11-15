"""Where a conversion from format 1 goes, and which documents are no profile of format 1 to convert."""
from pathlib import Path

import pytest

from xarch.modules.spec.application.logic.migrate_output import converted_folder, converted_name, not_format_1


def test_the_converted_profile_keeps_the_old_name_as_a_yaml_file():
    assert converted_name(Path("dir/old.json")) == "old.yaml"


@pytest.mark.parametrize("out, folder", [
    pytest.param(None, Path("dir/old-v2"), id="by default beside the old file, named for it"),
    pytest.param(Path("elsewhere"), Path("elsewhere"), id="else the folder asked for"),
])
def test_converted_folder(out, folder):
    assert converted_folder(Path("dir/old.yaml"), out) == folder


@pytest.mark.parametrize("document, refusal", [
    pytest.param({"xarch": 1}, None, id="format 1 is converted"),
    pytest.param({"xarch": 2}, "old.yaml: already in format 2: nothing to migrate", id="format 2 has nothing to do"),
    pytest.param({"xarch": True}, "old.yaml: not a profile of format 1: it says `xarch: True`",
                 id="a version that only equals 1 is not format 1"),
    pytest.param({"name": "x"}, "old.yaml: not a profile of format 1: it has no `xarch`", id="no version"),
    pytest.param(["xarch"], "old.yaml: not a profile of format 1: it has no `xarch`", id="no mapping"),
])
def test_not_format_1(document, refusal):
    assert not_format_1(document, "old.yaml") == refusal
