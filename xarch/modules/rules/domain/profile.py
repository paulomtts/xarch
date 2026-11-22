"""The values the source rules reason about: the profile as the checker sees it."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from xarch.kernel.logic.placement import repeat_of
from xarch.profile_values.capabilities import Shortfall
from xarch.profile_values.checks import Condition, Scope, WrittenCheck
from xarch.profile_values.excluded import Excluded
from xarch.profile_values.language import CheckedLanguage
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import Fakes, Framework, ScenarioCoverage, StandIns
from xarch.profile_values.tiers import CheckedTier

if TYPE_CHECKING:
    from xarch.modules.rules.domain.rule import OwnCheck


@dataclass(frozen=True)
class PartInfo:
    """What the profile says of a part in words: its role and litmus test, its name as the docs show it (a path below
    the instance for an instance's part, ending in `/` for a folder) and, for a part no tier tests, why."""
    role: str = ""
    litmus: str = ""
    shown: str = ""
    untested: str = ""


@dataclass(frozen=True)
class Asked:
    """An eval of the profile's own, as rules reads it: the kind of fact one question is asked of, the files it is
    asked in, the filters a fact must pass, in the words of the vocabulary, and its examples, the files of a small
    project it must read as flagged and of one it must read as clean, each by its path below the app with its code."""
    reads: str
    within: Scope
    keep: tuple[Condition, ...] = ()
    flagged: tuple[tuple[str, str], ...] = ()
    clean: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Profile:
    """The architecture in force, in the checker's terms.

    parts maps each part to its path pattern, and rules to what it may import. folders holds every folder of the
    layout as a pattern: those no part claims are structure, the package files that hold the tree together. libraries
    is None when outside packages are not checked. repeats are the repeating folders of the layout, each its word and
    the folder holding its instances. framework names the test files and functions; None: no file is a test.
    package_only, scenarios, no_comments, stand_ins and closed_tree are the guards switched on (None or False: off).
    uses_never holds, by part, the dotted names and modules a part may not use, and the methods it may not call on
    anything, each as ("", "<name>()"). info says each part in words. excluded
    holds the folders below the app that are not its source: no check reads a file below one. must_import holds, by
    part, the targets each of its files must import one of (or an outside package); no_duplicates is the fewest
    statements a function needs to count as a duplicate (None: off); no_twins the fewest fields a class needs to count
    as a twin of another (None: off), no_twins_renamed the fewest a renamed copy needs, no_twins_subset the fewest a copy
    of part of another's fields needs (None: that case is off; see twins), no_twins_translated the parts whose files
    translate one of a pair into the other, which is then no twin; dead_code switches the unused ports and fakes
    check on; pass_through lists the parts whose methods that only forward are listed (empty: off). untested lists,
    with dead_code, the files of a tiered part no test of its tier reaches; tests_only, with dead_code, the public names
    of the app no other file of the app names, but those tests_only_known accepts, each `<file below the app>:<name>`.
    holds says, by part, what its files define
    ("classes" or "functions"); immutable the parts every class of which, but an exception, is an immutable record;
    types_only, by part, the parts it may use as types only; no_callbacks the parts whose
    code calls none of its own parameters; names, by part, the patterns its public classes match one of; built_by, by
    part, the parts that alone may build its classes; shared, by part, the fewest users each public name of a part
    declared shared must have (see shared); private_imports switches the private-imports guard on. hints
    holds the profile's own advice, by rule id. language is the language of the app. reserved holds the
    standard-library modules (by top-level name, each with why) a part imports only when its libraries list them.
    approximate holds the keys whose check reads a fact the language supplies only partly. written are the checks the
    profile writes itself, by id, as spec read them; checks are those checks made into rules, in the profile's order
    (none until they are made, see own_checks). default_tests is the folder the tests go in, from the folder holding
    the app, when no tests folder is given or there: not a value a profile sets, but the convention spec publishes, the
    same for every profile; it is also the first step of the path of an example's test file. asked are the evals the
    profile writes itself, by id, as rules reads them (see Asked), which no check runs.
    """
    parts: dict[str, tuple[str, ...]]
    rules: dict[str, tuple[Target, ...]]
    folders: tuple[tuple[str, ...], ...] = ()
    tiers: tuple[CheckedTier, ...] = ()
    libraries: dict[str, tuple[str, ...]] | None = None
    fakes: Fakes | None = None
    repeats: tuple[Repeat, ...] = ()
    package_only: tuple[str, ...] = ()
    scenarios: ScenarioCoverage | None = None
    no_comments: bool = False
    stand_ins: StandIns | None = None
    closed_tree: bool = False
    framework: Framework | None = None
    uses_never: dict[str, tuple[tuple[str, ...], ...]] = field(default_factory=dict)
    info: dict[str, PartInfo] = field(default_factory=dict)
    excluded: tuple[Excluded, ...] = ()
    must_import: dict[str, tuple[Target, ...]] = field(default_factory=dict)
    no_duplicates: int | None = None
    no_twins: int | None = None
    no_twins_renamed: int | None = None
    no_twins_subset: int | None = None
    no_twins_translated: tuple[str, ...] = ()
    dead_code: bool = False
    pass_through: tuple[str, ...] = ()
    untested: bool = False
    tests_only: bool = False
    tests_only_known: tuple[str, ...] = ()
    holds: dict[str, str] = field(default_factory=dict)
    immutable: tuple[str, ...] = ()
    types_only: dict[str, tuple[str, ...]] = field(default_factory=dict)
    no_callbacks: tuple[str, ...] = ()
    names: dict[str, tuple[str, ...]] = field(default_factory=dict)
    built_by: dict[str, tuple[str, ...]] = field(default_factory=dict)
    shared: dict[str, int] = field(default_factory=dict)
    private_imports: bool = False
    hints: dict[str, str] = field(default_factory=dict)
    language: CheckedLanguage = CheckedLanguage()
    reserved: dict[str, str] = field(default_factory=dict)
    approximate: tuple[Shortfall, ...] = ()
    written: dict[str, WrittenCheck] = field(default_factory=dict)
    checks: tuple[OwnCheck, ...] = ()
    default_tests: str = ""
    asked: dict[str, Asked] = field(default_factory=dict)

    def words(self) -> dict[str, str]:
        """The word of the repeating folder each part lies in; a part outside every one has none."""
        return {name: repeat.word for name, pattern in self.parts.items()
                if (repeat := repeat_of(self.repeats, pattern)) is not None}
