"""How a custom profile is looser than a bundled one, on hand-made architectures: a rule's target is shown as the file
writes it."""
import pytest

from tests.modules.spec.builders import layered_tiers, parsed
from xarch.modules.spec.application.logic.looseness import looser


@pytest.mark.parametrize("target, shown", [
    pytest.param("service@own", "service@own", id="a part in the each folder keeps its scope"),
    pytest.param("store@any/sql", "store@any/sql", id="a scope and a sub path are both shown"),
    pytest.param("shared/text", "shared/text", id="a part outside the each folder has no scope"),
    pytest.param("*", "*", id="everything is shown as a star"),
    pytest.param("api@any", "api@any", id="another instance of the part itself is looser than its own, which is implied"),
])
def test_a_target_added_to_a_rule_is_shown_as_written(target, shown):
    custom = layered_tiers() | {"rules": {"api": [target]}}
    assert looser(parsed(custom), parsed(layered_tiers())) == [("rules", "api", shown)]
