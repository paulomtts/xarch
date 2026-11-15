"""Where code sits in a hand-made profile, how a place is named, and whether an import between two places is allowed."""
import pytest

from tests.modules.rules.builders import PROFILE, profile, steps
from xarch.kernel.logic.placement import Place, Target
from xarch.modules.rules.domain.places import allowed, label, place


@pytest.mark.parametrize("path, expected", [
    pytest.param("modules/docs/domain/doc", Place("domain", "docs", ("doc",)), id="a file in a part"),
    pytest.param("modules/docs/application/controller", Place("controller", "docs"), id="a part that is a file"),
    pytest.param("kernel", Place("kernel"), id="a part's own package"),
    pytest.param("modules/docs", Place(None), id="a folder of the layout no part claims is the structure"),
    pytest.param("modules/docs/application", Place(None), id="a deeper one too"),
    pytest.param("", Place(None), id="the app's own package is the structure"),
    pytest.param("modules/docs/helpers", None, id="a file in no part and no folder of the layout is ungoverned"),
    pytest.param("scripts/seed", None, id="as is a folder the layout does not hold"),
])
def test_place(path, expected):
    assert place(PROFILE, steps(path) if path else ()) == expected


@pytest.mark.parametrize("where, expected", [
    pytest.param(Place("domain", "docs", ("doc",)), "domain/ of modules/docs", id="a part of an instance"),
    pytest.param(Place("kernel", None, ("ids",)), "kernel/", id="a part outside the instances"),
    pytest.param(Place("kernel", "docs"), "kernel/", id="an instance on a part outside them is not shown"),
    pytest.param(Place("domain"), "domain/", id="an instance's part seen from no instance"),
    pytest.param(Place(None), "structure/", id="the structure"),
])
def test_label(where, expected):
    assert label(PROFILE, where) == expected


def test_the_apps_own_package_is_the_structure_even_when_the_layout_lists_no_root():
    assert place(profile(folders=()), ()) == Place(None)


def test_an_instance_below_a_deeper_each_root_is_named_by_its_full_folder():
    deeper = profile(parts={"api": ("src", "apps", "*", "api")})
    assert label(deeper, Place("api", "shop")) == "api/ of src/apps/shop"


@pytest.mark.parametrize("src, dst, expected", [
    pytest.param(Place("domain", "a"), Place("domain", "a", ("x",)), True, id="@own reaches the importer's instance"),
    pytest.param(Place("domain", "a"), Place("domain", "b"), False, id="@own does not reach another instance"),
    pytest.param(Place("domain", "a"), Place("kernel"), True, id="a bare part outside the instances"),
    pytest.param(Place("adapters", "a"), Place("contract", "b"), True, id="@any reaches every instance"),
    pytest.param(Place("contract", "a"), Place("domain", "a", ("values", "ids")), True,
                 id="a target's sub-path reaches what lies below it"),
    pytest.param(Place("contract", "a"), Place("domain", "a", ("valuesx",)), False,
                 id="a sub-path is matched by whole names"),
    pytest.param(Place("contract", "a"), Place("domain", "a"), False, id="nor does it reach the part itself"),
    pytest.param(Place("bootstrap"), Place("modules", "a"), True, id="everything reaches every place"),
    pytest.param(Place("bootstrap"), Place(None), True, id="even the structure"),
    pytest.param(Place("kernel"), Place(None), False, id="no other part may import the structure"),
    pytest.param(Place(None), Place("kernel"), False, id="the structure imports nothing"),
    pytest.param(Place("scripts"), Place("kernel"), False, id="a part with no rules imports nothing"),
])
def test_allowed(src, dst, expected):
    assert allowed(PROFILE, src, dst) == expected


def test_a_rule_lists_what_its_part_may_import():
    assert allowed(profile(rules={"kernel": (Target("platform"),)}), Place("kernel"), Place("kernel")) is False
