"""A profile file: the keys that say what code of a part holds and how it may be used (holds, the kinds it lists with
their settings names, immutable and built_by, and a types_only mark on an entry of imports.may), a name pattern
on a target of imports.may, what each test of a tier must reach, and the guards private-imports and dead-code's untested."""
import pytest

from tests.modules.spec.languages import BRACE, PYTHON
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.modules.spec.domain.published import Held
from xarch.modules.spec.domain.values import DeadCode, PrivateImports
from xarch.profile_values.placement import Target

FAKES = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}


def with_part(**keys) -> dict:
    document = layered()
    document["parts"]["service"].update(keys)
    return document


def test_a_part_says_what_its_files_hold_and_how_its_classes_are_named_and_built():
    part = parsed(with_part(holds={"classes": {"names": "*Service", "built_by": ["api"]}},
                            imports={"may": [{"store": "types_only"}, "shared"]})).parts["service"]
    assert (part.holds, part.imports_types_only) == ((Held("classes", ("*Service",), built_by=("api",)),),
                                             (Target("store", "own"),))
    assert not any(hasattr(part, key) for key in ("no_callbacks", "names", "built_by", "immutable"))


def test_the_keys_are_off_when_left_out():
    part = parsed(layered()).parts["service"]
    assert (part.holds, part.imports_types_only) == ((), ())


def test_a_part_says_what_its_files_hold_each_kind_with_its_settings_in_the_order_of_the_kinds():
    holds = {"exceptions": {"names": "*Error"}, "records": {"immutable": True, "names": ["*Found", "*Shown"]},
             "functions": {"names": "is_*"}}
    assert parsed(with_part(holds=holds)).parts["service"].holds == (
        Held("functions", ("is_*",)), Held("records", ("*Found", "*Shown"), True), Held("exceptions", ("*Error",)))


@pytest.mark.parametrize("holds, expected", [
    pytest.param({"classes": {}}, (Held("classes"),), id="classes, no setting"),
    pytest.param({"functions": {}, "records": {"immutable": True}, "exceptions": {}},
                 (Held("functions"), Held("records", immutable=True), Held("exceptions")), id="what logic holds"),
    pytest.param({"classes": {"immutable": True}, "functions": {}}, (Held("classes", immutable=True), Held("functions")),
                 id="classes and functions"),
    pytest.param({"classes": {"names": "*Service"}, "exceptions": {"names": "*Error"}},
                 (Held("classes", ("*Service",)), Held("exceptions", ("*Error",))), id="exceptions beside classes"),
    pytest.param({"records": {"immutable": False}}, (Held("records"),), id="immutable false is no setting"),
])
def test_each_kind_listed_is_held_with_the_settings_it_writes(holds, expected):
    assert parsed(with_part(holds=holds)).parts["service"].holds == expected


def test_a_part_whose_classes_are_immutable_records_says_so_and_is_not_one_when_left_out():
    assert parsed(with_part(holds={"classes": {"immutable": True}})).parts["service"].holds == (
        Held("classes", immutable=True),)


def test_names_may_be_a_list_of_patterns():
    assert parsed(with_part(holds={"classes": {"names": ["*Service", "*Step"]}})).parts["service"].holds == (
        Held("classes", ("*Service", "*Step")),)


MAP = "must be a map of its settings, {} for none, such as"


