"""Use case: every service that reads the app's code hands the reader how the profile's language starts a private
name, so that a name is public or not as `check` reads it; the reading of a text for spec, which has no profile, hands
none, so that every name of it reads public."""
from dataclasses import replace
from pathlib import Path

from tests.fakes.filesystem import FakeSourceTree
from tests.fakes.profiles import FakeProfiles
from tests.modules.rules.application.helpers import controller
from tests.modules.rules.builders import PYTHON, profile
from xarch.modules.rules.application.controller import ReaderController
from xarch.modules.rules.application.services.source_reading import SourceReadService
from xarch.modules.rules.contract import AskHolds, CheckApp, CheckProfile, KeepFacts, ReadSources, Resemblance, Reviewed
from xarch.modules.rules.domain.parsed import Class, SourceFile
from xarch.modules.rules.domain.profile import Asked
from xarch.profile_values.checks import APP, Quantified, Saying, Scope, WrittenCheck, WrittenTarget

PREFIX = "~"
"""How the profile's language starts a private name: not Python's, so that only the profile can have given it."""
LANGUAGE = replace(PYTHON, private=PREFIX)
ROOT, TESTS = Path("/src/app"), Path("/src/tests")
DOMAIN = "modules/docs/domain/x.py"
PARSED = {"manager": SourceFile("", (), (), classes=(Class(1, "Manager"),)), "nothing": SourceFile("", (), ())}


def tree() -> FakeSourceTree:
    return FakeSourceTree(ROOT, {"kernel/ids.py": [], DOMAIN: []}, more={TESTS: {"kernel/test_ids.py": []}},
                          parsed=PARSED)


def test_the_check_hands_it_for_the_app_and_for_the_tests():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).check_app(CheckApp(ROOT, "mine", ROOT.parent, TESTS))
    assert found.prefixes == [PREFIX, PREFIX]


def test_the_holds_question_hands_it_for_the_files_given_and_for_the_other_files_of_the_app():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).holds(
        AskHolds("mine", "app", ((DOMAIN, "nothing"),), ROOT))
    assert found.prefixes == [PREFIX, PREFIX]


def test_the_sources_read_for_a_module_that_reads_the_app_s_code_hand_it():
    found = tree()
    controller(found, FakeProfiles({"mine": profile(language=LANGUAGE)})).sources(
        ReadSources((Path("app/kernel/ids.py"),), Path("/src"), ROOT, "mine"))
    assert found.prefixes == [PREFIX]


def test_an_eval_s_facts_are_read_with_it():
    found = tree()
    evals = profile(asked={"rule": Asked("file", Scope(APP, "domain"))}, language=LANGUAGE)
    controller(found, FakeProfiles({"mine": evals})).kept(KeepFacts("mine", "app", "rule", ((DOMAIN, "nothing"),)))
    assert found.prefixes == [PREFIX]


def test_the_examples_of_a_profile_s_own_checks_and_evals_are_read_with_it():
    found = tree()
    checks = {"no-managers": WrittenCheck(("class",), Scope(APP, "domain"), Quantified("may_not", (WrittenTarget("exist"),)),
                                          (Saying("{name}", "rename it"),), flagged=((DOMAIN, "manager"),),
                                          clean=((DOMAIN, "nothing"),))}
    evals = {"rule": Asked("class", Scope(APP, "domain"), (), ((DOMAIN, "manager"),), ((DOMAIN, "manager"),))}
    reviewed = {"mine": Reviewed("mine", (), 2, Resemblance(False, "cli"))}
    owned = profile(written=checks, asked=evals, language=LANGUAGE)
    controller(found, FakeProfiles({"mine": owned}, reviewed=reviewed)).check_profile(CheckProfile(Path("/p/app"), "mine"))
    assert found.prefixes == [PREFIX, PREFIX, PREFIX, PREFIX]


def test_a_text_read_for_spec_hands_none_since_no_profile_says_it():
    found = tree()
    reader = ReaderController(SourceReadService(found))
    reader.imports("nothing")
    reader.comments("nothing")
    assert found.prefixes == ["", ""]
