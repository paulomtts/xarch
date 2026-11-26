"""Every variable of a message, on the facts of a small project: one row per variable, each what it prints for the
facts of one kind of one file, under a rule that says what the variable needs of it (a key, a part, targets, a hit);
and a sentence with each of its variables filled in."""
from dataclasses import replace

import pytest

from tests.modules.rules.application.logic.world import (
    BUILT,
    DOMAIN,
    FACTS,
    LISTED,
    NARROWED,
    PORTS,
    PROFILE,
    RESERVED,
    RULE,
    SERVICE,
    STRUCTURE,
    TEST,
    WIRING,
    found,
)
from tests.modules.rules.builders import imp, source
from xarch.modules.rules.application.logic import sentences
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.application.logic.sentences import said, value
from xarch.modules.rules.domain.rule import Found, Match
from xarch.modules.rules.domain.vocabulary import VARIABLES
from xarch.profile_values.checks import Scope
from xarch.profile_values.placement import Target

KEYED = replace(RULE, key="parts.domain.uses.never", scope=Scope(part="domain"))
TARGETED = replace(RULE, facts=("import", "import-into-app"), targets=(Match("place", places=(Target("kernel"), Target("kernel", "any"))),
                                  Match("outside")))
NAMED = replace(RULE, facts=("class",), targets=(Match("name", words=("*Repo", "*Store")),))
SERVICES = replace(RULE, scope=Scope(part="services"))
ALSO = replace(PROFILE, tiers=tuple(replace(tier, imports_also=(Target("web"),)) for tier in PROFILE.tiers))