@pytest.mark.parametrize("holds, expected", [
    pytest.param("types", "parts.service.holds: must be a map of kinds, such as {classes: {}}", id="another word"),
    pytest.param(True, "parts.service.holds: must be a map of kinds, such as {classes: {}}", id="true"),
    pytest.param(None, "parts.service.holds: must be a map of kinds, such as {classes: {}}", id="null"),
    pytest.param(["classes"], "parts.service.holds: must be a map of kinds, such as {classes: {}}", id="a list"),
    pytest.param(3, "parts.service.holds: must be a map of kinds, such as {classes: {}}", id="a number"),
    pytest.param({}, "parts.service.holds: lists no kind: list the kinds the part may hold, or drop holds to allow every "
                     "kind", id="an empty map"),
    pytest.param({"function": {}}, "parts.service.holds: no kind 'function': use classes, exceptions, functions, records",
                 id="a kind that is none"),
    pytest.param({"functions": None}, f"parts.service.holds.functions: {MAP} {{names: \"is_*\"}}", id="functions, null"),
    pytest.param({"functions": True}, f"parts.service.holds.functions: {MAP} {{names: \"is_*\"}}", id="functions, true"),
    pytest.param({"classes": False}, f"parts.service.holds.classes: {MAP} {{names: \"*Service\"}}", id="classes, false"),
    pytest.param({"classes": []}, f"parts.service.holds.classes: {MAP} {{names: \"*Service\"}}", id="classes, a list"),
    pytest.param({"records": "yes"}, f"parts.service.holds.records: {MAP} {{immutable: true}}", id="records, a string"),
    pytest.param({"exceptions": 1}, f"parts.service.holds.exceptions: {MAP} {{names: \"*Error\"}}",
                 id="exceptions, a number"),
    pytest.param({"functions": {"immutable": True}}, "parts.service.holds.functions: unknown key 'immutable': a setting "
                                                     "of classes and records; use names", id="immutable under functions"),
    pytest.param({"functions": {"built_by": ["api"]}}, "parts.service.holds.functions: unknown key 'built_by': a "
                                                       "setting of classes; use names", id="built_by under functions"),
    pytest.param({"records": {"built_by": ["api"]}}, "parts.service.holds.records: unknown key 'built_by': a setting "
                                                     "of classes; use immutable, names", id="built_by under records"),
    pytest.param({"exceptions": {"immutable": True}}, "parts.service.holds.exceptions: unknown key 'immutable': a "
                                                      "setting of classes and records; use names",
                 id="immutable under exceptions"),
    pytest.param({"exceptions": {"built_by": ["api"]}}, "parts.service.holds.exceptions: unknown key 'built_by': a "
                                                        "setting of classes; use names", id="built_by under exceptions"),
    pytest.param({"functions": {"methods": "x"}}, "parts.service.holds.functions: unknown key 'methods': use names",
                 id="a setting no kind takes"),
    pytest.param({"classes": {}, "exceptions": {}}, "parts.service.holds.exceptions: says nothing beside classes, which "
                                                    "already allows exceptions: give it a setting, or drop it",
                 id="exceptions with no setting beside classes"),
    pytest.param({"classes": {}, "records": {}}, "parts.service.holds.records: says nothing beside classes, which "
                                                 "already allows records: give it a setting, or drop it",
                 id="records with no setting beside classes"),
    pytest.param({"classes": {"names": ""}}, "parts.service.holds.classes.names: must be a name pattern with `*` for any "
                                             "text, such as *Service, or a list of them", id="names, empty"),
    pytest.param({"functions": {"names": "Bad Name"}}, "parts.service.holds.functions.names: 'Bad Name' is not a name "
                                                       "pattern: write it with no space, `@`, `/` or `:`, `*` standing "
                                                       "for any text", id="names, a space"),
    pytest.param({"records": {"names": [3]}}, "parts.service.holds.records.names: 3 is not a name pattern: write it with "
                                              "no space, `@`, `/` or `:`, `*` standing for any text", id="names, a number"),
    pytest.param({"classes": {"immutable": "yes"}}, "parts.service.holds.classes.immutable: must be true or false: "
                                                    "whether every class of the part, but an exception, is an immutable "
                                                    "record", id="classes, immutable no boolean"),
    pytest.param({"records": {"immutable": 1}}, "parts.service.holds.records.immutable: must be true or false: whether "
                                                "every record of the part is an immutable record",
                 id="records, immutable no boolean"),
    pytest.param({"classes": {"built_by": ["ghost"]}}, "parts.service.holds.classes.built_by: no part named 'ghost'",
                 id="built_by, no such part"),
    pytest.param({"classes": {"built_by": []}}, "parts.service.holds.classes.built_by: must be a list of part names",
                 id="built_by, empty"),
])
def test_a_bad_holds_is_refused(holds, expected):
    assert problems(with_part(holds=holds)) == [f"layered.yaml: {expected}"]


