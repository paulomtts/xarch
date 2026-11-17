"""Which loader reads a profile file: the format version it starts with decides, and any other version is refused."""
import pytest

from tests.modules.spec.profiles_v2 import PRESETS, SOURCE, layered
from xarch.modules.spec.application.logic.profile_file import parse_profile
from xarch.modules.spec.application.logic.profile_v2 import parse_v2
from xarch.modules.spec.domain.errors import InvalidArchitecture


def load(document):
    return parse_profile(document, SOURCE, (), PRESETS, ("cli",))


def problems(document) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        load(document)
    return list(caught.value.problems)


def test_format_2_is_read_by_its_own_loader():
    document = layered(based_on="cli")
    assert load(document) == parse_v2(document, SOURCE, (), PRESETS, ("cli",))
    assert load(document).based_on == "cli"


def test_a_document_that_is_no_mapping_is_refused():
    assert problems([1]) == ["layered.yaml: must be a mapping of keys, starting with `xarch: 2`"]


def test_a_missing_version_is_refused_naming_the_version_there_is():
    assert problems({"name": "x"}) == ["layered.yaml: missing format version: start the file with `xarch: 2`"]


@pytest.mark.parametrize("version", [1, 3, 0, "2", "1", True, 2.0, None])
def test_any_other_version_is_refused(version):
    assert problems({"xarch": version}) == [
        f"layered.yaml: unknown format version {version!r}: this xarch reads `xarch: 2`"]
