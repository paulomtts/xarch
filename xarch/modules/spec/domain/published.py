"""The values spec hands out as they are, which its contract re-exports as it does an id: each is read outside spec
just as spec holds it, so there is nothing to reshape. Everything else spec hands out is a type of the contract's own.

    Origin       where the profile in force comes from and how far it can be trusted, which the command line shows
                 and the checking module reads the guards of
    Loosened     one way a profile is looser than the bundled one it resembles, held by Origin and shown as it is
    LITMUS       the key of the Loosened that says a part lost its litmus, which the checking module fails
                 `check --strict` on
    ProjectFile  a file `init` writes beside the app folder, which the module that scaffolds writes and the checking
                 module compares a pinned one with
    DEFAULT_APP  the app folder read when none is given or recorded, which the module that scaffolds leaves
                 unrecorded
    DEFAULT_TESTS  the tests folder read when none is given or configured, where the checking module shows the
                 tests to be when there is none
    Entry        a folder or a file of a profile's layout, which the modules that check and build the layout read
    DocFile      a project doc and the text it starts with, which the module that scaffolds writes
"""
from __future__ import annotations

from dataclasses import dataclass

DEFAULT_APP = "app"
"""The app folder xarch assumes, in the working folder, when none is given or recorded."""
DEFAULT_TESTS = "tests"
"""The tests folder xarch assumes, beside the app folder, when none is given or configured."""
LITMUS = "litmus"
"""The key of a Loosened that says a part lost the litmus the bundled profile gives it: the one way of being looser
that leaves the code with no question to place it by, which `check --strict` fails on."""


@dataclass(frozen=True)
class Loosened:
    """One way a profile is looser than the bundled profile it is compared with. key is what loosened:

        may_import      part may also import what (a target as written)
        libraries       part may also import the outside package what; with no part, outside packages are unchecked
        must_import     part may also meet must_import with the target what; with no what, it has none now
        forbidden       part no longer forbids what
        untested        part is newly marked untested
        litmus          part has no litmus, though the bundled profile gives it one (LITMUS)
        types_only      the tests of tier part may now call what
        may_also_import the tests of tier part may also import what (a target as written)
        apply_forbidden the tests of tier part are no longer held to their part's forbidden list
        testing.skips   what is no longer counted as a skip
        files.pinned    the init file what is no longer pinned
        reserved        the standard-library name what is no longer reserved
        known           the tests-only check accepts the name what as one only the tests use
        translated      no-twins accepts each pair of classes a function of part translates
        review.never    the path pattern what, which the bundled profile never sends, may be sent again
        review.mask     the text pattern what, which the bundled profile hides, is no longer masked

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


@dataclass(frozen=True)
class Entry:
    """
    path: a folder or a file of the layout, e.g. ("application", "controller<ending>")
    leaf: a file, or a directory that holds nothing in the spec
    """
    path: tuple[str, ...]
    is_dir: bool
    leaf: bool


@dataclass(frozen=True)
class DocFile:
    """
    path: below the docs root, e.g. ("adrs", "0000-template.md")
    template: the text a new file starts with, filled from the profile's template
    """
    path: tuple[str, ...]
    template: str
