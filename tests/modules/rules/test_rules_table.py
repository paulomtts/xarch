"""The table-driven allowed() answers exactly as the hard-coded one it replaced, for every pair of places."""
import itertools

import pytest

from xarch.modules.rules.domain.places import Place, allowed


def old_allowed(src: Place, dst: Place) -> bool:
    """The oracle: allowed() as hard-coded before the rules became a table (commit cf01683)."""
    if src.part == "bootstrap":
        return True
    if dst.part == "structure":
        return False
    if dst.part == "kernel":
        return src.part != "structure"
    same = src.module is not None and src.module == dst.module
    match src.part:
        case "platform":
            return dst.part == "platform"
        case "entry":
            return dst.part == "entry" or (dst.part in ("controller", "contract") and dst.module is not None)
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
    + [Place("entry", None, sub, folder) for folder in ("cli", "web") for sub in ((), ("commands",))]
    + [Place(part, module, sub) for part in MODULE_PARTS for module in ("a", "b") for sub in SUBS]
)
PAIRS = list(itertools.product(GRID, GRID))


def test_the_grid_covers_every_part():
    assert {p.part for p in GRID} == {"structure", "kernel", "platform", "entry", "bootstrap", *MODULE_PARTS}


@pytest.mark.parametrize("src", GRID, ids=repr)
def test_allowed_matches_the_hard_coded_rules(src):
    mismatches = [f"{src} -> {dst}: table says {allowed(src, dst)}, old code said {old_allowed(src, dst)}"
                  for dst in GRID if allowed(src, dst) != old_allowed(src, dst)]
    assert mismatches == [], "\n".join(mismatches)


def test_the_grid_exercises_both_answers():
    answers = {old_allowed(src, dst) for src, dst in PAIRS}
    assert answers == {True, False}
