"""What the rules module promises: check the imports below a root folder against section 5."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.kernel.logic.origin import Origin
from xarch.kernel.violations import At, Violation, Weak

__all__ = ["DriftView", "FindingView", "ExcludedView", "EnforcementView", "ReachView", "NearestView", "TierInfoView", "WhereView", "CheckImports", "ImportsChecked",
           "NotADirectory", "CheckResult", "CheckApp", "AppChecked", "CheckAppResult", "Locate", "Located", "Outside", "LocateResult"]


@dataclass(frozen=True)
class DriftView:
    """An init file missing, or changed from what `init` would write: its path below the folder holding the app, as
    posix, and which."""
    file: str
    state: str


@dataclass(frozen=True)
class FindingView:
    """A finding `--strict` fails on: the key of the enforcement section it is under, and what, in words."""
    key: str
    detail: str


@dataclass(frozen=True)
class ExcludedView:
    """A folder the profile leaves out of every check, as shown below the folder holding the app, and why."""
    folder: str
    reason: str


@dataclass(frozen=True)
class EnforcementView:
    """The state of the check's own enforcement, beside its violations, as the enforcement section shows it: the
    origin of the profile; the files no part governs, and the top folders holding them (each once, in order); the init
    files missing or changed; the skipped tests and dynamic imports; the checks met to the letter only; the findings
    `--strict` fails on; the folders the profile excludes; and how the language of the app is named."""
    origin: Origin = Origin()
    ungoverned: tuple[str, ...] = ()
    ungoverned_folders: tuple[str, ...] = ()
    init_files: tuple[DriftView, ...] = ()
    skipped: tuple[At, ...] = ()
    dynamic: tuple[At, ...] = ()
    weak: tuple[Weak, ...] = ()
    strict: tuple[FindingView, ...] = ()
    excluded: tuple[ExcludedView, ...] = ()
    language: str = ""


@dataclass(frozen=True)
class ReachView:
    """One thing a place may import: a part, its scope (own, any, none), the part as the docs name it, and its folder
    below the project root."""
    part: str
    scope: str
    folder: str
    path: str


@dataclass(frozen=True)
class NearestView:
    """A part near a place no part claims: the part, as the docs name it, and its folder below the project root."""
    part: str
    folder: str
    path: str


@dataclass(frozen=True)
class TierInfoView:
    """A kind of test: its name, and the profile's words for what it proves, may touch and its litmus test."""
    name: str
    proves: str = ""
    may_touch: str = ""
    litmus: str = ""


@dataclass(frozen=True)
class WhereView:
    """What a place is and what code there may do, the answer of `xarch where`: its kind (part, structure, ungoverned,
    test, fake or support), its path below the folder holding the app and whether it is there now; the part claiming it
    (for a test, the part it mirrors), its role and litmus test, its name in the docs, its instance and the word of
    one; what it may import, as places and in the docs' words; the outside packages it may import (None: not checked)
    and the names it may not use; the tier that tests it (or why none does) and where its test would live; the parts
    around a place in no part, and whether a file there is a violation; for a test, whether it may import the fakes
    and where they live, the parts it may use as types only and the folder it may import test code from; and a note
    where the kind alone does not say it."""
    kind: str
    path: str
    exists: bool
    part: str = ""
    role: str = ""
    litmus: str = ""
    folder: str = ""
    instance: str = ""
    singular: str = ""
    may_import: tuple[ReachView, ...] = ()
    may_import_text: str = ""
    libraries: tuple[str, ...] | None = None
    forbidden: tuple[str, ...] = ()
    tier: TierInfoView | None = None
    untested: str = ""
    test_folder: str = ""
    test_file: str = ""
    nearest: tuple[NearestView, ...] = ()
    closed_tree: bool = False
    may_use_fakes: bool = False
    fakes_path: str = ""
    types_only: tuple[str, ...] = ()
    test_code_from: str = ""
    note: str = ""


@dataclass(frozen=True)
class CheckImports:
    """Check the code below root, imported as package, and the tests below tests (None: no tests), against the
    architecture at profile (a bundled name or a path)."""
    root: Path
    package: str
    profile: str
    tests: Path | None = None


@dataclass(frozen=True)
class ImportsChecked:
    """The violations, in the order the checks found them, and the state of the check's own enforcement."""
    violations: tuple[Violation, ...]
    enforcement: EnforcementView = EnforcementView()


@dataclass(frozen=True)
class NotADirectory:
    root: Path


CheckResult = ImportsChecked | NotADirectory


@dataclass(frozen=True)
class CheckApp:
    """Check the app below root, its imports and its structure, and the tests below tests (None: no tests), against
    the architecture at profile (a bundled name or a path); strict also fails on the enforcement's findings."""
    root: Path
    profile: str
    tests: Path | None = None
    strict: bool = False


@dataclass(frozen=True)
class AppChecked:
    """The violations of the source, then of the structure; the state of the check's enforcement; the profile's own
    advice by rule id; and whether the check passes: no violation and, under strict, no finding of the enforcement."""
    violations: tuple[Violation, ...]
    enforcement: EnforcementView
    hints: dict[str, str]
    ok: bool


CheckAppResult = AppChecked | NotADirectory


@dataclass(frozen=True)
class Locate:
    """Say what the path is and what code there may do. path is given from cwd, from the folder holding app, or from
    app; it may not exist yet. tests is the tests root (None: none), profile the architecture in force."""
    path: Path
    cwd: Path
    app: Path
    profile: str
    tests: Path | None = None


@dataclass(frozen=True)
class Located:
    where: WhereView


@dataclass(frozen=True)
class Outside:
    """The path is not in the project; reason is safe to show the user as-is."""
    reason: str


LocateResult = Located | Outside
