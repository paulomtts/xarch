"""Where the profile in force comes from and how far it can be trusted: spec works it out, the rules module reports it
with the check's enforcement."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Loosened:
    """One way a profile is looser than the bundled profile it is compared with. key is what loosened:

        may_import      part may also import what (a target as written)
        libraries       part may also import the outside package what; with no part, outside packages are unchecked
        must_import     part may also meet must_import with the target what; with no what, it has none now
        forbidden       part no longer forbids what
        untested        part is newly marked untested
        types_only      the tests of tier part may now call what
        apply_forbidden the tests of tier part are no longer held to their part's forbidden list
        testing.skips   what is no longer counted as a skip
        files.pinned    the init file what is no longer pinned
        reserved        the standard-library name what is no longer reserved

    sentence says it, naming the key of the profile that does.
    """
    key: str
    part: str
    what: str = ""
    sentence: str = ""


@dataclass(frozen=True)
class Origin:
    """Where a profile comes from: location as selected, a bundled name or a path; whether it is bundled; closest, for
    a custom file, the bundled profile sharing the most parts (the first by name on a tie), None when it is bundled or
    shares none; guards_off, the guards xarch has that it leaves off, in xarch's order; baseline_off, those the bundled
    profile it is, or is compared with, leaves off too; and looser, how it is looser than closest."""
    location: str = ""
    bundled: bool = True
    closest: str | None = None
    guards_off: tuple[str, ...] = ()
    baseline_off: tuple[str, ...] = ()
    looser: tuple[Loosened, ...] = ()