@pytest.mark.parametrize("name, file, kind, rule, profile, hit, printed", [
    pytest.param("hit", DOMAIN, "use", RULE, PROFILE, ("datetime", "datetime"), ["datetime.datetime", "datetime.datetime"],
                 id="hit"),
    pytest.param("key", DOMAIN, "file", KEYED, PROFILE, None, ["parts.domain.uses.never"], id="key"),
    pytest.param("scope_part", DOMAIN, "file", KEYED, PROFILE, None, ["domain"], id="scope_part"),
    pytest.param("targets", DOMAIN, "file", TARGETED, PROFILE, None, ["kernel/"], id="targets: places as their parts, once"),
    pytest.param("targets", DOMAIN, "file", NAMED, PROFILE, None, ["*Repo or *Store"], id="targets: patterns as written"),
    pytest.param("file", DOMAIN, "file", RULE, PROFILE, None, [DOMAIN], id="file"),
    pytest.param("line", DOMAIN, "comment", RULE, PROFILE, None, ["13", "14"], id="line"),
    pytest.param("where", DOMAIN, "file", RULE, PROFILE, None, ["domain/ of modules/docs"], id="where"),
    pytest.param("where", STRUCTURE, "file", RULE, PROFILE, None, ["structure/"], id="where: the structure"),
    pytest.param("tier", DOMAIN, "file", RULE, PROFILE, None, ["unit"], id="tier: the tier that tests a file of the app"),
    pytest.param("tier", TEST, "file", RULE, PROFILE, None, ["unit"], id="tier: a test's own"),
    pytest.param("mirrored_parts", TEST, "file", RULE, PROFILE, None, ["domain/"], id="mirrored_parts"),
    pytest.param("mirrored_may_import", TEST, "file", RULE, PROFILE, None, ["parts.domain.imports.may"],
                 id="mirrored_may_import"),
    pytest.param("mirrored_may_import", TEST, "file", RULE, ALSO, None,
                 ["parts.domain.imports.may; tiers.unit.imports.also"],
                 id="mirrored_may_import: with what its tier's tests may also import"),
    pytest.param("own_folder", TEST, "file", RULE, PROFILE, None, ["tests/modules/docs"], id="own_folder"),
    pytest.param("tests_folder", DOMAIN, "file", RULE, PROFILE, None, ["tests/modules/docs/domain"], id="tests_folder"),
    pytest.param("language", DOMAIN, "file", RULE, PROFILE, None, ["Python"], id="language"),
    pytest.param("importable_parts", DOMAIN, "file", RULE, PROFILE, None, ["domain/, kernel/"], id="importable_parts"),
    pytest.param("faked_parts", DOMAIN, "file", RULE, PROFILE, None, ["ports"], id="faked_parts"),
    pytest.param("parts_holding_functions", DOMAIN, "file", RULE, replace(PROFILE, holds={"logic": ("functions",)}),
                 None, ["a part that holds functions: logic/"], id="parts_holding_functions"),
    pytest.param("parts_holding_functions", DOMAIN, "file", RULE,
                 replace(PROFILE, holds={"logic": ("functions", "records"), "domain": ("classes",),
                                         "kernel": ("classes", "functions")}), None,
                 ["a part that holds functions: logic/, kernel/"],
                 id="parts_holding_functions: the parts that list functions"),
    pytest.param("parts_holding_classes", DOMAIN, "file", RULE, PROFILE, None, ["a part that holds classes"],
                 id="parts_holding_classes"),
    pytest.param("parts_holding_classes", DOMAIN, "file", RULE,
                 replace(PROFILE, holds={"logic": ("functions", "records"), "domain": ("classes",)}), None,
                 ["a part that holds classes: domain/"], id="parts_holding_classes: the parts that list classes"),
    pytest.param("name", DOMAIN, "class", RULE, PROFILE, None, ["Doc", "DocError", "Shown", "Frozen", "Loose", "Pair"], id="name"),
    pytest.param("qualified_name", DOMAIN, "function", RULE, PROFILE, None, ["make", "Doc.get", "Doc.put"],
                 id="qualified_name"),
    pytest.param("path", DOMAIN, "use", RULE, PROFILE, None, ["datetime.datetime.now", "yaml.load"], id="path"),
    pytest.param("package", DOMAIN, "import", RULE, PROFILE, None, ["yaml", "app", "", "json", "app"], id="package"),
    pytest.param("reserved_reason", DOMAIN, "import", RULE, RESERVED, None, ["", "", "", "only io reads files", ""],
                 id="reserved_reason"),
    pytest.param("library_owners", DOMAIN, "use", RULE, LISTED, None, ["", "platform/"], id="library_owners"),
    pytest.param("first_library_owner", DOMAIN, "use", RULE, LISTED, None, ["", "platform"], id="first_library_owner"),
    pytest.param("written", DOMAIN, "import", RULE, PROFILE, None, ["yaml", "app.kernel", ".", "json", "app.kernel.ids"],
                 id="written"),
    pytest.param("text", DOMAIN, "comment", RULE, PROFILE, None, ["# noqa: E501", "# a note TODO"], id="text"),
    pytest.param("target", SERVICE, "import-into-app", RULE, PROFILE, None,
                 ["app.modules.docs.domain.doc", "app.modules.docs.domain.doc", "app.platform.db"], id="target"),
    pytest.param("target", TEST, "import-into-tests", RULE, PROFILE, None,
                 ["tests.modules.docs.builders", "tests.fakes.repo", "tests.architecture.test_rules"],
                 id="target: below the tests' root for an import into the tests"),
    pytest.param("target_name", SERVICE, "import-into-app", RULE, PROFILE, None,
                 ["app.modules.docs.domain.doc", "app.modules.docs.domain.doc.Doc", "app.platform.db"], id="target_name"),
    pytest.param("target_name", TEST, "import-into-tests", RULE, PROFILE, None,
                 ["tests.modules.docs.builders", "tests.fakes.repo", "tests.architecture.test_rules"],
                 id="target_name: below the tests' root for an import into the tests"),
    pytest.param("target_part", SERVICE, "import-into-app", RULE, PROFILE, None,
                 ["domain/ of modules/docs", "domain/ of modules/docs", "platform/"], id="target_part"),
    pytest.param("target_part_name", SERVICE, "import-into-app", RULE, PROFILE, None, ["domain", "domain", "platform"],
                 id="target_part_name"),
    pytest.param("target_package", SERVICE, "import-into-app", RULE, PROFILE, None,
                 ["app.modules.docs.domain", "app.modules.docs.domain", "app.platform"], id="target_package"),
    pytest.param("built_by", WIRING, "construction", RULE, BUILT, None, ["bootstrap/"], id="built_by"),
    pytest.param("allowed_names", SERVICE, "import-into-app", RULE, NARROWED, None, ["*Id", "*Id", ""],
                 id="allowed_names"),
    pytest.param("disallowed_name", SERVICE, "import-into-app", RULE, PROFILE, None,
                 ["not the file as a whole", "not Doc", "not the file as a whole"], id="disallowed_name"),
    pytest.param("move_fix", SERVICE, "import-into-app", RULE, PROFILE, None,
                 ["move this code to contract/, controller/, logic/ or another part that may import it"] * 2
                 + ["move this code to adapters/, which may import it"], id="move_fix"),
    pytest.param("type_only_fix", SERVICE, "call", SERVICES, PROFILE, None,
                 ["use domain/ here only as a type, and leave the call to contract/, controller/ or logic/ or another "
                  "part, which may make it"] * 2 + ["use None/ here only as a type, and leave the call to code outside "
                                                     "services/"], id="type_only_fix"),
    pytest.param("tier_type_only_fix", TEST, "import-into-app", RULE, PROFILE, None,
                 ["use domain/ here only as a type, and drive what you test through kernel/, domain/, logic/, "
                  "adapters/", "use platform/ here only as a type, and drive what you test through kernel/, domain/, "
                               "logic/, adapters/"], id="tier_type_only_fix"),
    pytest.param("forwarded", DOMAIN, "function", RULE, PROFILE, None, ["", "self.repo.get", "self.repo.put"], id="forwarded"),
    pytest.param("returned", DOMAIN, "function", RULE, PROFILE, None, ["", "name", ""], id="returned"),
    pytest.param("verb", SERVICE, "construction", RULE, PROFILE, None, ["build"], id="verb"),
    pytest.param("verb", SERVICE, "function-reference", RULE, PROFILE, None, ["reference"], id="verb: a reference"),
    pytest.param("function", DOMAIN, "callback", RULE, PROFILE, None, ["make", "get"], id="function"),
    pytest.param("count", DOMAIN, "file", RULE, PROFILE, None, ["5"], id="count: the facts its rule keeps in the file"),
    pytest.param("lines", DOMAIN, "file", RULE, PROFILE, None, ["12"], id="lines"),
    pytest.param("chain", DOMAIN, "file", RULE, PROFILE, None, [""], id="chain: none for a file no way is worked out of"),
])
def test_a_variable_prints_what_it_says_of_each_finding(name, file, kind, rule, profile, hit, printed):
    assert [value(name, f, FACTS, profile) for f in found(file, kind, rule, hit)] == printed


