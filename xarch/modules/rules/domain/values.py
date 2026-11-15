"""The values the source rules reason about: the profile as the checker sees it, and already-parsed source files."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.logic.placement import Target


@dataclass(frozen=True)
class TestTier:
    """A kind of test as the checker sees it.

    subject holds the parts it tests, each as a target: a part inside the modules in the test's own module. folder is
    the folder of its example test below the tests root, which places the tests of a tier whose folder mirrors no part.
    """
    name: str
    subject: tuple[Target, ...]
    folder: tuple[str, ...] | None = None


@dataclass(frozen=True)
class Fakes:
    """Where the test fakes live below the tests root, and the parts they stand in for."""
    path: tuple[str, ...]
    stand_in_for: tuple[str, ...]


@dataclass(frozen=True)
class Scenarios:
    """The scenario-coverage guard: the part holding the result unions, the tier holding their scenarios, and how a
    union's name ends."""
    results: str
    tier: str
    suffix: str


@dataclass(frozen=True)
class Profile:
    """The architecture in force, in the checker's terms.

    parts maps each part to its path pattern, and rules to what it may import. folders holds every folder of the
    layout as a pattern: those no part claims are structure, the package files that hold the tree together. libraries
    is None when outside packages are not checked. each_root is the folder holding the instances of the layout's
    `each` folder. package_only, scenarios and no_comments are the guards switched on.
    """
    parts: dict[str, tuple[str, ...]]
    rules: dict[str, tuple[Target, ...]]
    folders: tuple[tuple[str, ...], ...] = ()
    tiers: tuple[TestTier, ...] = ()
    libraries: dict[str, tuple[str, ...]] | None = None
    fakes: Fakes | None = None
    each_root: tuple[str, ...] | None = None
    package_only: tuple[str, ...] = ()
    scenarios: Scenarios | None = None
    no_comments: bool = False


@dataclass(frozen=True)
class Import:
    """One imported name as written. names is None for `import a.b`, the imported names for `from a import x`."""
    line: int
    module: tuple[str, ...]
    level: int = 0
    names: tuple[str, ...] | None = None


@dataclass(frozen=True)
class Comment:
    """A `#` comment as written, and the line it is on."""
    line: int
    text: str


@dataclass(frozen=True)
class Union:
    """A module-level `Name = A | B | ...` of plain names, and the line it is on."""
    line: int
    name: str
    members: tuple[str, ...]


@dataclass(frozen=True)
class SourceFile:
    """A Python file as parsed, never run: how it is shown (e.g. "app/kernel/x.py"), its path below the root, what
    it imports, its comments, its module docstring, the names of its functions (at module level and in its
    classes) and its unions. error is how it fails to parse, as (line, message), and then it holds nothing else."""
    name: str
    path: tuple[str, ...]
    imports: tuple[Import, ...]
    comments: tuple[Comment, ...] = ()
    docstring: str | None = None
    functions: tuple[str, ...] = ()
    unions: tuple[Union, ...] = ()
    error: tuple[int, str] | None = None
