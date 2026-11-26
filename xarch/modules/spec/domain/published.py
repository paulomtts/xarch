"""The values spec hands out as they are, which its contract re-exports as it does an id: each is read outside spec
just as spec holds it, so there is nothing to reshape. Everything else spec hands out is a type of the contract's own.

    Origin       where the profile in force comes from, the profile it is compared with and how much the two have
                 in common, which the command line shows and the checking module reads the guards of;
                 BASED_ON, CLOSEST and AGAINST why it is compared with that one
    Loosened     one way a profile is looser than the profile it is compared with, held by Origin and shown as it is
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
    Held         one kind of definition a part's `holds` lists, with its settings, which the checking module holds a
                 part's files to; KINDS the kinds, in the order they are read and said
    Counterpart  what the profile says lies with what (`counterparts`), its paths each a PathPattern, which the
                 module that checks the layout holds the disk to
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


KINDS = ("classes", "functions", "records", "exceptions")
"""The kinds of definition a part's `holds` lists, in the order they are read and said: every class defined at the top
level of a file, every public function defined there, in no class, a record and an exception; a record and an
exception are classes too, narrower than every class."""


@dataclass(frozen=True)
class Held:
    """One kind of definition a part's `holds` lists, one of KINDS, with its settings: the patterns one of which every
    public definition held to the kind matches (`*` for any text; empty: any name); whether every class held to it, but
    an exception, is an immutable record; and the only parts whose code may build a class held to it (empty: any
    part). A setting the kind does not take stays at its default."""
    kind: str
    names: tuple[str, ...] = ()
    immutable: bool = False
    built_by: tuple[str, ...] = ()


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

        imports.may     part may also import what (a target as a reference: parts.<part> or <word>.<part>)
        imports.may.types_only
                        part may now call what, a target it used only as a type
        imports.libraries
                        part may also import the outside package what; with no part, outside packages are unchecked
        imports.must    part may also meet imports.must with the target what; with no what, it has none now
        uses.never      part no longer forbids what
        untested        part is newly marked untested
        litmus          part has no litmus, though the bundled profile gives it one (LITMUS); with what, though
                        what, the anchor --strict rests on, gives the part it pairs with one
        imports.types_only
                        the tests of tier part may now call what
        imports.also    the tests of tier part may also import what (a target as a reference: parts.<part> or <word>.<part>)
        uses.apply_never the tests of tier part are no longer held to their part's never list
        testing.skips   what is no longer counted as a skip
        testing.beside  the tests of a part may sit beside its code, which the compared profile does not allow
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


BASED_ON, CLOSEST, AGAINST = "based_on", "closest", "against"
"""Why a profile is compared with the one it is (Origin.chosen_by): a custom one says it is based on it, or that one
has the highest match; or, for this run, --against names it."""


@dataclass(frozen=True)
class Origin:
    """Where a profile comes from and the profile it is compared with.

    location: as selected, a bundled name or a path
    bundled: whether it is a bundled profile, its own baseline
    compared: the profile it is compared with, as its location is given: for a custom file the bundled one, or the
        profile file its based_on names, as written there; for either the one --against names; None when it is
        bundled and --against is not given, or none is
    guards_off: the guards xarch has that it leaves off, in xarch's order
    baseline_off: those the profile it is, or is compared with, leaves off too; for one based on a profile file, those
        the anchor and every file of the chain leave off too, none when there is no anchor
    looser: how it is looser than the profile it is compared with
    chosen_by: why that one: BASED_ON, CLOSEST or AGAINST; None when nothing is compared
    match: the share of what `check` reads under either profile that has a counterpart in the other, rounded to two
        decimals; None when nothing is compared
    low: the match is below the line of a low one, or no part pairs
    counts: (kind, comparable, all) for each kind of thing `check` reads, in the order they are said
    only_here, only_there: the parts, then the tiers, of this profile, and of the one it is compared with, that pair
        with none of the other's, each as "part <name>" or "tier <name>", by name
    elsewhere: each part the other profile has by the same name at another path, as "<name>: <its path there> there"
    higher: when it is compared with the profile it says it is based on, the bundled profile of higher match and that
        match; None when there is none, and always with --against
    based_on: with --against, the profile its own based_on names, which the command line says beside it; empty
        otherwise
    anchor: the bundled profile --strict rests on: the one compared with when that one is bundled (so a profile file
        is compared with exactly when chosen_by is BASED_ON and anchor is not compared); for one based on a profile
        file, the bundled profile the chain of files ends on, else the bundled profile of highest match with its last
        file; None for a bundled profile without --against, with --against, and when there is none
    """
    location: str = ""
    bundled: bool = True
    compared: str | None = None
    guards_off: tuple[str, ...] = ()
    baseline_off: tuple[str, ...] = ()
    looser: tuple[Loosened, ...] = ()
    chosen_by: str | None = None
    match: float | None = None
    low: bool = False
    counts: tuple[tuple[str, int, int], ...] = ()
    only_here: tuple[str, ...] = ()
    only_there: tuple[str, ...] = ()
    elsewhere: tuple[str, ...] = ()
    higher: tuple[str, float] | None = None
    based_on: str = ""
    anchor: str | None = None


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
    leaf: a file, or a directory that holds nothing in the spec but optional parts
    optional: it is an optional part: it need not be there
    when: the optional part it lies in, the deepest, by its path as path is written: it need be there only when that
        part is; () for none
    """
    path: tuple[str, ...]
    is_dir: bool
    leaf: bool
    optional: bool = False
    when: tuple[str, ...] = ()


@dataclass(frozen=True)
class DocFile:
    """
    path: below the docs root, e.g. ("adrs", "0000-template.md")
    template: the text a new file starts with, filled from the profile's template
    """
    path: tuple[str, ...]
    template: str


@dataclass(frozen=True)
class AcceptedPath:
    """A finding of the layout the profile accepts (`structure.accepted`): the folder or file it is about, by its path
    below the app (tests/<path> for one below the tests root), as written; and why it is accepted."""
    path: tuple[str, ...]
    why: str


@dataclass(frozen=True)
class PathPattern:
    """A path a counterpart names, as the profile writes it: its steps below the app (tests/<path> for one below the
    tests root), each a name in which `<word>` is a placeholder and `*` any text within the step; and whether it is a
    folder, written ending in `/`."""
    steps: tuple[str, ...]
    folder: bool

    @property
    def written(self) -> str:
        return "/".join(self.steps) + ("/" if self.folder else "")


@dataclass(frozen=True)
class Counterpart:
    """What the profile says lies with what (`counterparts.<id>`): its id; source, the path whose every match must
    have a counterpart; has, the path the counterpart is at, its placeholders bound by source; when, the paths
    that must also match, so bound, for a match of source to need one; the sources it accepts with none (`accepted`),
    each with why; and the message and fix of a source with none, "" for xarch's own."""
    id: str
    source: PathPattern
    has: PathPattern
    when: tuple[PathPattern, ...] = ()
    accepted: tuple[AcceptedPath, ...] = ()
    message: str = ""
    fix: str = ""
