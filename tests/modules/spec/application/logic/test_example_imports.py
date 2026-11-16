"""The example check: the imports of an architecture's examples obey that architecture's own rules; a tier's example
test under tests/ is only read, one in a part obeys its rules. Each example is given as the reader of the app's
language reads it: its imports, or where it does not parse."""
from tests.modules.spec.profiles_v2 import covered, parsed
from tests.modules.spec.profiles_v2 import layered as layered_v2
from tests.modules.spec.profiles_v2 import parsed as v2
from xarch.kernel.source import Import, Unparsable
from xarch.modules.spec.application.logic.example_imports import Read, example_problems


def frm(module: str, *names: str, up: int | None = None) -> Import:
    """The names imported from a module, named from the top or, given up, from the example's own folder climbed up
    folders."""
    return Import(1, tuple(module.split(".")) if module else (), names, up is not None, up or 0)


def whole(module: str) -> Import:
    """A module imported as a whole."""
    return Import(1, tuple(module.split(".")))

PROFILE = {
    "xarch": 2, "name": "layered",
    "parts": {"shared": {"path": "shared", "role": "code every module uses"},
              "store": {"path": "src/<module>/store", "role": "database access", "may_import": ["sql", "shared/text"]},
              "sql": {"path": "src/<module>/store/sql", "role": "queries"},
              "service": {"path": "src/<module>/service", "role": "business logic",
                          "may_import": ["store", "api@any"]},
              "api": {"path": "src/<module>/api.py", "role": "HTTP handlers", "may_import": "everything"}},
}
PATHS = {"shared": "shared/x.py", "store": "src/billing/store/x.py", "sql": "src/billing/store/sql/x.py",
         "service": "src/billing/service/x.py", "api": "src/billing/api.py"}


def project(texts: dict[str, Read]) -> list[str]:
    """The problems of an example project whose files are the paths given, each read as given."""
    architecture = v2(PROFILE | {"docs": {"examples": ["ex"]}}, folders={"ex": tuple(texts)})
    return example_problems(architecture, texts)


def check(**codes: Read) -> list[str]:
    """The problems of examples at <part>/x.py in module billing, each read as given for its part."""
    return project({PATHS[part]: code for part, code in codes.items()})


def test_imports_the_rules_allow_pass():
    """Imports outside the app are ignored; api@any reaches another module's api; a module of shared is reached by
    name (shared/text); api's * reaches everything, the structure too."""
    assert check(
        service=(whole("os"), frm("typing", "Protocol"), whole("yaml"), frm("app.src.billing.service.rules", "cap"),
                 frm("app.src.billing.store", "Repo"), whole("app.src.billing.store.repo"),
                 frm("app.src.tax.api", "handle")),
        store=(frm("app.shared.text", "slug"), frm("app.src.billing.store.sql", "queries"), frm("app.shared", "text")),
        sql=(frm("app.src.billing.store.sql.queries", "Q"),),
        api=(frm("app.src.tax.store", "Repo"), whole("app")),
    ) == []


def test_an_import_the_rules_forbid_is_reported_once_with_its_rule():
    """store@own reaches billing's store, not tax's; shared/text reaches only that path of shared; sql lies deeper
    than store, so it is its own part with its own rules; the structure (app.src.billing) is reached only by *."""
    assert check(
        service=(frm("app.src.tax.store", "Repo"), frm("app.src.tax.store", "Other"), frm("app.shared", "x")),
        store=(frm("app.shared.other", "y"), frm("app.src.billing.service", "S")),
        sql=(frm("app.src.billing.store.repo", "R"),),
        shared=(frm("app.src", "billing"),),
    ) == [
        "example (src/billing/service/x.py): imports app.src.tax.store which service may not import "
        "(parts.service.may_import)",
        "example (src/billing/service/x.py): imports app.shared which service may not import "
        "(parts.service.may_import)",
        "example (src/billing/store/x.py): imports app.shared.other which store may not import (parts.store.may_import)",
        "example (src/billing/store/x.py): imports app.src.billing.service which store may not import "
        "(parts.store.may_import)",
        "example (src/billing/store/sql/x.py): imports app.src.billing.store.repo which sql may not import "
        "(parts.sql.may_import)",
        "example (shared/x.py): imports app.src.billing which shared may not import (parts.shared.may_import)",
    ]


