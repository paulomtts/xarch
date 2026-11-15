"""How a custom profile is looser than a bundled one, on hand-made architectures: a rule's target is shown as the file
writes it."""
from dataclasses import replace

import pytest

from tests.modules.spec.profiles_v2 import layered, parsed
from xarch.modules.spec.application.logic.looseness import closest, looser


@pytest.mark.parametrize("target, shown", [
    pytest.param("service", "service", id="a part in the repeating folder is shown by its bare name, which means its own instance"),
    pytest.param("store@any/sql", "store@any/sql", id="a scope and a sub path are both shown"),
    pytest.param("shared/text", "shared/text", id="a part outside the repeating folder has no scope"),
    pytest.param("everything", "everything", id="everything is shown as the word"),
    pytest.param("api@any", "api@any", id="another instance of the part itself is looser than its own, which is implied"),
])
def test_a_target_added_to_a_rule_is_shown_as_written(target, shown):
    custom = layered()
    custom["parts"]["api"]["may_import"] = target if target == "everything" else [target]
    stricter = layered()
    stricter["parts"]["api"]["may_import"] = []
    assert looser(parsed(custom), parsed(stricter)) == [("may_import", "api", shown)]


def test_the_bundled_profile_a_profile_says_it_is_based_on_wins_over_the_one_sharing_most_parts():
    full = parsed(layered())
    bundled = {"alpha": full, "beta": replace(full, parts={"api": full.parts["api"]})}
    mine = replace(full, parts={name: full.parts[name] for name in ("api", "store")})
    assert closest(mine, bundled) == "alpha"
    assert closest(replace(mine, based_on="beta"), bundled) == "beta"
