"""The facts of a run, read once from hand-made parsed files: each file placed once, and what it says by kind, with
the facts derived over the whole app (a construction of a class of the app, a reference to a function of the app);
and, for the rules given, only the kinds they read."""
from dataclasses import replace

import pytest

from tests.modules.rules.builders import BRACE, PERCENT, PROFILE, imp, in_tests, profile, source
from xarch.kernel.placement import Place
from xarch.kernel.source import Unparsable
from xarch.modules.rules.application.logic.facts import KINDS, facts_of
from xarch.modules.rules.domain.parsed import Call, Callback, Class, Comment, Function, Method, MethodCall, SoleCall, SourceFile, Use
from xarch.modules.rules.domain.rule import EXISTING, MAY_NOT, MUST_BE_REACHED, MUST_REACH, Fact, Match, Rule
from xarch.modules.rules.domain.vocabulary import KINDS as VOCABULARY
from xarch.profile_values.checks import APP, TESTS, Condition, Saying, Scope

DOC = ("app", "modules", "docs", "domain", "doc", "Doc")
MAKE = ("app", "modules", "docs", "domain", "doc", "make")
APP_FILES = [
    source("modules/docs/domain/doc.py", classes=(Class(1, "Doc", named=frozenset({"Repo"})),
                                                  Class(9, "Shown", methods=(Method(10, "__repr__", "str"),))),
           module_functions=("make",), comments=(Comment(3, "# a note"),),
           functions=(Function(4, "make", returns_named=frozenset({"Shown"})),
                      Function(6, "get", owner="Doc", forwards="self.repo.get", sole_call=SoleCall(
                          ("self", "repo", "get"), then=("name",)))),
           callbacks=(Callback(7, "make", "check", annotated=True),), named=frozenset({"Doc", "make"})),
    source("modules/docs/application/services/publish.py", imp(1, "app.modules.docs.domain", "doc"),
           imp(2, "yaml", "load"), imp(3, "", "values", up=0),
           calls=(Call(5, DOC), Call(6, ("yaml", "load")), Call(7, MAKE)),
           uses=(Use(7, MAKE, 2), Use(8, (*MAKE, "cache"), 2)),
           method_calls=(MethodCall(8, "resolve", held=True),)),
    source("scripts/seed.py"),
    SourceFile("app/kernel/broken.py", ("kernel", "broken.py"), (), error=Unparsable(2, "invalid syntax"))]
TEST_FILES = [in_tests("modules/docs/domain/test_doc.py", imp(1, "app.modules.docs.domain", "doc"),
                       imp(2, "", "builders", up=0), imp(3, "tests.fakes", "repo")),
              in_tests("fakes/repo.py")]
FACTS = facts_of(APP_FILES, TEST_FILES, PROFILE, "app", "tests")
DOMAIN, SERVICE, BROKEN, TEST = FACTS.files[0], FACTS.files[1], FACTS.files[3], FACTS.files[4]


def test_each_file_is_placed_once_the_apps_by_its_part_and_the_tier_that_tests_it_and_a_test_by_its_tier():
    assert [(r.file.name, r.place, r.tier, r.mirrors) for r in FACTS.files] == [
        ("app/modules/docs/domain/doc.py", Place("domain", "docs", ("doc",)), "unit", ()),
        ("app/modules/docs/application/services/publish.py", Place("services", "docs", ("publish",)),
         "integration", ()),
        ("app/scripts/seed.py", None, "", ()),
        ("app/kernel/broken.py", Place("kernel", None, ("broken",)), "unit", ()),
        ("tests/modules/docs/domain/test_doc.py", None, "unit", ("domain",)),
        ("tests/fakes/repo.py", None, "", ())]
    assert (TEST.is_test, FACTS.files[5].is_fake, FACTS.test_files) == (
        True, True, frozenset({("modules", "docs", "domain", "test_doc")}))


def test_the_kinds_are_those_of_the_vocabulary_in_its_order():
    assert KINDS == tuple(kind.name for kind in VOCABULARY)


def test_an_import_is_a_fact_as_written_and_one_per_name_it_takes():
    assert [(f.path, f.traits, f.text) for f in SERVICE.facts["import"]] == [
        (("app", "modules", "docs", "domain"), frozenset(), "app.modules.docs.domain"),
        (("yaml",), frozenset(), "yaml"), ((), frozenset({"relative"}), ".")]
    assert [(f.path, f.name) for f in SERVICE.facts["imported-name"]] == [
        (("app", "modules", "docs", "domain", "doc"), "doc"), (("yaml", "load"), "load"), (("values",), "values")]


