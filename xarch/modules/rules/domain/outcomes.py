"""The values the source rules reason about: what a check found, and how the profile in force stands."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.violations import Violation
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import (
    AcceptedEdge,
    At,
    BaselineStanding,
    Drift,
    Excused,
    KnownName,
    Loosened,
    Translation,
    Unresolved,
    Weak,
)
from xarch.profile_values.capabilities import Shortfall
from xarch.profile_values.excluded import Excluded


@dataclass(frozen=True)
class InitFile:
    """A file `init` writes beside the app folder: its path below the folder holding the app, the text `init` would
    write now, and whether it is pinned: the project keeps it as written."""
    path: tuple[str, ...]
    text: str
    pinned: bool = False


@dataclass(frozen=True)
class Known:
    """The profiles a project knows: the one in force for it (None: none is configured), and the bundled ones."""
    in_force: str | None
    bundled: tuple[str, ...]


@dataclass(frozen=True)
class Standing:
    """How the profile in force stands, besides its rules: the guards xarch has that it leaves off, in xarch's order,
    and those the bundled profile it is, or is compared with, leaves off too (baseline_off); the files `init` would
    write now beside the app folder, in the profile's order; and, for a custom profile, every way it is looser than the
    bundled profile it is compared with (looser)."""
    guards_off: tuple[str, ...]
    baseline_off: tuple[str, ...]
    init_files: tuple[InitFile, ...]
    looser: tuple[Loosened, ...] = ()


@dataclass(frozen=True)
class Finding:
    """An enforcement finding that `--strict` fails on: the key of the enforcement section it is under, and the item
    there that fails: a guard left off or an ungoverned file (by name), an init file that drifted, a skip or a dynamic
    import (where it is), an import the reader could not follow, a weak check, a key whose check reads a fact the
    language supplies only partly, a check of the profile's own that read nothing (its id), or a part redefined
    without its litmus (as said)."""
    key: str
    item: str | Drift | At | Unresolved | Weak | Shortfall


@dataclass(frozen=True)
class Enforcement:
    """The state of the check's own enforcement, beside its violations: the guards the profile leaves off, and those the
    bundled profile it is, or is compared with, leaves off too (baseline_off); the app's source files no part and no
    folder of the layout governs (never read, so never checked), as shown; the init files missing or changed; the
    tests skipped or expected to fail, and the dynamic imports, where they are; the imports of the files read that the
    reader could not follow, with the module as written; the checks satisfied to the letter
    only; and strict, the findings `--strict` fails on; the folders the profile excludes, which no check reads; app,
    the name of the app folder the shown paths start with; language, how the language of the app is named;
    approximate, the keys whose check reads a fact the language supplies only partly, so that it may miss what it
    looks for; and checks, the checks the profile writes itself, each by its id with how many facts it read in the
    project (one that read none passes for want of anything to check, and fails `--strict`); unplaced, each part
    the profile redefines without the litmus the bundled profile it is compared with gives it, as said; and known, the
    public names only the tests use that the profile accepts (guards.dead-code.known), which the tests-only check
    then does not list; and translated, the pairs of classes no-twins accepts as translations
    (guards.no-twins.translated), which it then does not report; and accepted, the imports a part's imports.accepted
    accepts, which may-import then does not report; and excused, the findings the profile's other entries accept
    (checks.<id>.accepted, structure.accepted, tiers.<tier>.accepted, counterparts.<id>.accepted), which are then not
    reported; and counterparts, what the profile says lies with what, each by its id with how many matches of its
    source it read in the project (one that read none passes for want of anything to check, and fails `--strict`);
    and forbidding, the ids of the checks of the profile's own written under may_not, whose point is to find nothing."""
    guards_off: tuple[str, ...] = ()
    baseline_off: tuple[str, ...] = ()
    ungoverned: tuple[str, ...] = ()
    init_files: tuple[Drift, ...] = ()
    skipped: tuple[At, ...] = ()
    dynamic: tuple[At, ...] = ()
    unresolved: tuple[Unresolved, ...] = ()
    weak: tuple[Weak, ...] = ()
    strict: tuple[Finding, ...] = ()
    excluded: tuple[Excluded, ...] = ()
    app: str = ""
    language: str = ""
    approximate: tuple[Shortfall, ...] = ()
    checks: tuple[tuple[str, int], ...] = ()
    unplaced: tuple[str, ...] = ()
    known: tuple[KnownName, ...] = ()
    translated: tuple[Translation, ...] = ()
    accepted: tuple[AcceptedEdge, ...] = ()
    excused: tuple[Excused, ...] = ()
    counterparts: tuple[tuple[str, int], ...] = ()
    forbidding: tuple[str, ...] = ()


@dataclass(frozen=True)
class Twins:
    """What the no-twins check found: the violations, and the pairs it accepts as translations, which it does not
    report."""
    violations: tuple[Violation, ...]
    translated: tuple[Translation, ...]


@dataclass(frozen=True)
class Accepting:
    """What the tests-only check lists once the public names the profile accepts as only the tests' are taken out:
    the findings still listed, each entry that no longer holds among them, and the names accepted."""
    listed: tuple[Violation | Weak, ...]
    known: tuple[KnownName, ...]


@dataclass(frozen=True)
class Ratchet:
    """What the imports the parts accept come to: each entry that no longer accepts anything, as a may-import
    violation, and each import accepted."""
    stale: tuple[Violation, ...]
    accepted: tuple[AcceptedEdge, ...]


@dataclass(frozen=True)
class Sifted:
    """What findings come to once the entries that accept some are held against them: the findings still reported,
    each entry that accepts nothing, as a violation, and each finding accepted."""
    kept: tuple[Violation | Weak, ...]
    stale: tuple[Violation, ...]
    excused: tuple[Excused, ...]


@dataclass(frozen=True)
class StructureFound:
    """What the layout finds wrong below an app folder: the violations, the findings structure.accepted or a
    counterpart's accepted accepts, which it does not report, and how many matches of its source each counterpart
    read, by its id."""
    violations: tuple[Violation, ...]
    excused: tuple[Excused, ...] = ()
    counterparts: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True)
class Baselined:
    """What the baseline comes to on a run: the violations it does not hold back, in their order, and how it stands."""
    shown: tuple[Violation, ...]
    standing: BaselineStanding


@dataclass(frozen=True)
class Checked:
    """What a check found: the violations, in the order the checks found them; the state of its enforcement; and the
    profile it checked against."""
    violations: tuple[Violation, ...]
    enforcement: Enforcement
    profile: Profile
