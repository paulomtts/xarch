"""Use case: a bundled profile is copied into the project as a custom one, with the files it points to, and never over a
file that exists."""
from pathlib import Path

import pytest

from tests.modules.spec.application.builders import spec_controller
from xarch.modules.spec.contract import NewProfile, ProfileCreated, ProfileRefused

ROOT = Path("/p")
APP = ROOT / "app"
MINE = ROOT / "architecture" / "mine"


@pytest.mark.parametrize("given, when, then", [
    pytest.param(set(), NewProfile("mine", "base", APP, ROOT),
                 ProfileCreated(MINE, MINE / "mine.yaml", ("mine.yaml", "docs/a.md", "agents.md"),
                                "architecture/mine/mine.yaml"),
                 id="a copy goes to architecture/<name>/ beside the app folder, with every file it points to"),
    pytest.param(set(), NewProfile("mine", "base", APP, ROOT, Path("/p/elsewhere")),
                 ProfileCreated(Path("/p/elsewhere"), Path("/p/elsewhere/mine.yaml"),
                                ("mine.yaml", "docs/a.md", "agents.md"), "elsewhere/mine.yaml"),
                 id="a copy goes to the folder asked for"),
    pytest.param({MINE / "mine.yaml"}, NewProfile("mine", "base", APP, ROOT),
                 ProfileRefused("/p/architecture/mine/mine.yaml already exists: nothing was written; `new` writes only "
                                "new files, so pass `--out <folder>` to write somewhere else, or choose another name"),
                 id="a copy over a file that exists is refused naming it"),
    pytest.param({MINE / "agents.md", MINE / "docs/a.md"}, NewProfile("mine", "base", APP, ROOT),
                 ProfileRefused("/p/architecture/mine/docs/a.md, /p/architecture/mine/agents.md already exist: nothing "
                                "was written; `new` writes only new files, so pass `--out <folder>` to write somewhere "
                                "else, or choose another name"),
                 id="every file that exists is named"),
    pytest.param(set(), NewProfile("mine", "nope", APP, ROOT), ProfileRefused("unknown profile 'nope': use one of base"),
                 id="a profile that is not bundled is refused with the ones that are"),
    pytest.param(set(), NewProfile("my profile", "base", APP, ROOT),
                 ProfileRefused("'my profile' is not a profile name: use letters, digits, '-' and '_', starting with a "
                                "letter or a digit"),
                 id="a name that cannot name a folder is refused"),
])
def test_new(given, when, then):
    spec, _ = spec_controller(existing=given)
    assert spec.new_profile(when) == then


def test_the_copy_is_named_and_based_on_the_original_and_holds_every_file_as_it_was():
    spec, output = spec_controller()
    spec.new_profile(NewProfile("mine", "base", APP, ROOT))
    assert output.written == {MINE / "mine.yaml": b"# the base\nxarch: 2\nname: mine\nbased_on: base\ntesting: x\n",
                              MINE / "docs/a.md": b"page\n", MINE / "agents.md": b"agents\n"}


def test_nothing_is_written_when_any_file_exists():
    spec, output = spec_controller(existing={MINE / "agents.md"})
    spec.new_profile(NewProfile("mine", "base", APP, ROOT))
    assert output.written == {}


def test_a_copy_that_would_not_load_is_refused_before_anything_is_written():
    broken = {**{"xarch": 2, "name": "base"}, "parts": {"core": {"path": "core"}}}
    spec, output = spec_controller({"base": broken})
    refused = spec.new_profile(NewProfile("mine", "base", APP, ROOT))
    assert isinstance(refused, ProfileRefused) and refused.reason.startswith("base: ")
    assert output.written == {}