def test_an_import_into_the_app_leads_to_the_file_it_reaches_and_where_that_sits_or_to_a_package_and_a_name():
    assert [(f.target, f.name, f.at) for f in SERVICE.facts["import-into-app"]] == [
        (("modules", "docs", "domain", "doc"), None, Place("domain", "docs", ("doc",))),
        (("modules", "docs", "application", "services"), "values", Place("services", "docs"))]
    assert [f.target for f in TEST.facts["import-into-app"]] == [("modules", "docs", "domain", "doc")]
    assert [f.target for f in TEST.facts["import-into-tests"]] == [("modules", "docs", "domain"), ("fakes", "repo")]
    assert SERVICE.facts["import-into-tests"] == ()


def test_a_call_of_a_class_of_the_app_is_a_construction_and_a_use_of_one_of_its_functions_a_reference():
    assert SERVICE.facts["construction"] == (Fact("construction", 5, DOC, "Doc", at=Place("domain", "docs", ("doc",))),)
    assert [f.at for f in SERVICE.facts["call"]] == [Place("domain", "docs", ("doc", "Doc")), None,
                                                    Place("domain", "docs", ("doc", "make"))]


def test_a_reference_is_a_use_of_a_function_of_the_app_but_the_callee_of_a_call_on_its_line():
    assert SERVICE.facts["function-reference"] == (
        Fact("function-reference", 8, (*MAKE, "cache"), target=("modules", "docs", "domain", "doc", "make"),
             at=Place("domain", "docs", ("doc",))),)


def test_a_use_reads_its_path_and_how_far_its_import_bound_it():
    assert SERVICE.facts["use"] == (Fact("use", 7, MAKE, bound=2), Fact("use", 8, (*MAKE, "cache"), bound=2))


def test_a_method_call_on_what_the_object_holds_says_so():
    assert SERVICE.facts["method-call"] == (Fact("method-call", 8, name="resolve", traits=frozenset({"on-own-object"})),)


def test_a_class_carries_its_name_the_names_it_mentions_and_what_it_is():
    assert DOMAIN.facts["class"] == (
        Fact("class", 1, ("Doc",), "Doc", frozenset({"public"}), names=frozenset({"Repo"})),
        Fact("class", 9, ("Shown",), "Shown", frozenset({"record", "public"})))


def test_a_class_the_reader_says_is_an_immutable_record_carries_it():
    classes = (Class(1, "Frozen", immutable=True), Class(2, "Loose"))
    read = facts_of([source("modules/docs/domain/a.py", classes=classes)], [], PROFILE, "app").files[0]
    assert [fact.traits for fact in read.facts["class"]] == [frozenset({"immutable", "public"}), frozenset({"public"})]


def test_the_trait_record_follows_what_the_reader_says_alone():
    classes = (Class(1, "Said", methods=(Method(2, "size", None),), record=True),
               Class(4, "Unsaid", methods=(Method(5, "__repr__", "str"),)))
    file = SourceFile("app/modules/docs/domain/a.py", ("modules", "docs", "domain", "a.py"), (), classes=classes,
                      functions=(Function(8, "make", returns_named=frozenset({"Unsaid"})),))
    read = facts_of([file], [], PROFILE, "app").files[0]
    assert [fact.traits for fact in read.facts["class"]] == [frozenset({"record", "public"}), frozenset({"public"})]


def test_under_brace_a_class_the_reader_says_is_a_record_is_one_with_no_method_list_and_no_function_naming_it():
    file = source("modules/docs/domain/point.ts", classes=(Class(1, "Point", record=True), Class(2, "Shape")),
                  language=BRACE)
    read = facts_of([file], [], profile(language=BRACE), "app").files[0]
    assert [fact.traits for fact in read.facts["class"]] == [frozenset({"record", "public"}), frozenset({"public"})]


def test_under_percent_a_class_of_special_methods_a_top_level_function_returns_is_no_record_unless_the_reader_says():
    file = source("modules/docs/domain/point.cls", classes=(Class(1, "Point", methods=(Method(2, "%OnNew", None),)),),
                  functions=(Function(4, "Make", returns_named=frozenset({"Point"})),), language=PERCENT)
    read = facts_of([file], [], profile(language=PERCENT), "app").files[0]
    assert [fact.traits for fact in read.facts["class"]] == [frozenset({"public"})]


def test_a_file_built_under_python_has_its_records_read_as_python_s_reader_would_and_one_given_stays_one():
    file = source("modules/docs/domain/a.py", classes=(Class(1, "Shown", methods=(Method(2, "__repr__", "str"),)),
                                                       Class(4, "Loose"),
                                                       Class(5, "Given", methods=(Method(6, "size", None),), record=True)),
                  functions=(Function(8, "make", returns_named=frozenset({"Shown"})),
                             Function(9, "build", owner="Given", returns_named=frozenset({"Loose"}))))
    assert [c.record for c in file.classes] == [True, False, True]


def test_a_file_built_under_another_language_keeps_its_records_as_given():
    file = source("modules/docs/domain/a.ts", classes=(Class(1, "Shown"), Class(2, "Given", record=True)),
                  functions=(Function(8, "make", returns_named=frozenset({"Shown"})),), language=BRACE)
    assert [c.record for c in file.classes] == [False, True]