def test_a_part_may_import_itself_in_its_own_instance_and_not_in_another_without_saying_so():
    assert check(
        shared=(frm("app.shared", "x"),),
        sql=(frm("app.src.billing.store.sql.queries", "Q"), frm("app.src.tax.store.sql", "Q")),
    ) == [
        "example (src/billing/store/sql/x.py): imports app.src.tax.store.sql which sql may not import (parts.sql.may_import)"]


def test_relative_imports_resolve_from_the_examples_path():
    assert check(service=(frm("rules", "cap", up=0), frm("store", "Repo", up=1), frm("tax.store", "T", up=2))) == [
        "example (src/billing/service/x.py): imports app.src.tax.store which service may not import "
        "(parts.service.may_import)"]


def test_an_example_in_no_part_or_not_valid_python_is_reported_and_other_files_are_not_checked():
    assert project({"src/billing/service/a.py": Unparsable(1, "invalid syntax"), "src/billing/service/b.py": (),
                    "src/billing/service/c.sql": (frm("app.src.tax.store", "x"),),
                    "src/billing/helpers.py": ()}) == [
        "example (src/billing/service/a.py): is not valid Python: invalid syntax (line 1)",
        "example (src/billing/helpers.py): lies in no part of the architecture"]


def test_every_python_file_of_an_example_project_is_checked_by_its_path_and_test_code_is_only_parsed():
    files = ("src/billing/api/x.py", "src/billing/store/x.py", "shared/text.py", "tests/src/billing/test_x.py",
             "tests/src/billing/test_y.py", "other/x.py", "notes.md")
    architecture = v2(layered_v2(docs={"examples": ["ex"]}), folders={"ex": files})
    texts = {"src/billing/api/x.py": (frm("app.src.billing.service", "S"),),
             "src/billing/store/x.py": (frm("app.shared", "text"), frm("app.src.billing.api", "A")),
             "shared/text.py": (whole("os"),),
             "tests/src/billing/test_x.py": (frm("app.src.billing.api", "anything"),),
             "tests/src/billing/test_y.py": Unparsable(1, "invalid syntax"), "other/x.py": (),
             "notes.md": ()}
    assert example_problems(architecture, texts) == [
        "example (src/billing/store/x.py): imports app.src.billing.api which store may not import "
        "(parts.store.may_import)",
        "example (tests/src/billing/test_y.py): is not valid Python: invalid syntax (line 1)",
        "example (other/x.py): lies in no part of the architecture"]


UNIT = "tests/src/billing/service/test_rules.py"
INTEGRATION = "src/billing/service/test_api.py"


def test_a_tier_example_under_tests_is_only_parsed_and_one_in_a_part_obeys_its_rules():
    document = covered(docs={"examples": ["ex"]})
    document["parts"]["service"]["may_import"] = []
    document["tiers"]["unit"]["docs"] = {"example": UNIT}
    document["tiers"]["integration"]["docs"] = {"example": INTEGRATION}
    architecture = parsed(document, folders={"ex": (UNIT, INTEGRATION)})
    texts = {UNIT: (frm("app.src.tax.store", "anything"),), INTEGRATION: (frm("app.src.tax.store", "x"),)}
    assert example_problems(architecture, texts) == [
        "example (src/billing/service/test_api.py): imports app.src.tax.store which service may not import "
        "(parts.service.may_import)"]
    assert example_problems(architecture, {**texts, UNIT: Unparsable(1, "invalid syntax")}) == [
        "example (tests/src/billing/service/test_rules.py): is not valid Python: invalid syntax (line 1)",
        "example (src/billing/service/test_api.py): imports app.src.tax.store which service may not import "
        "(parts.service.may_import)"]