def test_the_problems_of_holds_are_collected_together_with_the_others_of_the_part():
    holds = {"function": {}, "classes": {"names": ""}, "records": {}, "exceptions": {"built_by": ["api"]}}
    assert problems(with_part(holds=holds, shared=1)) == [
        "layered.yaml: parts.service.holds: no kind 'function': use classes, exceptions, functions, records",
        "layered.yaml: parts.service.holds.classes.names: must be a name pattern with `*` for any text, such as "
        "*Service, or a list of them",
        "layered.yaml: parts.service.holds.records: says nothing beside classes, which already allows records: give it "
        "a setting, or drop it",
        "layered.yaml: parts.service.holds.exceptions: unknown key 'built_by': a setting of classes; use names",
        "layered.yaml: parts.service.shared: must be a whole number of users, at least 2, such as 2; leave it out for a "
        "part that is not there to be shared"]


def test_a_part_there_to_be_shared_says_by_how_many_users_and_is_not_shared_when_left_out():
    assert parsed(with_part(shared=3)).parts["service"].shared == 3
    assert parsed(layered()).parts["service"].shared is None


@pytest.mark.parametrize("keys, expected", [
    pytest.param({"shared": 1}, "parts.service.shared: must be a whole number of users, at least 2, such as 2; leave it "
                                "out for a part that is not there to be shared", id="shared, one user"),
    pytest.param({"shared": True}, "parts.service.shared: must be a whole number of users, at least 2, such as 2; leave "
                                   "it out for a part that is not there to be shared", id="shared, no number"),
])
def test_a_bad_key_of_a_part_is_refused(keys, expected):
    assert problems(with_part(**keys)) == [f"layered.yaml: {expected}"]


def test_a_target_of_imports_may_may_narrow_what_is_imported_by_a_name_pattern():
    document = with_part(imports={"may": ["store:*Id", "shared/text:Word*"]})
    assert parsed(document).rules["service"] == (Target("store", "own", (), "*Id"), Target("shared", "none", ("text",),
                                                                                           "Word*"))


@pytest.mark.parametrize("value, expected", [
    pytest.param("store:", "'store:' has an empty name pattern after `:`", id="an empty pattern"),
    pytest.param("store:a b", "'store:a b' has a name pattern that is not one: write it with no space, `@`, `/` or "
                              "`:`, `*` standing for any text", id="a pattern with a space"),
])
def test_a_bad_name_pattern_is_refused(value, expected):
    assert problems(with_part(imports={"may": [value]})) == [f"layered.yaml: parts.service.imports.may: {expected}"]


def test_imports_must_takes_no_name_pattern():
    document = with_part(imports={"may": ["store:*Id"], "must": ["store:*Id"]})
    assert problems(document) == [
        "layered.yaml: parts.service.imports.must: 'store:*Id' has a name pattern, which this key does not take: drop "
        "':*Id'"]


def test_a_tier_says_what_each_of_its_tests_must_reach():
    document = covered()
    document["tiers"]["integration"]["imports"] = {"must": ["api", "store"]}
    tiers = {tier.name: tier for tier in parsed(document).tiers}
    assert (tiers["integration"].imports_must, tiers["unit"].imports_must) == (("api", "store"), ())


def test_a_tier_must_import_names_parts():
    document = covered()
    document["tiers"]["unit"]["imports"] = {"must": ["ghost"]}
    assert problems(document) == ["layered.yaml: tiers.unit.imports.must: no part named 'ghost'"]


def test_dead_code_may_also_list_the_files_no_test_of_their_tier_reaches():
    guards = {"dead-code": {"untested": True}, "private-imports": {}}
    assert parsed(covered(guards=guards, fakes=FAKES)).guards == (DeadCode(True), PrivateImports())
    assert parsed(covered(guards={"dead-code": {}}, fakes=FAKES)).guards == (DeadCode(False),)


