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
from xarch.kernel.placement import Target
from xarch.modules.rules.application.logic import sentences
from xarch.modules.rules.application.logic.sentences import said, value
from xarch.modules.rules.domain.rule import Match, Scope
from xarch.modules.rules.domain.vocabulary import VARIABLES

KEYED = replace(RULE, key="parts.domain.forbidden", scope=Scope(part="domain"))
TARGETED = replace(RULE, facts=("import", "import-into-app"), targets=(Match("place", places=(Target("kernel"), Target("kernel", "any"))),
                                  Match("outside")))
NAMED = replace(RULE, facts=("class",), targets=(Match("name", words=("*Repo", "*Store")),))
SERVICES = replace(RULE, scope=Scope(part="services"))


@pytest.mark.parametrize("name, file, kind, rule, profile, printed", [
    pytest.param("key", DOMAIN, "file", KEYED, PROFILE, ["parts.domain.forbidden"], id="key"),
    pytest.param("scope_part", DOMAIN, "file", KEYED, PROFILE, ["domain"], id="scope_part"),
    pytest.param("targets", DOMAIN, "file", TARGETED, PROFILE, ["kernel/"], id="targets: places as their parts, once"),
    pytest.param("targets", DOMAIN, "file", NAMED, PROFILE, ["*Repo or *Store"], id="targets: patterns as written"),
    pytest.param("hit", DOMAIN, "use", RULE, PROFILE, ["datetime.datetime", "datetime.datetime"], id="hit"),
    pytest.param("file", DOMAIN, "file", RULE, PROFILE, [DOMAIN], id="file"),
    pytest.param("line", DOMAIN, "comment", RULE, PROFILE, ["13", "14"], id="line"),
    pytest.param("where", DOMAIN, "file", RULE, PROFILE, ["domain/ of modules/docs"], id="where"),
    pytest.param("where", STRUCTURE, "file", RULE, PROFILE, ["structure/"], id="where: the structure"),
    pytest.param("tier", DOMAIN, "file", RULE, PROFILE, ["unit"], id="tier: the tier that tests a file of the app"),
    pytest.param("tier", TEST, "file", RULE, PROFILE, ["unit"], id="tier: a test's own"),
    pytest.param("mirrored_parts", TEST, "file", RULE, PROFILE, ["domain/"], id="mirrored_parts"),
    pytest.param("mirrored_may_import", TEST, "file", RULE, PROFILE, ["parts.domain.may_import"],
                 id="mirrored_may_import"),
    pytest.param("own_folder", TEST, "file", RULE, PROFILE, ["tests/modules/docs"], id="own_folder"),
    pytest.param("tests_folder", DOMAIN, "file", RULE, PROFILE, ["tests/modules/docs/domain"], id="tests_folder"),
    pytest.param("language", DOMAIN, "file", RULE, PROFILE, ["Python"], id="language"),
    pytest.param("importable_parts", DOMAIN, "file", RULE, PROFILE, ["domain/, kernel/"], id="importable_parts"),
    pytest.param("faked_parts", DOMAIN, "file", RULE, PROFILE, ["ports"], id="faked_parts"),
    pytest.param("parts_holding_functions", DOMAIN, "file", RULE, replace(PROFILE, holds={"logic": "functions"}),
                 ["a part that holds functions: logic/"], id="parts_holding_functions"),
    pytest.param("parts_holding_classes", DOMAIN, "file", RULE, PROFILE, ["a part that holds classes"],
                 id="parts_holding_classes"),
    pytest.param("name", DOMAIN, "class", RULE, PROFILE, ["Doc", "DocError", "Shown", "Frozen", "Loose", "Pair"], id="name"),
    pytest.param("qualified_name", DOMAIN, "function", RULE, PROFILE, ["make", "Doc.get", "Doc.put"],
                 id="qualified_name"),
    pytest.param("path", DOMAIN, "use", RULE, PROFILE, ["datetime.datetime.now", "yaml.load"], id="path"),
    pytest.param("package", DOMAIN, "import", RULE, PROFILE, ["yaml", "app", "", "json", "app"], id="package"),
    pytest.param("reserved_reason", DOMAIN, "import", RULE, RESERVED, ["", "", "", "only io reads files", ""],
                 id="reserved_reason"),
    pytest.param("library_owners", DOMAIN, "use", RULE, LISTED, ["", "platform/"], id="library_owners"),
    pytest.param("first_library_owner", DOMAIN, "use", RULE, LISTED, ["", "platform"], id="first_library_owner"),
    pytest.param("written", DOMAIN, "import", RULE, PROFILE, ["yaml", "app.kernel", ".", "json", "app.kernel.ids"],
                 id="written"),
    pytest.param("text", DOMAIN, "comment", RULE, PROFILE, ["# noqa: E501", "# a note TODO"], id="text"),
    pytest.param("target", SERVICE, "import-into-app", RULE, PROFILE,
                 ["app.modules.docs.domain.doc", "app.modules.docs.domain.doc", "app.platform.db"], id="target"),
    pytest.param("target", TEST, "import-into-tests", RULE, PROFILE,
                 ["tests.modules.docs.builders", "tests.fakes.repo", "tests.architecture.test_rules"],
                 id="target: below the tests' root for an import into the tests"),
    pytest.param("target_name", SERVICE, "import-into-app", RULE, PROFILE,
                 ["app.modules.docs.domain.doc", "app.modules.docs.domain.doc.Doc", "app.platform.db"], id="target_name"),
    pytest.param("target_name", TEST, "import-into-tests", RULE, PROFILE,
                 ["tests.modules.docs.builders", "tests.fakes.repo", "tests.architecture.test_rules"],
                 id="target_name: below the tests' root for an import into the tests"),
    pytest.param("target_part", SERVICE, "import-into-app", RULE, PROFILE,
                 ["domain/ of modules/docs", "domain/ of modules/docs", "platform/"], id="target_part"),
    pytest.param("target_part_name", SERVICE, "import-into-app", RULE, PROFILE, ["domain", "domain", "platform"],
                 id="target_part_name"),
    pytest.param("target_package", SERVICE, "import-into-app", RULE, PROFILE,
                 ["app.modules.docs.domain", "app.modules.docs.domain", "app.platform"], id="target_package"),
    pytest.param("built_by", WIRING, "construction", RULE, BUILT, ["bootstrap/"], id="built_by"),
    pytest.param("allowed_names", SERVICE, "import-into-app", RULE, NARROWED, ["*Id", "*Id", ""],
                 id="allowed_names"),
    pytest.param("disallowed_name", SERVICE, "import-into-app", RULE, PROFILE,
                 ["not the file as a whole", "not Doc", "not the file as a whole"], id="disallowed_name"),
    pytest.param("move_fix", SERVICE, "import-into-app", RULE, PROFILE,
                 ["move this code to contract/, controller/, logic/ or another part that may import it"] * 2
                 + ["move this code to adapters/, which may import it"], id="move_fix"),
    pytest.param("type_only_fix", SERVICE, "call", SERVICES, PROFILE,
                 ["use domain/ here only as a type, and leave the call to contract/, controller/ or logic/ or another "
                  "part, which may make it"] * 2 + ["use None/ here only as a type, and leave the call to code outside "
                                                     "services/"], id="type_only_fix"),
    pytest.param("tier_type_only_fix", TEST, "import-into-app", RULE, PROFILE,
                 ["use domain/ here only as a type, and drive what you test through kernel/, domain/, logic/, "
                  "adapters/", "use platform/ here only as a type, and drive what you test through kernel/, domain/, "
                               "logic/, adapters/"], id="tier_type_only_fix"),
    pytest.param("forwarded", DOMAIN, "function", RULE, PROFILE, ["", "self.repo.get", "self.repo.put"], id="forwarded"),
    pytest.param("returned", DOMAIN, "function", RULE, PROFILE, ["", "name", ""], id="returned"),
    pytest.param("verb", SERVICE, "construction", RULE, PROFILE, ["build"], id="verb"),
    pytest.param("verb", SERVICE, "function-reference", RULE, PROFILE, ["reference"], id="verb: a reference"),
    pytest.param("function", DOMAIN, "callback", RULE, PROFILE, ["make", "get"], id="function"),
])
def test_a_variable_prints_what_it_says_of_each_finding(name, file, kind, rule, profile, printed):
    hit = ("datetime", "datetime") if name == "hit" else None
    assert [value(name, f, FACTS, profile) for f in found(file, kind, rule, hit)] == printed


def test_a_sentence_is_said_with_each_variable_filled_in():
    (first, *_) = found(PORTS, "class")
    assert said("{name} of {where} at line {line}, {{braces}} kept", first, FACTS, PROFILE) == (
        "Repo of ports/ of modules/docs at line 2, {braces} kept")


def test_every_variable_the_vocabulary_publishes_has_a_row_and_the_engine_says_it():
    rows = {param.values[0] for param in test_a_variable_prints_what_it_says_of_each_finding.pytestmark[0].args[1]}
    assert rows == {variable.name for variable in VARIABLES} == set(sentences.NAMES)
