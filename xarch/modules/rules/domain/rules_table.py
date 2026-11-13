"""Who may import whom, as data: one row per part, listing the targets that part may import (section 5).

A target names a part, a scope and an optional path below the part:
- scope "own": the part in the importer's own module;
- scope "any": the part in any module;
- scope "none": a part that is not in a module (kernel, platform, the entry point).
- sub: when set, only that path below the part, e.g. ("values",) for domain/values.

A part with no target may import nothing; a part missing from the table may import nothing. The part "*"
matches every place, structure included, and is how bootstrap may import everything. No other row lists
"structure": the package files that only hold the tree together are never a valid target.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Scope = Literal["own", "any", "none"]


@dataclass(frozen=True)
class Target:
    part: str                      # the imported part, or "*" for every place
    scope: Scope = "none"
    sub: tuple[str, ...] = ()      # only this path below the part, if set


EVERYTHING = "*"
KERNEL = Target("kernel")

RULES: dict[str, tuple[Target, ...]] = {
    "structure": (),
    "kernel": (KERNEL,),
    "platform": (Target("platform"), KERNEL),
    "entry": (Target("entry"), Target("controller", "any"), Target("contract", "any"), KERNEL),
    "bootstrap": (Target(EVERYTHING),),
    "domain": (Target("domain", "own"), KERNEL),
    "contract": (Target("contract", "own"), Target("domain", "own", ("values",)), KERNEL),
    "controller": (Target("controller", "own"), Target("services", "own"), Target("logic", "own"),
                   Target("ports", "own"), Target("domain", "own"), Target("contract", "own"), KERNEL),
    "services": (Target("services", "own"), Target("logic", "own"), Target("ports", "own"),
                 Target("domain", "own"), Target("contract", "own"), KERNEL),
    "logic": (Target("logic", "own"), Target("domain", "own"), KERNEL),
    "ports": (Target("ports", "own"), Target("domain", "own"), KERNEL),
    "adapters": (Target("platform"), Target("contract", "any"),   # any module's: its own, or the provider's
                 Target("adapters", "own"), Target("ports", "own"),  # whose controller it wraps (section 6)
                 Target("domain", "own"), KERNEL),
}