def test_dead_code_may_accept_public_names_as_only_the_tests_each_as_its_file_below_the_app_and_its_name():
    known = ["src/billing/store/db.py:Store", "shared/text.py:clean"]
    assert parsed(covered(guards={"dead-code": {"tests_only": True, "known": known}}, fakes=FAKES)).guards == (
        DeadCode(False, True, ("src/billing/store/db.py:Store", "shared/text.py:clean")),)


NOT = "is not <file below the app>:<name>, such as documents/rules.py:clean"
"""How the format refuses an entry of guards.dead-code.known that is not one, under Python."""


@pytest.mark.parametrize("guards, expected", [
    pytest.param({"dead-code": {"untested": "yes"}}, "guards.dead-code.untested: must be true or false",
                 id="untested, no boolean"),
    pytest.param({"dead-code": {"x": 1}}, "guards.dead-code: unknown key 'x': use known, tests_only, untested",
                 id="an unknown key"),
    pytest.param({"dead-code": 3}, "guards.dead-code: must be a mapping {untested: true|false, tests_only: true|false, "
                                   "known: [<file>:<name>, ...]}, or {}", id="no mapping"),
    pytest.param({"dead-code": {"known": ["shared/text.py:clean"]}},
                 "guards.dead-code.known: needs `tests_only: true`: it names the public names that check accepts as only "
                 "the tests'", id="known without tests_only"),
    pytest.param({"dead-code": {"tests_only": True, "known": "shared/text.py:clean"}},
                 "guards.dead-code.known: must be a list of <file below the app>:<name>, such as [documents/rules.py:clean]",
                 id="known, no list"),
    pytest.param({"dead-code": {"tests_only": True, "known": ["shared/text.py"]}},
                 "guards.dead-code.known: 'shared/text.py' " + NOT, id="known, an entry with no name"),
    pytest.param({"dead-code": {"tests_only": True, "known": ["shared/text:clean"]}},
                 "guards.dead-code.known: 'shared/text:clean' " + NOT, id="known, a file not of the language"),
    pytest.param({"dead-code": {"tests_only": True, "known": ["/shared/text.py:clean"]}},
                 "guards.dead-code.known: '/shared/text.py:clean' " + NOT, id="known, a file not below the app"),
    pytest.param({"dead-code": {"tests_only": True, "known": ["shared/text.py:2x"]}},
                 "guards.dead-code.known: 'shared/text.py:2x' " + NOT, id="known, a name the language does not allow"),
    pytest.param({"dead-code": {"tests_only": True, "known": [3]}}, "guards.dead-code.known: 3 " + NOT,
                 id="known, an entry that is no text"),
    pytest.param({"dead-code": {"tests_only": True, "known": ["shared/text.py:clean", "shared/text.py:clean"]}},
                 "guards.dead-code.known: 'shared/text.py:clean' is listed twice", id="known, an entry listed twice"),
    pytest.param({"private-imports": {"x": 1}}, "guards.private-imports: takes no parameters: write {}",
                 id="private-imports, a parameter"),
])
def test_a_bad_parameter_of_the_guards_is_refused(guards, expected):
    assert problems(covered(guards=guards, fakes=FAKES)) == [f"layered.yaml: {expected}"]


def test_dead_code_may_accept_a_public_name_of_a_file_of_any_ending_of_the_language():
    known = ["shared/text.tsx:clean", "shared/run.mts:main"]
    document = covered(guards={"dead-code": {"tests_only": True, "known": known}}, fakes=FAKES, language="brace",
                       testing={"files": ["*.test.ts"], "declared": [{"function": "test*"}]})
    assert parsed(document, languages={"python": PYTHON, "brace": BRACE}).guards == (
        DeadCode(False, True, ("shared/text.tsx:clean", "shared/run.mts:main")),)
