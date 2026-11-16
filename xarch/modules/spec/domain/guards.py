"""The pre-built checks a profile may switch on, by the name its `guards` key (or, for package-only, a part's
`package_only: true`) uses, each with the kind of value its parameters are read into; what each checks is said by the
text of its key (see key_catalogue)."""
from __future__ import annotations

from xarch.modules.spec.domain.values import (
    ClosedTree,
    DeadCode,
    NoComments,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    PassThrough,
    PrivateImports,
)
from xarch.profile_values.testing import ScenarioCoverage, StandIns

KEY: dict[type, str] = {PackageOnly: "package-only", ScenarioCoverage: "scenario-coverage", NoComments: "no-comments",
                        StandIns: "stand-ins", ClosedTree: "closed-tree", NoDuplicates: "no-duplicates",
                        NoTwins: "no-twins", DeadCode: "dead-code", PrivateImports: "private-imports",
                        PassThrough: "pass-through"}
"""The name a profile switches each guard on by, by the kind of value it is read into."""
GUARD = {key: kind for kind, key in KEY.items()}
"""The kind of value each guard is read into, by the name a profile switches it on by."""

ORDER = ("package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree", "no-duplicates", "no-twins",
         "dead-code", "pass-through", "private-imports")
"""The name of every pre-built check a profile may switch on, in the order xarch lists them."""
