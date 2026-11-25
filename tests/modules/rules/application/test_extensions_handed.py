"""Use case: every service that lists the app's files lists them by every ending of the profile's language, so that a
file of the second ending is read as one of the first is."""
from dataclasses import replace
from pathlib import Path

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import PYTHON, profile
from xarch.modules.rules.contract import AskHolds, CheckApp, ReadSources
from xarch.modules.rules.domain.parsed import SourceFile

ENDINGS = (".py", ".pyi")
"""The endings of the profile's language: more than one, so that only the language can have given them."""
LANGUAGE = replace(PYTHON, extensions=ENDINGS)
ROOT, TESTS = Path("/src/app"), Path("/src/tests")
DOMAIN = "modules/docs/domain/x.py"


def tree() -> FakeSourceTree:
    return FakeSourceTree(ROOT, {"kernel/ids.py": [], DOMAIN: []},
                          more={TESTS: {"kernel/test_ids.py": []}, ROOT / "kernel": {"ids.py": []}},
                          parsed={"nothing": SourceFile("", (), ())})


def test_the_check_lists_the_app_and_the_tests_by_every_ending():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).check_app(CheckApp(ROOT, "mine", ROOT.parent, TESTS))
    assert found.listed == [ENDINGS, ENDINGS]


def test_the_holds_question_lists_the_other_files_of_the_app_by_every_ending():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).holds(
        AskHolds("mine", "app", ((DOMAIN, "nothing"),), ROOT))
    assert found.listed == [ENDINGS]


def test_the_sources_of_a_folder_are_listed_by_every_ending():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).sources(
        ReadSources((Path("app/kernel"),), Path("/src"), ROOT, "mine"))
    assert found.listed == [ENDINGS]
