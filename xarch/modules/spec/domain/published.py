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
    LINE         the line of a part no `evals.placement.lines` writes one for, which the module that reviews reads a
                 file's answer against
    Eval         an eval of the profile's own, which the module that reviews asks and the checking module holds to its
                 examples statically; YES_NO, SCORE and CHOICE its answer forms, READS what one question may be asked
                 of
"""
from __future__ import annotations

from dataclasses import dataclass, field

from xarch.profile_values.checks import Condition, Scope

DEFAULT_APP = "app"
"""The app folder xarch assumes, in the working folder, when none is given or recorded."""
DEFAULT_TESTS = "tests"
"""The tests folder xarch assumes, beside the app folder, when none is given or configured."""
LITMUS = "litmus"
"""The key of a Loosened that says a part lost the litmus the bundled profile gives it: the one way of being looser
that leaves the code with no question to place it by, which `check --strict` fails on."""
EXAMPLE_APP = "app"
"""The app folder's name in the docs' example project, which shows an example file with its placeholder filled: the
import name the code of the docs' examples, and of placement's own examples, is written for."""
LINE = 0.3
"""The line of a part the profile writes none for under `evals.placement.lines`: below it, the probability review's
decision model puts on the part a file sits in reads as doubtful there. In the trials it caught about nine in ten
plainly misplaced files and doubted about one well-placed file in ten."""


YES_NO, SCORE, CHOICE = "yes-no", "score", "choice"
"""The answer forms of an eval of the profile's own: yes or no; a score of five levels, 0 to 4; a choice of one option
out of three or more."""
READS = ("file", "class", "function")
"""What one question of an eval of the profile's own is asked of: a file whole, each class at its top level, or each
function (a method is a function)."""


@dataclass(frozen=True)
class Eval:
    """An eval of the profile's own, as it is written under `evals.<id>`, everything already checked statically.

    ask: the question, one short rule about what the text shows
    form: YES_NO, SCORE or CHOICE
    options: what each answer means, in order, each a name and its description: for YES_NO `yes` and `no` (a
        description "" when it is not written), for SCORE the levels `0` to `4`, for CHOICE the options as written
    flagged: the names of the options whose probability reads as the fault: `yes`; the levels from `flagged_from`; or
        the options `flagged` lists
    reads: one of READS
    within: the files it is asked in, as a check's `in` (the app's files only)
    keep: the filters a fact must pass, as a check's `keep`, in the words of the check vocabulary
    line: the value at or above which a reading is listed; None when calibration sets it
    message, fix: what is said of a reading, with {file}, {line}, {name} and {value}
    flagged_examples, clean_examples: the code it must read as flagged and as clean, each a file by its path below
        the app and its text, in the order of the file
    """
    ask: str
    form: str
    options: tuple[tuple[str, str], ...]
    flagged: tuple[str, ...]
    reads: str
    within: Scope = field(default_factory=Scope)
    keep: tuple[Condition, ...] = ()
    line: float | None = None
    message: str = ""
    fix: str = ""
    flagged_examples: tuple[tuple[str, str], ...] = ()
    clean_examples: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Loosened:
    """One way a profile is looser than the bundled profile it is compared with. key is what loosened:

        may_import      part may also import what (a target as written)
        libraries       part may also import the outside package what; with no part, outside packages are unchecked
        must_import     part may also meet must_import with the target what; with no what, it has none now
        uses.never      part no longer forbids what
        untested        part is newly marked untested
        litmus          part has no litmus, though the bundled profile gives it one (LITMUS)
        types_only      the tests of tier part may now call what
        may_also_import the tests of tier part may also import what (a target as written)
        uses.apply_never the tests of tier part are no longer held to their part's never list
        testing.skips   what is no longer counted as a skip
        files.pinned    the init file what is no longer pinned
        reserved        the standard-library name what is no longer reserved
        known           the tests-only check accepts the name what as one only the tests use
        translated      no-twins accepts each pair of classes a function of part translates
        review.never    the path pattern what, which the bundled profile never sends, may be sent again
        review.mask     the text pattern what, which the bundled profile hides, is no longer masked
        evals.placement.lines  part reads as doubtful only below the line what, lower than the bundled profile's

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
