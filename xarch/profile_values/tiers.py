"""A kind of test as the checks read it."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.placement import Target


@dataclass(frozen=True)
class CheckedTier:
    """One kind of test as a check reads it: its name; the parts it tests, each as a target (in its own instance for a
    part of a repeating folder); the folder below the tests root of tests that mirror no part (an empty folder places
    nothing); the parts its tests may use as types only; whether its tests keep to the forbidden list of the part they
    mirror; its words (proves, may_touch, litmus, one_file_per), which `where` shows; what the tests of its folder may
    import of the app (None: no folder, and the tests import what the part they mirror may); the parts one of which
    each of its test files must reach; and whether every table test of it holds no branch in its body."""
    name: str
    subject: tuple[Target, ...]
    folder: tuple[str, ...] | None = None
    types_only: tuple[str, ...] = ()
    forbidden: bool = False
    proves: str = ""
    may_touch: str = ""
    litmus: str = ""
    one_file_per: str = ""
    may_import: tuple[Target, ...] | None = None
    must_import: tuple[str, ...] = ()
    plain_tables: bool = False
