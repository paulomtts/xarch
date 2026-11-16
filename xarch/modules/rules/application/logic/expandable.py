"""Whether a key of the profile is one the engine expands to rules when a profile sets it: the keys the rules of a
profile that sets every such key, on a part, on a tier and as a guard, are keyed by (see explained.keyed). A key
that expands to no rule in a profile is either one that profile sets nowhere, when the engine expands it, or one a
check of xarch's own reads."""
from __future__ import annotations

from xarch.kernel.logic.placement import Target
from xarch.kernel.logic.testing import Fakes, Framework, TierView
from xarch.modules.rules.application.logic.expansion import book
from xarch.modules.rules.application.logic.explained import general, keyed
from xarch.modules.rules.domain.values import PartInfo, Profile

_SET = Profile(
    parts={"one": ("one",), "two": ("two",)}, rules={"one": (Target("two"),), "two": ()},
    libraries={"one": ("outside",)}, forbidden={"one": (("outside",),)},
    tiers=(TierView("tier", (Target("one"),), ("tier",), types_only=("two",), forbidden=True,
                    may_import=(Target("two"),), must_import=("two",)),),
    package_only=("two",), types_only={"one": ("two",)}, no_callbacks=("one",), names={"one": ("*",)},
    built_by={"two": ("one",)}, private_imports=True, no_comments=True, closed_tree=True, holds={"one": "classes"},
    must_import={"one": (Target("two"),)}, dead_code=True, untested=True, pass_through=("one",),
    fakes=Fakes(("fakes",), ("two",)), framework=Framework(("*",), "*"), info={"one": PartInfo(), "two": PartInfo()})
"""A profile of two parts and a tier that sets every key the engine expands."""


def expands(address: str) -> bool:
    """Whether the engine expands the key at address to rules when a profile sets it (on any part or tier, for a key
    that names one)."""
    return bool(keyed((rule for rules in book(_SET).values() for rule in rules), general(address.strip().strip("."))))