def test_a_function_says_whether_it_is_at_the_top_level_or_a_method_that_forwards():
    assert DOMAIN.facts["function"] == (
        Fact("function", 4, ("make",), "make", frozenset({"top-level", "public"})),
        Fact("function", 6, ("Doc", "get"), "get", frozenset({"forwards", "public"}), target=("name",),
             text="self.repo.get"))


def test_a_callback_a_comment_the_names_of_a_file_and_the_file_as_a_whole_are_facts():
    assert DOMAIN.facts["callback"] == (Fact("callback", 7, ("make",), "check", frozenset({"annotated-callable"})),)
    assert DOMAIN.facts["comment"] == (Fact("comment", 3, text="# a note"),)
    assert DOMAIN.facts["names-mentioned"] == (Fact("names-mentioned", 0, names=frozenset({"Doc", "make"})),)
    assert DOMAIN.facts["file"] == (Fact("file", 0, traits=frozenset({"no-statements"})),)


def test_a_comment_carries_the_marker_it_opens_with_as_its_name():
    read = facts_of([source("modules/docs/domain/a.py", comments=(Comment(2, "// a note", marker="//"),))], [],
                    PROFILE, "app").files[0]
    assert read.facts["comment"] == (Fact("comment", 2, name="//", text="// a note"),)


def test_a_doc_comment_carries_the_doc_trait():
    read = facts_of([source("modules/docs/domain/a.py", comments=(Comment(2, "/** a doc */", marker="/**", doc=True),))],
                    [], PROFILE, "app").files[0]
    assert read.facts["comment"] == (Fact("comment", 2, name="/**", traits=frozenset({"doc"}), text="/** a doc */"),)


def test_a_file_that_does_not_parse_says_only_its_error():
    assert BROKEN.facts["syntax-error"] == (Fact("syntax-error", 2, text="invalid syntax"),)
    assert {kind for kind, found in BROKEN.facts.items() if found} == {"syntax-error"}


def _rule(**changes) -> Rule:
    fields = {"id": "names", "scope": Scope(APP, "services"), "facts": ("import",), "quantifier": MAY_NOT,
              "targets": EXISTING, "sayings": (Saying("{line}", "x"),)} | changes
    return Rule(**fields)


@pytest.mark.parametrize("rule, kinds", [
    pytest.param(_rule(), {"modules/docs/application/services/publish.py": {"import"}},
                 id="a rule reads its kinds in the files of its scope alone"),
    pytest.param(_rule(scope=Scope(APP, "services"), facts=("import",), quantifier=MUST_REACH,
                       targets=(Match("outside"),), links=("import-into-app",)),
                 {"modules/docs/domain/doc.py": {"import", "import-into-app"}, "scripts/seed.py": {"import", "import-into-app"},
                  "kernel/broken.py": {"import", "import-into-app"},
                  "modules/docs/application/services/publish.py": {"import", "import-into-app", "file"}},
                 id="a rule a file must reach reads its kinds and links on its side, and the file of its scope"),
    pytest.param(_rule(scope=Scope(APP, "domain"), facts=("class",), quantifier=MUST_BE_REACHED, links=("names-mentioned",),
                       roots=Scope(TESTS, where=(Condition("test"),)), spread=("class",),
                       sayings=(Saying("{name}", "x"),)),
                 {"modules/docs/domain/doc.py": {"class", "names-mentioned"}, "modules/docs/domain/test_doc.py": {"names-mentioned"}},
                 id="a rule a fact must be reached by reads its kinds, its links and spread, and the links of its roots"),
])
def test_for_the_rules_given_a_file_holds_only_the_kinds_they_read(rule, kinds):
    facts = facts_of(APP_FILES, TEST_FILES, PROFILE, "app", "tests", (rule,))
    assert {"/".join(r.file.path): set(r.facts) for r in facts.files if r.facts} == kinds


def test_a_class_a_function_and_a_name_an_import_takes_carry_public_exactly_when_the_reader_says_so():
    file = source("modules/docs/domain/a.ts", imp(1, "app.kernel.ids", "shown", "hidden", withheld=("hidden",),
                                                  language=BRACE), imp(2, "app.kernel.ids", language=BRACE),
                  classes=(Class(3, "Kept", public=False), Class(4, "_Shown")),
                  functions=(Function(5, "kept", public=False), Function(6, "_shown"),
                             Function(7, "m", owner="Kept", public=False)), language=BRACE)
    read = facts_of([file], [], replace(PROFILE, language=BRACE), "app").files[0]
    assert [(f.name, "public" in f.traits) for f in read.facts["class"]] == [("Kept", False), ("_Shown", True)]
    assert [(f.name, "public" in f.traits) for f in read.facts["function"]] == [
        ("kept", False), ("_shown", True), ("m", False)]
    assert [(f.name, "public" in f.traits) for f in read.facts["imported-name"]] == [
        ("shown", True), ("hidden", False), (None, False)]
