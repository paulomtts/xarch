"""The values the rules module hands out as they are, which its contract re-exports as it does an id: each is read
outside rules just as rules holds it, so there is nothing to reshape. Everything else rules hands out is a type of the
contract's own.

    At    a place in a file, as the enforcement section names a skip or a dynamic import; the command line shows it
    Unresolved an import the reader could not follow, as the enforcement section lists it; the command line shows it
    Weak  a check met to the letter only, which the enforcement section lists and the command line shows
    KnownName a public name only the tests use that the profile accepts, which the enforcement section names and the
          command line shows
    Translation a pair of classes no-twins accepts as a translation, which the enforcement section names and the
          command line shows
    Slot  a slot of a check as a profile writes it, which `profile explain checks` shows
    Drift an init file as it stands against what `init` would write, which the enforcement section lists
    KeyFacts what the format says of a key the profile sets nowhere, which the command line shows
    Loosened one way a profile is looser than the profile it is compared with, which the command line shows
    Resemblance whether a profile is bundled, the profile it is compared with, how much the two have in common
          and how it is looser, which the command line shows
    Reviewed what checking a profile that loads found before its own checks are held, which the command line shows
    Piece one piece of a source file as the reader cuts it, which SourcesRead hands out

and CHECKS, the address of how a check is written, the keys of the enforcement's sections (SECTIONS), where a file
found to be read lies, and the kinds of a piece.
"""
from __future__ import annotations

from dataclasses import dataclass

CHECKS = "checks"
"""The address `profile explain` explains how a check is written at, and the first step of a slot's (checks.keep)."""
GUARDS_OFF, UNGOVERNED, INIT_FILES, SKIPPED, DYNAMIC, UNRESOLVED, WEAK, APPROXIMATE, VACUOUS, UNPLACED = (
    "guards_off", "ungoverned", "init_files", "skipped", "dynamic", "unresolved", "weak", "approximate", "vacuous",
    "litmus")
"""The keys of the sections of the enforcement a finding `--strict` fails on is under: a guard left off, an
ungoverned file, an init file, a skip, a dynamic import, an import the reader could not follow, a weak finding, an
approximate key, a check of the profile's own that reads nothing, and a part redefined without its litmus."""
SECTIONS = (GUARDS_OFF, UNGOVERNED, INIT_FILES, SKIPPED, DYNAMIC, UNRESOLVED, WEAK, APPROXIMATE, VACUOUS, UNPLACED)
"""Every key of a section of the enforcement, in the order the sections are shown."""


@dataclass(frozen=True)
class At:
    """A place in a file: how the file is shown and the line."""
    file: str
    line: int


@dataclass(frozen=True)
class Unresolved:
    """An import of a file read that names a place of the app (relative, or by an alias the project maps) the reader
    found no file or folder for: how the file is shown, the import's first line, and the module as the source writes
    it."""
    file: str
    line: int
    written: str


@dataclass(frozen=True)
class Weak:
    """A check satisfied to the letter only, which is not a violation: the id of the check it concerns (one of RULES,
    or the id of a check the profile writes itself, listed by its mode), where, and why; fix is what to do about it,
    empty when there is no advice."""
    rule: str
    file: str
    line: int
    message: str
    fix: str = ""


@dataclass(frozen=True)
class KnownName:
    """A public name only the tests use that the profile accepts as such (guards.dead-code.known): the file defining
    it, as shown, its line, and the name."""
    file: str
    line: int
    name: str


@dataclass(frozen=True)
class AcceptedEdge:
    """An import of a part that its imports.may does not allow and its imports.accepted accepts: the file importing,
    as shown, the line, the part, the import as the entry writes it, and why."""
    file: str
    line: int
    part: str
    written: str
    why: str


@dataclass(frozen=True)
class Excused:
    """A finding an entry of the profile accepts (checks.<id>.accepted, structure.accepted, tiers.<tier>.accepted), which
    is then not reported: the rule that found it, its file, as shown, and line (0: the file as a whole), the key of
    the entry, the finding's message, and why."""
    rule: str
    file: str
    line: int
    key: str
    message: str
    why: str


@dataclass(frozen=True)
class Translation:
    """A pair of classes no-twins does not report because a function of a part guards.no-twins.translated lists
    translates one into the other: the file of the function, as shown, its line and its name (`<class>.<name>` for a
    method), the class its file builds and the other class, each by its name."""
    file: str
    line: int
    function: str
    built: str
    other: str


