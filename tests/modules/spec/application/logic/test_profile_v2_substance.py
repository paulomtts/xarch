"""A profile file in format 2: the keys that say what code of a part holds and how it may be used (holds, immutable,
types_only, no_callbacks, names, built_by), a name pattern on a target of may_import, what each test of a tier must reach, and the
guards private-imports and dead-code's untested."""
import pytest

from tests.modules.spec.profiles_v2 import covered, layered, parsed, problems
from xarch.modules.spec.domain.values import DeadCode, PrivateImports
from xarch.profile_values.placement import Target

FAKES = {"folder": "fakes", "for": ["store"], "prefix": "Fake"}


def with_part(**keys) -> dict:
    document = layered()
    document["parts"]["service"].update(keys)
    return document


def test_a_part_says_what_its_files_hold_and_how_its_classes_are_named_and_built():
    part = parsed(with_part(holds="classes", names="*Service", built_by=["api"], no_callbacks=True,
                            types_only=["store"])).parts["service"]
    assert (part.holds, part.names, part.built_by, part.no_callbacks, part.types_only) == (
        "classes", ("*Service",), ("api",), True, ("store",))


def test_the_keys_are_off_when_left_out():
    part = parsed(layered()).parts["service"]
    assert (part.holds, part.names, part.built_by, part.no_callbacks, part.types_only) == ("", (), (), False, ())


def test_a_part_there_to_be_shared_says_by_how_many_users_and_is_not_shared_when_left_out():
    assert parsed(with_part(shared=3)).parts["service"].shared == 3
    assert parsed(layered()).parts["service"].shared is None


def test_a_part_whose_classes_are_immutable_records_says_so_and_is_not_one_when_left_out():
    assert parsed(with_part(holds="functions", immutable=True)).parts["service"].immutable is True
    assert parsed(layered()).parts["service"].immutable is False


def test_names_may_be_a_list_of_patterns():
    assert parsed(with_part(names=["*Service", "*Step"])).parts["service"].names == ("*Service", "*Step")


@pytest.mark.parametrize("keys, expected", [
    pytest.param({"holds": "types"}, "parts.service.holds: must be classes or functions", id="holds, another word"),
    pytest.param({"holds": True}, "parts.service.holds: must be classes or functions", id="holds, no word"),
    pytest.param({"no_callbacks": "yes"}, "parts.service.no_callbacks: must be true or false",
                 id="no_callbacks, no boolean"),
    pytest.param({"immutable": "yes"}, "parts.service.immutable: must be true or false: whether every class the part "
                                       "defines, but an exception, is an immutable record", id="immutable, no boolean"),
    pytest.param({"names": ""}, "parts.service.names: must be a class name pattern with `*` for any text, such as "
                                "*Store, or a list of them", id="names, empty"),
    pytest.param({"names": "Bad Name"}, "parts.service.names: 'Bad Name' is not a class name pattern: use letters, "
                                        "digits, '_' and `*`", id="names, a space"),
    pytest.param({"names": [3]}, "parts.service.names: 3 is not a class name pattern: use letters, digits, '_' and "
                                 "`*`", id="names, a number"),
    pytest.param({"built_by": ["ghost"]}, "parts.service.built_by: no part named 'ghost'", id="built_by, no such part"),
    pytest.param({"built_by": []}, "parts.service.built_by: must be a list of part names", id="built_by, empty"),
    pytest.param({"types_only": ["ghost"]}, "parts.service.types_only: no part named 'ghost'",
                 id="types_only, no such part"),
    pytest.param({"types_only": ["api"]}, "parts.service.types_only: 'api' is not in `may_import`, so no file could "
                                          "import it to use as a type: add it there, or drop it", id="types_only, not importable"),
    pytest.param({"shared": 1}, "parts.service.shared: must be a whole number of users, at least 2, such as 2; leave it "
                                "out for a part that is not there to be shared", id="shared, one user"),
    pytest.param({"shared": True}, "parts.service.shared: must be a whole number of users, at least 2, such as 2; leave "
                                   "it out for a part that is not there to be shared", id="shared, no number"),
])
def test_a_bad_key_of_a_part_is_refused(keys, expected):
    assert problems(with_part(**keys)) == [f"layered.yaml: {expected}"]


def test_types_only_is_met_by_a_part_that_may_import_everything():
    document = layered()
    document["parts"]["api"]["may_import"] = "everything"
    document["parts"]["api"]["types_only"] = ["store"]
    assert parsed(document).parts["api"].types_only == ("store",)


def test_a_target_of_may_import_may_narrow_what_is_imported_by_a_name_pattern():
    document = with_part(may_import=["store:*Id", "shared/text:Word*"])
    assert parsed(document).rules["service"] == (Target("store", "own", (), "*Id"), Target("shared", "none", ("text",),
                                                                                           "Word*"))


@pytest.mark.parametrize("value, expected", [
    pytest.param("store:", "'store:' has an empty name pattern after `:`", id="an empty pattern"),
    pytest.param("store:a b", "'store:a b' has a name pattern that is not one: use letters, digits, '_' and `*`",
                 id="a pattern with a space"),
])
def test_a_bad_name_pattern_is_refused(value, expected):
    assert problems(with_part(may_import=[value])) == [f"layered.yaml: parts.service.may_import: {expected}"]


def test_must_import_takes_no_name_pattern():
    document = with_part(may_import=["store:*Id"], must_import=["store:*Id"])
    assert problems(document) == [
        "layered.yaml: parts.service.must_import: 'store:*Id' has a name pattern, which this key does not take: drop "
        "':*Id'"]


def test_a_tier_says_what_each_of_its_tests_must_reach():
    document = covered()
    document["tiers"]["integration"]["must_import"] = ["api", "store"]
    tiers = {tier.name: tier for tier in parsed(document).tiers}
    assert (tiers["integration"].must_import, tiers["unit"].must_import) == (("api", "store"), ())


def test_a_tier_must_import_names_parts():
    document = covered()
    document["tiers"]["unit"]["must_import"] = ["ghost"]
    assert problems(document) == ["layered.yaml: tiers.unit.must_import: no part named 'ghost'"]


def test_dead_code_may_also_list_the_files_no_test_of_their_tier_reaches():
    guards = {"dead-code": {"untested": True}, "private-imports": {}}
    assert parsed(covered(guards=guards, fakes=FAKES)).guards == (DeadCode(True), PrivateImports())
    assert parsed(covered(guards={"dead-code": {}}, fakes=FAKES)).guards == (DeadCode(False),)


@pytest.mark.parametrize("guards, expected", [
    pytest.param({"dead-code": {"untested": "yes"}}, "guards.dead-code.untested: must be true or false",
                 id="untested, no boolean"),
    pytest.param({"dead-code": {"x": 1}}, "guards.dead-code: unknown key 'x': use tests_only, untested", id="an unknown key"),
    pytest.param({"dead-code": 3}, "guards.dead-code: must be a mapping {untested: true|false, tests_only: true|false}, or {}",
                 id="no mapping"),
    pytest.param({"private-imports": {"x": 1}}, "guards.private-imports: takes no parameters: write {}",
                 id="private-imports, a parameter"),
])
def test_a_bad_parameter_of_the_guards_is_refused(guards, expected):
    assert problems(covered(guards=guards, fakes=FAKES)) == [f"layered.yaml: {expected}"]