def test_a_sentence_is_said_with_each_variable_filled_in():
    (first, *_) = found(PORTS, "class")
    assert said("{name} of {where} at line {line}, {{braces}} kept", first, FACTS, PROFILE) == (
        "Repo of ports/ of modules/docs at line 2, {braces} kept")


def test_every_variable_the_vocabulary_publishes_has_a_row_and_the_engine_says_it():
    rows = {param.values[0] for param in test_a_variable_prints_what_it_says_of_each_finding.pytestmark[0].args[1]}
    assert rows == {variable.name for variable in VARIABLES} == set(sentences.NAMES)


def test_the_folders_of_a_test_beside_the_code_are_shown_below_the_app_root():
    other = replace(source("modules/docs/domain/test_other.py"), beside=True)
    beside = replace(source("modules/docs/domain/test_doc.py", imp(1, "app.modules.docs.domain.test_other", "x")),
                     beside=True)
    built = facts_of([], [beside, other], PROFILE, "app", "tests")
    read = built.files[0]
    found = Found(RULE, read, read.facts["import-into-tests"][0], None)
    assert value("own_folder", found, built, PROFILE) == "app/modules/docs"
    assert value("tests_folder", found, built, PROFILE) == "app/modules/docs/domain"
    assert value("target", found, built, PROFILE) == "app.modules.docs.domain.test_other"


def test_under_beside_the_folder_where_a_file_of_the_app_is_tested_is_its_own_folder_in_the_app():
    near = replace(PROFILE, framework=replace(PROFILE.framework, beside=True))
    built = facts_of([source("modules/docs/domain/doc.py")], [], near, "app", "tests")
    read = built.files[0]
    found = Found(RULE, read, read.facts["file"][0], None)
    assert value("tests_folder", found, built, near) == "app/modules/docs/domain"
    assert value("tests_folder", found, built, PROFILE) == "tests/modules/docs/domain"
