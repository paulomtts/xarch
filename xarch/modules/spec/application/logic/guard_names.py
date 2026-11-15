"""The name a profile switches each guard on by."""
from __future__ import annotations

from xarch.modules.spec.domain.values import (
    ClosedTree,
    DeadCode,
    Guard,
    NoComments,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    PassThrough,
    PrivateImports,
    ScenarioCoverage,
    StandIns,
)

_GUARD_NAMES: dict[type, str] = {PackageOnly: "package-only", ScenarioCoverage: "scenario-coverage",
                                 NoComments: "no-comments", StandIns: "stand-ins", ClosedTree: "closed-tree",
                                 NoDuplicates: "no-duplicates", NoTwins: "no-twins", DeadCode: "dead-code", PassThrough: "pass-through",
                                 PrivateImports: "private-imports"}


def guard_name(guard: Guard) -> str:
    """The name a profile switches the guard on by, one of GUARDS."""
    return _GUARD_NAMES[type(guard)]