@dataclass(frozen=True)
class Slot:
    """A slot of a check as a profile writes it: its name, what it is for, what it accepts, and the category of words
    it is written with ("" for one written in words of its own)."""
    name: str
    meaning: str
    accepts: str
    takes: str = ""


@dataclass(frozen=True)
class Drift:
    """An init file as it stands: missing, or changed from what `init` would write (pinned files only). path is its
    path below the folder holding the app."""
    path: tuple[str, ...]
    state: str


@dataclass(frozen=True)
class KeyFacts:
    """What the format says of a key: how a profile writes it ("" for no example), its own name, what holds it when
    it is set on each of a kind of thing (part or tier, "" for neither), and the command other than `check` that alone
    reads it ("" for none)."""
    example: str = ""
    name: str = ""
    holder: str = ""
    read_by: str = ""


@dataclass(frozen=True)
class Loosened:
    """One way a profile is looser than the profile it is compared with: the key of the profile's format
    that loosened (imports.may, imports.libraries, litmus and the others the spec module names), the part or tier, what it
    loosened to ("" for nothing more), and all of it in a sentence naming the key of the profile that does."""
    key: str
    part: str
    what: str = ""
    sentence: str = ""


@dataclass(frozen=True)
class Resemblance:
    """How a profile stands to the bundled ones, as the spec module's origin of it says.

    bundled: whether it is one, its own baseline
    compared: the profile it is compared with: for a custom profile the bundled one, and for either the one --against
        names; None when it is bundled and --against is not given, or none is
    looser: how it is looser than the profile it is compared with, in the order the spec module finds it
    chosen_by: why that one: "based_on", the profile says it is based on it, "closest", it has the highest match, or
        "against", --against names it for this run; None when nothing is compared
    match: the share of what `check` reads under either profile that has a counterpart in the other, rounded to two
        decimals; None when nothing is compared
    low: the match is below the line of a low one, or no part pairs
    counts: (kind, comparable, all) for each kind of thing `check` reads, in the order they are said
    only_here, only_there: the parts, then the tiers, of this profile, and of the one it is compared with, that pair
        with none of the other's, each as "part <name>" or "tier <name>", by name
    elsewhere: each part the other profile has by the same name at another path, as "<name>: <its path there> there"
    higher: when it is compared with the profile it says it is based on, the bundled profile of higher match and that
        match; None when there is none
    based_on: with --against, the profile its own based_on names, said beside it; empty otherwise
    anchor: the bundled profile --strict rests on, as the spec module's origin names it: the one compared with when
        that one is bundled, so a profile file is compared with exactly when chosen_by is "based_on" and anchor is not
        compared; None for a bundled profile without --against, with --against, and when there is none
    """
    bundled: bool
    compared: str | None = None
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
class Reviewed:
    """A profile that loads, as checking it found it before its own checks are held: where it is, what its examples
    import that their part may not (each in words), how many files it points to, and how it stands to the bundled
    profiles."""
    location: str
    examples: tuple[str, ...]
    files: int
    resemblance: Resemblance


IN_PART, NOT_THERE, NOT_SOURCE, IN_TESTS, IN_PROJECT, EXCLUDED, IN_NO_PART, LINKED_OUT = (
    "part", "missing", "other", "tests", "project", "excluded", "ungoverned", "linked")
"""Where a file found at a path given to be read lies (SourceRead.lies): in a part of the app; nowhere, it is not
there; it is no source file of the app's language; below the tests root; in the project, outside the app and the
tests; below a folder the profile excludes; in the app, in no part; in a part, but reached through a link to a file
outside the app, or to no source file of the app's language."""

FUNCTION = "function"
"""The kind of a piece that is a function at the top level of its file."""
CLASS = "class"
"""The kind of a piece that is a class at the top level of its file."""
METHOD = "method"
"""The kind of a piece that is a function defined in the body of a class at the top level of its file."""


@dataclass(frozen=True)
class Piece:
    """One piece of a source file as its language's reader cuts it, which SourcesRead hands out: a function or a
    class at the top level of the file, or a method of such a class, which owner then names; its kind is one of
    FUNCTION, CLASS and METHOD. first and last are the lines it spans, counted from 1, its decorators included, so that
    its text is those lines."""
    kind: str
    name: str
    first: int
    last: int
    owner: str = ""
