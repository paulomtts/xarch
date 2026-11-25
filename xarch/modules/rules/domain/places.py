"""The values the source rules reason about: a place and what code there may do, the answers of `xarch where`."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from xarch.kernel.placement import Place
from xarch.modules.rules.domain.profile import PartInfo
from xarch.profile_values.placement import Target
from xarch.profile_values.tiers import CheckedTier


@dataclass(frozen=True)
class Resolved:
    """A path settled: which folder it lies in (app, tests or project), its steps below that folder, the path in full,
    whether it exists, and how it is shown: below the folder holding the app, or in full when it lies outside it."""
    within: str
    steps: tuple[str, ...]
    path: Path
    exists: bool
    shown: str


@dataclass(frozen=True)
class Sited:
    """A file where the profile places it, read for a module that reads the app's code: where it lies (one of the
    places of published, IN_PART to NO_PART) and the part it lies in ("" for none)."""
    lies: str
    part: str


@dataclass(frozen=True)
class PartAt:
    """A part as a target names it (the part, its scope, a path below it), how the docs name it, and its folder below
    the project root (a placeholder for an instance that is not fixed, such as <module>): what a place may import, and
    the parts near a place no part claims."""
    target: Target
    folder: str
    path: str


@dataclass(frozen=True)
class PartPlace:
    """A place in a part: the path as resolved; the part claiming it (place: its name, the instance it is in and the
    path below), its words (info) and the word of one instance of its repeating folder (singular); what its code may
    import, as places and in the docs' words; the outside packages it may import (None: not checked) and the names it
    may not use; and the tier that tests it with the folder and the file its test would be in (the file a name
    pattern when it is not its own, empty when the place is no source file), or None when no tier does, and then why
    (untested; "" when the profile does not say)."""
    found: Resolved
    place: Place
    info: PartInfo
    singular: str
    reaches: tuple[PartAt, ...]
    may_import_text: str
    libraries: tuple[str, ...] | None
    uses_never: tuple[str, ...]
    tier: CheckedTier | None
    test_folder: str
    test_file: str
    untested: str


@dataclass(frozen=True)
class StructurePlace:
    """A folder of the layout no part claims: the path as resolved, and the parts below it."""
    found: Resolved
    nearest: tuple[PartAt, ...]


@dataclass(frozen=True)
class UngovernedPlace:
    """A place in no part and no folder of the layout, below a folder the profile excludes, or outside the app and its
    tests: the path as resolved; the parts near it (none when it is excluded or outside the app); whether a file there
    is a violation (None when no part is near, so that the closed-tree guard has nothing to say); and why it is
    ungoverned when that is not plain."""
    found: Resolved
    nearest: tuple[PartAt, ...]
    closed_tree: bool | None
    note: str


@dataclass(frozen=True)
class SuitePlace:
    """A file or folder below the tests root that is no fake: the path as resolved; whether it is a test (else a
    helper or other support); the tier it lies in (None: none), the part it mirrors (place, with its words and the
    word of one instance of its folder, None when it mirrors none) and what it may import, as places and in the docs'
    words; the names it may not use; whether it may import the fakes and where they live; the one folder it may
    import test code from; note, why it is in no tier, for a test; and the shared test code it may import besides
    (testing.shared), each a folder ending in / or a file, from the project root."""
    found: Resolved
    test: bool
    tier: CheckedTier | None
    place: Place | None
    info: PartInfo | None
    singular: str
    reaches: tuple[PartAt, ...]
    may_import_text: str
    uses_never: tuple[str, ...]
    may_use_fakes: bool
    fakes_path: str
    test_code_from: str
    note: str
    shared: tuple[str, ...] = ()


@dataclass(frozen=True)
class FakePlace:
    """A test fake: the path as resolved, where the fakes live, the one folder it may import test code from, and that
    it is no test."""
    found: Resolved
    fakes_path: str
    test_code_from: str
    note: str


Placed = PartPlace | StructurePlace | UngovernedPlace | SuitePlace | FakePlace
"""What a place is and what code there may do, the answer of `xarch where`, one variant per kind of place."""
