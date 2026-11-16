"""The values spec hands out as they are, which its contract re-exports as it does an id: each is read outside spec
just as spec holds it, so there is nothing to reshape. Everything else spec hands out is a type of the contract's own.

    Copy         a file the conversion of a profile copies, which the command line shows: where it goes, and
                 from where
    Origin       where the profile in force comes from and how far it can be trusted, which the command line shows
                 and the checking module reads the guards of
    Loosened     one way a profile is looser than the bundled one it resembles, held by Origin and shown as it is
    ProjectFile  a file `init` writes beside the app folder, which the module that scaffolds writes and the checking
                 module compares a pinned one with
    DEFAULT_APP  the app folder read when none is given or recorded, which the module that scaffolds leaves
                 unrecorded
"""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_APP = "app"
"""The app folder xarch assumes, in the working folder, when none is given or recorded."""


@dataclass(frozen=True)
class Copy:
    """A file of the converted folder: where it goes, the file next to the old profile it is read from, and whether its
    example placeholders are rewritten."""
    destination: str
    source: str
    rewritten: bool = False


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


@dataclass(frozen=True)
class ProjectFile:
    """A file `init` writes beside the app folder, in the folder holding it.

    path: below the folder holding the app, e.g. ("tests", "architecture", "test_rules<ending>"); a file inside the app
        folder starts with the app folder's name
    content: the file's text, the app folder's name filled in, or, for a file that is not filled, its bytes as they are
    pinned: the project keeps it as written; `check` reports it when it differs
    """
    path: tuple[str, ...]
    content: str | bytes
    pinned: bool = False
