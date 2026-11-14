"""Values of the spec module."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass(frozen=True)
class Configured:
    """A profile name as a project configured it, and the file it came from."""
    name: str
    source: Path


Layout = dict[str, "Layout | None"]    # as skeleton.Tree: a dict is a folder, None a file; the key "*" is every module


EACH = "*"                             # the layout's `each`: the folder every module gets, named by the module
EVERYTHING = "*"                       # the rule target that reaches every place

Scope = Literal["own", "any", "none"]


@dataclass(frozen=True)
class Target:
    """What a part may import: a part, in which module, and optionally only a path below it."""
    part: str                          # a part name, or EVERYTHING
    scope: Scope = "none"              # "own": the importer's module; "any": any module; "none": a part outside the modules
    sub: tuple[str, ...] = ()          # only this path below the part, e.g. ("values",) for domain/values


@dataclass(frozen=True)
class Part:
    """Where code sits: a named path in the layout, with what goes there and how to tell."""
    name: str
    path: tuple[str, ...]              # in the layout; EACH stands for the module name, e.g. ("modules", "*", "domain")
    role: str                          # one line; also the part's note in the docs' tree
    litmus: str = ""
    entry: bool = False                # the entry point, which drives the modules; at most one part is
    driver_proves: str = ""            # the entry point only: what a test of it proves, for testing.md
    driver_test: str | None = None     # the entry point only: the file holding its example test, relative to the file

    @property
    def in_module(self) -> bool:
        return EACH in self.path


@dataclass(frozen=True)
class Example:
    path: tuple[str, ...]              # where the example would live in an app, e.g. ("src", "billing", "service", "charge.py")
    file: str                          # the file holding its code, relative to the architecture file


@dataclass(frozen=True)
class Naming:
    """One row of the docs' naming table: what a kind of thing is called, and where it lives."""
    kind: str                          # e.g. "adapter"
    where: tuple[str, ...]             # the folders it lives in, as the docs show them, e.g. ("adapters/",)
    pattern: str                       # markdown, e.g. "`<System><PortName>`"
    example: tuple[str, ...]           # names, e.g. ("DbDocumentRepo", "ModerationContentReview")


@dataclass(frozen=True)
class Architecture:
    """An architecture as described in an architecture file (format version 1)."""
    name: str
    layout: Layout
    parts: dict[str, Part]
    rules: dict[str, tuple[Target, ...]]   # every part, in the order of parts; a part with no row may import nothing
    docs_template: str | None = None       # relative to the architecture file
    examples: dict[str, Example] = field(default_factory=dict)   # by part
    notes: dict[tuple[str, ...], str] = field(default_factory=dict)   # by layout path: a folder that is not a part
    layers: dict[str, tuple[str, ...]] = field(default_factory=dict)  # named chains of parts, from the inside out
    placement: tuple[str, ...] = ()        # every part once: the order the litmus tests run in
    naming: tuple[Naming, ...] = ()

    @property
    def entry(self) -> Part | None:
        """The entry point: the part marked `entry: true`, if any."""
        return next((part for part in self.parts.values() if part.entry), None)

    def is_file(self, path: tuple[str, ...]) -> bool:
        """Whether a path of the layout, such as a part's, is a file rather than a folder."""
        here: Layout | None = self.layout
        for step in path:
            if here is None or step not in here:
                return False
            here = here[step]
        return here is None

    def module_root(self) -> tuple[str, ...] | None:
        """The folder holding the modules, e.g. ("modules",), or None if the layout has no `each`."""
        return _find_each(self.layout, ())

    def module_tree(self) -> Layout:
        """What every module holds."""
        root = self.module_root()
        if root is None:
            return {}
        folder = self.layout
        for name in root:
            folder = folder[name] or {}
        return folder[EACH] or {}

    def top_level_tree(self) -> Layout:
        """The layout below the app root, with the modules folder empty."""
        return _without_each(self.layout)


def _find_each(tree: Layout, prefix: tuple[str, ...]) -> tuple[str, ...] | None:
    for name, sub in tree.items():
        if name == EACH:
            return prefix
        if sub:
            found = _find_each(sub, prefix + (name,))
            if found is not None:
                return found
    return None


def _without_each(tree: Layout) -> Layout:
    return {name: None if sub is None else _without_each(sub) for name, sub in tree.items() if name != EACH}


@dataclass(frozen=True)
class ArchitectureSource:
    """Where an architecture file is: one bundled with xarch, by name, or a path."""
    location: str                      # a bundled name, e.g. "cli", or a path to a .yaml, .yml or .json file
    bundled: bool


@dataclass(frozen=True)
class ArchitectureDocument:
    """An architecture file as parsed, not yet validated."""
    source: str                        # how problems name the file, e.g. "cli.yaml" or "docs/layered.yaml"
    document: Any                      # whatever the YAML or JSON parser returned
