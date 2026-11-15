"""The facts of a run, read once from hand-made parsed files: each file placed once, and what it says by kind, with
the facts derived over the whole app (a build of a class of the app, a reference to a function of the app)."""
from tests.modules.rules.builders import PROFILE, imp, in_tests, source
from xarch.kernel.logic.placement import Place
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.domain.rule import Fact
from xarch.modules.rules.domain.values import Call, Class, MethodCall, Use

DOC = ("app", "modules", "docs", "domain", "doc", "Doc")
APP = [source("modules/docs/domain/doc.py", classes=(Class(1, "Doc"),), module_functions=("make",)),
       source("modules/docs/application/services/publish.py", imp(1, "app.modules.docs.domain", "doc"),
              imp(2, "yaml", "load"), imp(3, "", "values", up=0),
              calls=(Call(5, DOC), Call(6, ("yaml", "load"))),
              uses=(Use(7, ("app", "modules", "docs", "domain", "doc", "make", "cache"), 2),),
              method_calls=(MethodCall(8, "resolve", held=True),)),
       source("scripts/seed.py")]
TESTS = [in_tests("modules/docs/domain/test_doc.py", imp(1, "app.modules.docs.domain", "doc"),
                  imp(2, "", "builders", up=0), imp(3, "tests.fakes", "repo")),
         in_tests("fakes/repo.py")]
FACTS = facts_of(APP, TESTS, PROFILE, "app", "tests")
SERVICE, TEST = FACTS.files[1], FACTS.files[3]


def test_each_file_is_placed_once_the_apps_by_its_part_and_a_test_by_its_tier_and_what_it_mirrors():
    assert [(r.file.name, r.place, r.tier, r.mirrors) for r in FACTS.files] == [
        ("app/modules/docs/domain/doc.py", Place("domain", "docs", ("doc",)), "", ()),
        ("app/modules/docs/application/services/publish.py", Place("services", "docs", ("publish",)), "", ()),
        ("app/scripts/seed.py", None, "", ()),
        ("tests/modules/docs/domain/test_doc.py", None, "unit", ("domain",)),
        ("tests/fakes/repo.py", None, "", ())]
    assert (TEST.is_test, FACTS.files[4].is_fake, FACTS.test_files) == (
        True, True, frozenset({("modules", "docs", "domain", "test_doc")}))


def test_an_import_is_a_fact_as_written_and_one_per_name_it_takes():
    assert [(f.path, f.traits) for f in SERVICE.facts["import"]] == [
        (("app", "modules", "docs", "domain"), frozenset()), (("yaml",), frozenset()),
        ((), frozenset({"relative"}))]
    assert [(f.path, f.name) for f in SERVICE.facts["imported"]] == [
        (("app", "modules", "docs", "domain", "doc"), "doc"), (("yaml", "load"), "load"), (("values",), "values")]


def test_an_import_into_the_app_is_an_edge_to_the_file_it_reaches_and_where_that_sits_or_to_a_package_and_a_name():
    assert [(f.target, f.name, f.at) for f in SERVICE.facts["edge"]] == [
        (("modules", "docs", "domain", "doc"), None, Place("domain", "docs", ("doc",))),
        (("modules", "docs", "application", "services"), "values", Place("services", "docs"))]
    assert [f.target for f in TEST.facts["edge"]] == [("modules", "docs", "domain", "doc")]
    assert [f.target for f in TEST.facts["suite_edge"]] == [("modules", "docs", "domain"), ("fakes", "repo")]


def test_a_call_of_a_class_of_the_app_is_a_build_and_a_use_of_one_of_its_functions_a_reference():
    assert SERVICE.facts["build"] == (Fact("build", 5, DOC, at=Place("domain", "docs", ("doc",))),)
    assert SERVICE.facts["reference"] == (
        Fact("reference", 7, ("app", "modules", "docs", "domain", "doc", "make", "cache"),
             target=("modules", "docs", "domain", "doc", "make"), at=Place("domain", "docs", ("doc",))),)
    assert [f.at for f in SERVICE.facts["call"]] == [Place("domain", "docs", ("doc", "Doc")), None]


def test_a_method_call_on_what_the_object_holds_says_so():
    assert SERVICE.facts["method"] == (Fact("method", 8, name="resolve", traits=frozenset({"held"})),)
