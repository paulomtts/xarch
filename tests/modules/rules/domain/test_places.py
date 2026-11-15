"""The profile-driven allowed() answers exactly as the hard-coded one it replaced, for every pair of places, under the
bundled cli and web architecture files: moving the rules into the files did not change what they mean."""
import itertools

import pytest

from xarch.bootstrap.wiring import build_spec
from xarch.kernel.logic.placement import Place
from xarch.modules.rules.adapters.spec_profile import SpecProfiles
from xarch.modules.rules.domain.places import allowed


def old_allowed(src: Place, dst: Place) -> bool:
    """The oracle: allowed() as hard-coded before the rules became a table (commit cf01683), in its own names:
    "structure" for the package files no part claims, "entry" for the entry point."""
    if src.part == "bootstrap":
        return True
    if dst.part == "structure":
        return False
    if dst.part == "kernel":
        return src.part != "structure"
    same = src.instance is not None and src.instance == dst.instance
    match src.part:
        case "platform":
            return dst.part == "platform"
        case "entry":
            return dst.part == "entry" or (dst.part in ("controller", "contract") and dst.instance is not None)
        case "domain":
            return same and dst.part == "domain"
        case "contract":
            return same and (dst.part == "contract" or (dst.part == "domain" and dst.sub[:1] == ("values",)))
        case "controller":
            return same and dst.part in ("controller", "services", "logic", "ports", "domain", "contract")
        case "services":
            return same and dst.part in ("services", "logic", "ports", "domain", "contract")
        case "logic":
            return same and dst.part in ("logic", "domain")
        case "ports":
            return same and dst.part in ("ports", "domain")
        case "adapters":
            if dst.part == "platform":
                return True
            if dst.part == "contract":
                return True
            return same and dst.part in ("adapters", "ports", "domain")
    return False


MODULE_PARTS = ("contract", "domain", "controller", "services", "ports", "logic", "adapters")
SUBS = ((), ("values",), ("other",), ("values", "ids"), ("valuesx",))

GRID = (
    [Place("structure")]
    + [Place(part, None, sub) for part in ("kernel", "platform", "bootstrap") for sub in ((), ("logic",), ("x",))]
    + [Place("entry", None, sub) for sub in ((), ("commands",))]
    + [Place(part, instance, sub) for part in MODULE_PARTS for instance in ("a", "b") for sub in SUBS]
)
PAIRS = list(itertools.product(GRID, GRID))


def test_the_grid_covers_every_part():
    assert {p.part for p in GRID} == {"structure", "kernel", "platform", "entry", "bootstrap", *MODULE_PARTS}


def as_profile(place: Place, entry: str) -> Place:
    """The place in the profile's names: the entry point is its part, the structure is no part."""
    names = {"structure": None, "entry": entry}
    return Place(names.get(place.part, place.part), place.instance, place.sub)


@pytest.mark.parametrize("profile", ["cli", "web"])
@pytest.mark.parametrize("src", GRID, ids=repr)
def test_allowed_matches_the_hard_coded_rules(profile, src):
    rules = SpecProfiles(build_spec()).profile(profile)

    def now(a: Place, b: Place) -> bool:
        return allowed(rules, as_profile(a, profile), as_profile(b, profile))

    mismatches = [f"{src} -> {dst}: profile says {now(src, dst)}, old code said {old_allowed(src, dst)}"
                  for dst in GRID if now(src, dst) != old_allowed(src, dst)]
    assert mismatches == [], "\n".join(mismatches)


def test_the_grid_exercises_both_answers():
    answers = {old_allowed(src, dst) for src, dst in PAIRS}
    assert answers == {True, False}
