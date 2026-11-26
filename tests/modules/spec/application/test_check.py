"""Use case: validate a profile without an app: whether it loads (and so whether every file it points to is there),
whether its examples keep to its own rules, and how it differs from the bundled profile it is based on. The checks
the profile writes itself are held to their examples by rules, which asks spec for the rest."""
from pathlib import Path

import pytest

from tests.fakes.settings import FakeSettings
from tests.modules.spec.application.builders import BASE, spec_controller
from xarch.kernel.source import Import
from xarch.modules.spec.contract import CheckProfile, NoProfileChosen, Origin, Problem, ProfileChecked, ProfileRefused
from xarch.modules.spec.domain.values import Configured

APP = Path("/p/app")
MINE = {**BASE, "name": "mine", "based_on": "base"}
WITH_EXAMPLE = {**MINE, "docs": {"examples": ["ex"]}}
WITH_EXAMPLE_FILES = {"ex/core/rule.py": "from app.api import handler\n", "ex/api/handler.py": "X = 1\n"}
WITH_EXAMPLE_READS = {"from app.api import handler\n": (Import(1, ("app", "api"), ("handler",)),)}
OFF = ("package-only", "scenario-coverage", "no-comments", "stand-ins", "closed-tree", "no-duplicates", "no-twins",
       "dead-code", "pass-through", "no-callbacks", "private-imports")
SELF = (("parts", 2, 2), ("part_keys", 3, 3), ("tiers", 0, 0), ("guards", 0, 0), ("profile", 2, 2))
"""The counts of base against itself: everything check reads under it has a counterpart."""
COPY = Origin("mine.yaml", False, "base", OFF, OFF, (), "based_on", 1.0, False, SELF, anchor="base")
"""The origin of a copy of base that says it is based on it."""


@pytest.mark.parametrize("given, when, then", [
    pytest.param(dict(files={"mine.yaml": MINE}), CheckProfile(APP, "mine.yaml"),
                 ProfileChecked("mine.yaml", (), 2, COPY),
                 id="a profile that loads and keeps to its rules is valid, with how many files it points to"),
    pytest.param(dict(files={"mine.yaml": {**MINE, "colour": 1, "parts": {"core/": {"litmus": "q"}}}}),
                 CheckProfile(APP, "mine.yaml"),
                 ProfileChecked("mine.yaml", (
                     Problem("load", "mine.yaml: unknown key 'colour': use based_on, checks, counterparts, docs, evals, "
                                     "excluded, fakes, files, guards, hints, language, layers, name, never, parts, "
                                     "reserved, review, structure, testing, tiers"),
                     Problem("load", "mine.yaml: parts.core: missing `role`")), 0, None),
                 id="a profile that does not load has every problem reported at once"),
    pytest.param(dict(files={"mine.yaml": WITH_EXAMPLE}, texts=WITH_EXAMPLE_FILES, reads=WITH_EXAMPLE_READS),
                 CheckProfile(APP, "mine.yaml"),
                 ProfileChecked("mine.yaml", (
                     Problem("examples", "example (core/rule.py): imports app.api which core may not import "
                                         "(parts.core.imports.may)"),), 3, COPY),
                 id="an example that imports what its part may not is a problem"),
    pytest.param(dict(files={}), CheckProfile(APP, "gone.yaml"),
                 ProfileChecked("gone.yaml", (Problem("load", "gone.yaml: cannot read the file: no such file"),), 0, None),
                 id="a path that holds no file is a problem of the profile"),
    pytest.param(dict(), CheckProfile(APP, None),
                 NoProfileChosen(("base",)),
                 id="with no profile named and none configured nothing is chosen"),
    pytest.param(dict(), CheckProfile(APP, "nope"), ProfileRefused("unknown profile 'nope': use one of base"),
                 id="a name that is not a bundled profile is refused with the ones that are"),
])
def test_check_profile(given, when, then):
    spec, _ = spec_controller(**given)
    assert spec.check_profile(when) == then


def test_with_no_profile_named_the_one_configured_for_the_project_is_checked():
    settings = FakeSettings(Configured("mine.yaml", Path("/p/pyproject.toml")))
    spec, _ = spec_controller(files={"/p/mine.yaml": MINE}, settings=settings)
    checked = spec.check_profile(CheckProfile(APP, None))
    assert isinstance(checked, ProfileChecked) and checked.ok and checked.location == "/p/mine.yaml"


def test_a_bundled_profile_is_valid_and_is_compared_with_nothing():
    spec, _ = spec_controller()
    checked = spec.check_profile(CheckProfile(APP, "base"))
    assert isinstance(checked, ProfileChecked) and checked.ok and checked.origin.bundled


THEIRS = {**BASE, "name": "theirs"}
"""A copy of base at a path, for --against to name."""


def test_with_against_the_profile_checked_is_compared_with_the_one_it_names():
    spec, _ = spec_controller(files={"mine.yaml": MINE, "theirs.yaml": THEIRS})
    checked = spec.check_profile(CheckProfile(APP, "mine.yaml", "theirs.yaml"))
    assert isinstance(checked, ProfileChecked) and checked.origin is not None
    assert (checked.problems, checked.origin.compared, checked.origin.chosen_by, checked.origin.based_on) == (
        (), "theirs.yaml", "against", "base")


def test_against_a_profile_with_several_problems_is_refused_with_all_of_them_on_one_line():
    broken = {**MINE, "colour": 1, "parts": {"core/": {"litmus": "q"}}}
    spec, _ = spec_controller(files={"mine.yaml": MINE, "broken.yaml": broken})
    assert spec.check_profile(CheckProfile(APP, "mine.yaml", "broken.yaml")) == ProfileRefused(
        "--against does not load: broken.yaml: unknown key 'colour': use based_on, checks, counterparts, docs, evals, excluded, "
        "fakes, files, guards, hints, language, layers, name, never, parts, reserved, review, structure, testing, tiers; "
        "broken.yaml: parts.core: missing `role`")


def test_against_is_not_read_when_the_profile_checked_does_not_load():
    spec, _ = spec_controller(files={})
    assert spec.check_profile(CheckProfile(APP, "gone.yaml", "nosuch")) == ProfileChecked(
        "gone.yaml", (Problem("load", "gone.yaml: cannot read the file: no such file"),), 0, None)
