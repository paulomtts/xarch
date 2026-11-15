"""What the rules module promises: check the imports below a root folder against section 5."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from xarch.kernel.logic.origin import Origin
from xarch.kernel.violations import At, Violation, Weak

__all__ = ["DriftView", "FindingView", "ExcludedView", "EnforcementView", "ReachView", "NearestView", "TierInfoView",
           "PartShown", "CoveringTest", "Untested", "InPart", "InStructure", "Ungoverned", "InTests", "Support", "Fake",
           "WhereAnswer", "CheckImports", "ImportsChecked", "NotADirectory", "CheckResult", "CheckApp", "AppChecked",
           "CheckAppResult", "Locate", "Located", "Outside", "LocateResult"]


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
class ApproximateView:
    """A key whose check reads a fact the language's reader supplies only partly: its address, the fact, what the
    reader misses, and all of it in words."""
    key: str
    fact: str
    note: str
    sentence: str


@dataclass(frozen=True)
class EnforcementView:
    """The state of the check's own enforcement, beside its violations, as the enforcement section shows it: the
    origin of the profile; the files no part governs, and the top folders holding them (each once, in order); the init
    files missing or changed; the skipped tests and dynamic imports; the checks met to the letter only; the findings
    `--strict` fails on; the folders the profile excludes; how the language of the app is named; and the keys whose
    check reads a fact the language supplies only partly, each in words."""
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
    approximate: tuple[ApproximateView, ...] = ()


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
class PartShown:
    """The part claiming a place, or the one a test mirrors: its name, its name as the docs show it (folder), the
    instance of its repeating folder the place is in ("" for none) and the word one instance is called by, and its
    role and litmus test."""
    name: str
    folder: str
    instance: str = ""
    singular: str = ""
    role: str = ""
    litmus: str = ""


@dataclass(frozen=True)
class CoveringTest:
    """The tier that tests a place and where its test lives: the folder below the project root, the file's name (a
    name pattern when the file is not its own, "" when the place is no source file), and the two as one path."""
    tier: TierInfoView
    folder: str
    file: str
    path: str


@dataclass(frozen=True)
class Untested:
    """No tier tests a place, and the profile says why."""
    reason: str


@dataclass(frozen=True)
class InPart:
    """A place in a part: its path below the folder holding the app and whether it is there now; the part; what its
    code may import, as places and in the docs' words; the outside packages it may import (None: not checked); the
    names it may not use; and what tests it: CoveringTest, Untested, or None when no tier does and the profile says
    nothing."""
    kind: ClassVar[str] = "part"
    path: str
    exists: bool
    part: PartShown
    may_import: tuple[ReachView, ...]
    may_import_text: str
    libraries: tuple[str, ...] | None
    forbidden: tuple[str, ...]
    tested: CoveringTest | Untested | None


@dataclass(frozen=True)
class InStructure:
    """A folder of the layout no part claims: its path, whether it is there now, and the parts below it."""
    kind: ClassVar[str] = "structure"
    path: str
    exists: bool
    nearest: tuple[NearestView, ...]


@dataclass(frozen=True)
class Ungoverned:
    """A place in no part and no folder of the layout, below a folder the profile excludes, or outside the app and its
    tests: its path, whether it is there now, the parts near it, whether a file there is a violation (None when no
    part is near), and why it is ungoverned when that is not plain ("" for nothing to say)."""
    kind: ClassVar[str] = "ungoverned"
    path: str
    exists: bool
    nearest: tuple[NearestView, ...]
    closed_tree: bool | None
    note: str


@dataclass(frozen=True)
class InTests:
    """A test file, or the folder of one, below the tests root: its path, whether it is there now; the part it mirrors
    (None: none); what it may import, as places and in the docs' words; the parts it may use as types only; the names
    it may not use; its tier (None: it lies in none); whether it may import the fakes and where they live; the one
    folder it may import test code from; and why it lies in no tier ("" for nothing to say)."""
    kind: ClassVar[str] = "test"
    path: str
    exists: bool
    mirrors: PartShown | None
    may_import: tuple[ReachView, ...]
    may_import_text: str
    types_only: tuple[str, ...]
    forbidden: tuple[str, ...]
    tier: TierInfoView | None
    may_use_fakes: bool
    fakes_path: str
    code_from: str
    note: str


@dataclass(frozen=True)
class Support(InTests):
    """A file below the tests root that is no test, such as a helper: told as a test is."""
    kind: ClassVar[str] = "support"


@dataclass(frozen=True)
class Fake:
    """A test fake: its path, whether it is there now, where the fakes live, the one folder it may import test code
    from, and that it is no test."""
    kind: ClassVar[str] = "fake"
    path: str
    exists: bool
    fakes_path: str
    code_from: str
    note: str


WhereAnswer = InPart | InStructure | Ungoverned | InTests | Fake
"""What a place is and what code there may do, the answer of `xarch where`: one variant per kind of place, each
named by its kind (Support is an InTests)."""


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
    where: WhereAnswer


@dataclass(frozen=True)
class Outside:
    """The path is not in the project; reason is safe to show the user as-is."""
    reason: str


LocateResult = Located | Outside
