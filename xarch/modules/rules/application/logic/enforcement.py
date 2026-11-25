"""The findings of the enforcement section, besides the violations: what the check could not see or was told to
pass over, read from the same parsed files.

    skipped    a use, in a test file, of a name the profile's `testing.skips` lists, or one below it: a marker such as
               `pytest.mark.skip`, `pytest.mark.skipif(...)` (a name of its own, so listed on its own) or a call such
               as `pytest.skip(...)`, read through imports like any use (see the Use value); one per use
    dynamic    a use, in a file read, of what the language of the app imports by a computed or string name with,
               the names its data file lists; the import rules cannot see what those import
    unresolved an import, in a file read, naming a place of the app (relative, or by an alias the project maps) the
               reader found no file or folder for, with the module as written; the import rules cannot see what it
               names
    drift      an init file (`files` in the profile) that is missing, or pinned and not what `init` would write now

strict_findings lists what `--strict` fails on: what the profile in force leaves unenforced or unseen. That is every
guard it leaves off but those that the bundled profile in force, or the one a custom profile is compared with, also
leaves off (with no profile to compare with, every guard left off), the ungoverned files, the init files missing or
changed, the skips, the dynamic imports, the imports the reader could not follow, the weak checks, the keys whose
check reads a fact the language supplies only partly (approximate), the checks of the profile's own that read
nothing (vacuous) and each part a custom profile
redefines without the litmus the bundled profile it is compared with gives it (litmus), which leaves its code no
question to be placed by. Every other way a custom profile differs from the closest bundled one (`origin.looser`) is
information in the enforcement section and no finding: the profile defines the architecture.

What the enforcement section shows of them is worked out here too: the folders holding the ungoverned files, a
finding's detail, and an excluded folder as it is shown below the folder holding the app.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.outcomes import Enforcement, Finding, InitFile
from xarch.modules.rules.domain.parsed import SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import (
    APPROXIMATE,
    DYNAMIC,
    GUARDS_OFF,
    INIT_FILES,
    SKIPPED,
    UNGOVERNED,
    UNPLACED,
    UNRESOLVED,
    VACUOUS,
    WEAK,
    At,
    Drift,
    Loosened,
    Unresolved,
    Weak,
)
from xarch.profile_values.capabilities import Shortfall
from xarch.profile_values.excluded import Excluded

MISSING, CHANGED = "missing", "changed"


def skipped(tests: Iterable[SourceFile], profile: Profile) -> list[At]:
    skips = profile.framework.skips if profile.framework is not None else ()
    return [At(file.name, use.line) for file in tests for use in file.uses
            if any(use.name[:len(skip)] == skip for skip in skips)]


def dynamic(files: Iterable[SourceFile], profile: Profile) -> list[At]:
    return [At(file.name, use.line) for file in files for use in file.uses if use.name in profile.language.dynamic]


def unresolved(files: Iterable[SourceFile]) -> list[Unresolved]:
    """Each import of the files that the reader could not follow, the files in the order given and the imports of each
    by line: a reader need not hand them over in that order."""
    return [Unresolved(file.name, i.line, i.written) for file in files
            for i in sorted(file.imports, key=lambda i: i.line) if i.unresolved]


def drift(files: Sequence[InitFile], found: Sequence[str | None]) -> list[Drift]:
    """found holds the text of each file as it stands, None where there is none."""
    states = [(file, MISSING if text is None else CHANGED if file.pinned and text != file.text else None)
              for file, text in zip(files, found)]
    return [Drift(file.path, state) for file, state in states if state is not None]


def unplaced(looser: Iterable[Loosened]) -> tuple[str, ...]:
    """Each way a profile is looser that `--strict` fails on, as said: a part redefined without the litmus the bundled
    profile it is compared with gives it, whose key is the key of its section of the enforcement."""
    return tuple(item.sentence for item in looser if item.key == UNPLACED)


def strict_findings(enforcement: Enforcement) -> tuple[Finding, ...]:
    found = [Finding(GUARDS_OFF, g) for g in enforcement.guards_off if g not in enforcement.baseline_off]
    found += [Finding(UNGOVERNED, file) for file in enforcement.ungoverned]
    found += [Finding(INIT_FILES, item) for item in enforcement.init_files]
    found += [Finding(SKIPPED, at) for at in enforcement.skipped]
    found += [Finding(DYNAMIC, at) for at in enforcement.dynamic]
    found += [Finding(UNRESOLVED, item) for item in enforcement.unresolved]
    found += [Finding(WEAK, weak) for weak in enforcement.weak]
    found += [Finding(APPROXIMATE, item) for item in enforcement.approximate]
    found += [Finding(VACUOUS, _vacuous(name)) for name, read in enforcement.checks if not read]
    found += [Finding(UNPLACED, sentence) for sentence in enforcement.unplaced]
    return tuple(found)


def reading(name: str, read: int) -> str:
    """How much a check of the profile's own read, in words."""
    return _vacuous(name) if not read else f"checks.{name} read {read} fact{'' if read == 1 else 's'}"


def _vacuous(name: str) -> str:
    """A check of the profile's own that read nothing, in words."""
    return (f"checks.{name} reads nothing in the project, so it passes for want of anything to check: widen what it "
            "reads, or drop it")


def detail(item: str | Drift | At | Unresolved | Weak | Shortfall) -> str:
    """A finding's item in words: a guard or a file by its name, an init file with its state, a place as
    `<file>:<line>`, an import the reader could not follow as its place, its module as written and that it names no
    file of the app, a weak check as its place (the file alone for a whole file) and its message, a key whose check
    reads a fact partly as the key, the fact and what the reader misses, and one whose check reads less for want of a
    fact by what it reads less."""
    match item:
        case Drift(path, state):
            return f"{'/'.join(path)} is {state}"
        case At(file, line):
            return f"{file}:{line}"
        case Unresolved(file, line, written):
            return f'{file}:{line}: import "{written}" names no file of the app'
        case Weak(file=file, line=line, message=message):
            return f"{file}{f':{line}' if line else ''}: {message}"
        case Shortfall(address, fact, note, unread):
            return approximation(address, fact, note or "", unread)
        case _:
            return item


def approximation(address: str, fact: str, note: str, unread: bool = False) -> str:
    """A key whose check reads a fact the language supplies only partly, in words; one whose check reads less for want
    of a fact it reads only when supplied, by its note alone, which says it whole."""
    return note if unread else f"{address} reads {fact} only partly: {note}"


def folders(files: Sequence[str]) -> list[str]:
    """The top folders below the app holding the files, each once, in order; a file at the app's root as itself."""
    tops = ["/".join(parts[:2]) + "/" if len(parts) > 2 else file
            for file in files for parts in [file.split("/")]]
    return list(dict.fromkeys(tops))


def excluded_folder(app: str, excluded: Excluded) -> str:
    """An excluded folder as shown below the folder holding the app folder named app, such as "app/examples"."""
    return "/".join((app, *excluded.path))


def weak_of(found: Iterable[Violation | Weak], untested: Iterable[Violation | Weak], tests: bool) -> list[Weak]:
    """The findings the enforcement section lists as weak, in order: those found, then those of the untested check,
    which count only when there are tests to have tested the code."""
    return [item for item in (*found, *(untested if tests else ())) if isinstance(item, Weak)]
