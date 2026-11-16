"""What the rules module promises: check the imports below a root folder against section 5."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

from xarch.kernel.logic.origin import Origin
from xarch.kernel.violations import At, Violation, Weak

__all__ = ["ChecksCannotRun", "OwnCheckView",
           "DriftView", "FindingView", "ExcludedView", "EnforcementView", "ReachView", "NearestView", "TierInfoView",
           "PartShown", "CoveringTest", "Untested", "InPart", "InStructure", "Ungoverned", "InTests", "Support", "Fake",
           "WhereAnswer", "CheckImports", "ImportsChecked", "NotADirectory", "CheckResult", "CheckApp", "AppChecked",
           "CheckAppResult", "Locate", "Located", "Outside", "LocateResult", "CATEGORIES", "ExplainWords", "SlotShown",
           "WordLine", "CategoryShown", "ChecksShown", "WordsShown", "FieldShown", "WordShown", "UnknownWords",
           "WordsResult", "ExplainRule", "RuleShown", "KeyUnset", "NoRuleShown", "RuleResult", "CheckExamples", "ExamplesChecked"]


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
class OwnCheckView:
    """A check the profile writes itself: its id, how many facts it read in the project (none: it passes for want of
    anything to check), and that in words."""
    id: str
    read: int
    said: str


@dataclass(frozen=True)
class EnforcementView:
    """The state of the check's own enforcement, beside its violations, as the enforcement section shows it: the
    origin of the profile; the files no part governs, and the top folders holding them (each once, in order); the init
    files missing or changed; the skipped tests and dynamic imports; the checks met to the letter only; the findings
    `--strict` fails on; the folders the profile excludes; how the language of the app is named; the keys whose
    check reads a fact the language supplies only partly, each in words; and the checks the profile writes itself,
    each with how many facts it read in the project."""
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
    checks: tuple[OwnCheckView, ...] = ()


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
    architecture at profile (a bundled name or a path); root and tests are given in full."""
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


@dataclass(frozen=True)
class ChecksCannotRun:
    """The checks the profile writes itself cannot run: every problem, each at its address in the profile."""
    problems: tuple[str, ...]


CheckResult = ImportsChecked | NotADirectory | ChecksCannotRun


@dataclass(frozen=True)
class CheckApp:
    """Check the app below root, its imports and its structure, and the tests below tests (None: no tests), against
    the architecture at profile (a bundled name or a path); strict also fails on the enforcement's findings. cwd is the
    working folder, in full, that a relative root or tests folder is read from."""
    root: Path
    profile: str
    cwd: Path
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


CheckAppResult = AppChecked | NotADirectory | ChecksCannotRun


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


LocateResult = Located | Outside | ChecksCannotRun


CATEGORIES = ("checks", "kinds", "quantifiers", "targets", "filters", "variables")
"""The first steps of the addresses `explain` answers with the words a check is written in: how a check is written,
and each category of its words."""


@dataclass(frozen=True)
class ExplainWords:
    """Explain how a check is written (`checks`), a category of its words (`filters`), or one word (`filters.public`);
    an example is a rule of the first of the profiles named (a bundled name or a path) that is written with the word."""
    address: str
    examples_from: tuple[str, ...] = ()


@dataclass(frozen=True)
class SlotShown:
    """A slot of a check: its name, what it is for, what it accepts."""
    name: str
    meaning: str
    accepts: str


@dataclass(frozen=True)
class WordLine:
    """A word in a line: its name and what it means."""
    name: str
    meaning: str


@dataclass(frozen=True)
class CategoryShown:
    """A category of words: its address, what it holds, and its words."""
    name: str
    meaning: str
    words: tuple[WordLine, ...]


@dataclass(frozen=True)
class ChecksShown:
    """How a check is written and read: the sentence it reads as, its slots, the categories of its words, and one
    whole check of a profile, as an example, with the key and the profile it comes from."""
    reading: str
    slots: tuple[SlotShown, ...]
    categories: tuple[CategoryShown, ...]
    example_key: str
    example_profile: str
    example: str


@dataclass(frozen=True)
class WordsShown:
    """A category of words, each in a line."""
    category: CategoryShown


@dataclass(frozen=True)
class FieldShown:
    """A field a kind of fact carries: its name, what it is, and the filter that must hold for a fact to carry it
    ("" when it always does)."""
    name: str
    meaning: str
    when: str


@dataclass(frozen=True)
class WordShown:
    """One word: its address, category, name and meaning; what it is about (a filter: the file, the fact or what the
    fact reaches); the kinds of fact it applies to; the side of the files it applies to ("" both); what its value is
    ("" none); for a kind, its fields, the facts of the source it needs and its verb; and an example, a whole check
    written with the word, with the key and the profile it comes from ("" when none of them has one)."""
    address: str
    category: str
    name: str
    meaning: str
    about: str = ""
    applies_to: tuple[str, ...] = ()
    side: str = ""
    value: str = ""
    fields: tuple[FieldShown, ...] = ()
    needs: tuple[str, ...] = ()
    verb: str = ""
    example_key: str = ""
    example_profile: str = ""
    example: str = ""


@dataclass(frozen=True)
class UnknownWords:
    """An address of no word: what was typed and the nearest addresses."""
    typed: str
    nearest: tuple[str, ...]


WordsResult = ChecksShown | WordsShown | WordShown | UnknownWords


@dataclass(frozen=True)
class ExplainRule:
    """The rules a key of the profile at location expands to (parts.names: of every part), as a profile would write
    them as checks of its own."""
    address: str
    profile: str


@dataclass(frozen=True)
class RuleShown:
    """The rules a key expands to in a profile, written as checks, and how many."""
    address: str
    profile: str
    text: str
    count: int


@dataclass(frozen=True)
class KeyUnset:
    """A key the engine expands to rules when a profile sets it, which that profile sets nowhere."""
    address: str
    profile: str


@dataclass(frozen=True)
class NoRuleShown:
    """A key that expands to no rule in that profile, and why (the profile does not set it, it is checked by a check
    of its own, or the profile cannot be read)."""
    address: str
    profile: str
    reason: str


RuleResult = RuleShown | KeyUnset | NoRuleShown


@dataclass(frozen=True)
class CheckExamples:
    """Hold the checks the profile at location writes itself to their examples, the app being the package app
    names."""
    profile: str
    app: str


@dataclass(frozen=True)
class ExamplesChecked:
    """What holding a profile's own checks to their examples found: every problem, each at its address in the
    profile (none: each check finds something in its flagged code and nothing in its clean code), and how many checks
    the profile writes itself."""
    problems: tuple[str, ...]
    checks: int
