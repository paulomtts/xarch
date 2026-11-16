"""Whether a key is one the engine expands to rules when a profile sets it, for a key a profile sets nowhere."""
import pytest

from xarch.modules.rules.application.logic.expandable import expands


@pytest.mark.parametrize("address, expected", [
    pytest.param("parts.types_only", True, id="a key of every part the engine expands"),
    pytest.param("parts.services.types_only", True, id="the same key of one part"),
    pytest.param("tiers.unit.types_only", True, id="a key of a tier"),
    pytest.param("guards.no-comments", True, id="a guard the engine runs"),
    pytest.param("guards.no-twins", False, id="a guard a check of xarch's own runs"),
    pytest.param("parts.path", False, id="a key of the layout"),
    pytest.param("docs", False, id="a key of the docs"),
])
def test_a_key_is_expandable_when_the_engine_expands_it_once_set(address, expected):
    assert expands(address) is expected
