"""The test tiers of a profile file: parsed, validated, and every part covered or marked untested; what they put in the
docs."""
import pytest

from tests.modules.spec.format_files import FILE_TYPES
from tests.modules.spec.profiles import covered, layered, parsed, problems
from xarch.modules.spec.application.logic.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidArchitecture, InvalidTemplate
from xarch.modules.spec.domain.values import TierExample

UNIT = "tests/src/billing/service/test_rules.py"
API = "tests/src/test_api.py"
BUILDERS = "tests/src/builders.py"
CONFTEST = "tests/src/conftest.py"
FILES = {"ex": (UNIT, API, BUILDERS, CONFTEST)}
EXAMPLE_PROBLEM = "layered.yaml: tiers.unit.docs.example: must be a path in an example project, such as " \
                  "src/billing/charge.py"
FOLDER_PROBLEM = ("layered.yaml: tiers.unit.folder: must be a folder below the tests folder, such as architecture: "
                  "relative, with no `..`, no empty step and no `*`")
TIERS_PROBLEM = ("layered.yaml: tiers: must be a mapping of tier names to {proves, litmus, ...}, in the order their "
                 "litmus tests run")
UNTESTED_PROBLEM = "layered.yaml: parts.shared.untested: must be one line of text: why no tier tests the part"
OUTSIDE = ("layered.yaml: tiers.unit.docs.example: '{path}' is not inside the tier's folder 'checks' below the tests "
           "folder: the docs would show a place `check` places in no tier")


def tiered() -> dict:
    """covered(), whose tiers carry every text of the docs and an example each, taken from the example project ex."""
    document = covered(docs={"examples": ["ex"], "example_notes": {UNIT: "one per rule", BUILDERS: "shared"}})
    document["tiers"]["unit"]["docs"] = {"may_touch": "nothing", "one_file_per": "rule",
                                         "cases_from": "the invariants", "data": "built in the test", "example": UNIT}
    document["tiers"]["integration"]["docs"] = {
        "subject": "`src/` but `service/`", "may_touch": "the database", "one_file_per": "route",
        "cases_from": "its arguments", "data": "the seed", "example": API}
    return document


def parse(document: dict):
    return parsed(document, folders=FILES)


def found(document: dict, files=FILES) -> list[str]:
    """The problems of the document; none when it loads."""
    try:
        parsed(document, folders=files)
    except InvalidArchitecture as error:
        return list(error.problems)
    return []


def with_tier(**changes) -> dict:
    document = covered()
    document["tiers"]["integration"] |= changes
    return document


def with_docs(**docs) -> dict:
    document = covered(docs={"examples": ["ex"]})
    document["tiers"]["unit"]["docs"] = docs
    return document


@pytest.mark.parametrize("types_only, expected", [
    pytest.param(["repo", "service"], ["layered.yaml: tiers.integration.types_only: no part named 'repo'"],
                 id="a part that does not exist is refused"),
    pytest.param(["service", "service"], ["layered.yaml: tiers.integration.types_only: 'service' is listed twice"],
                 id="a part listed twice is refused"),
    pytest.param("service", ["layered.yaml: tiers.integration.types_only: must be a list of part names"],
                 id="a part given as one text is refused"),
    pytest.param([], ["layered.yaml: tiers.integration.types_only: must be a list of part names"],
                 id="no part at all is refused"),
])
def test_a_bad_types_only_entry_is_refused(types_only, expected):
    assert problems(with_tier(types_only=types_only)) == expected


def test_a_tier_with_no_types_only_has_none():
    assert [tier.types_only for tier in parsed(covered()).tiers] == [(), ()]


def test_a_litmus_of_blanks_is_refused():
    assert problems(with_tier(litmus="  ")) == [
        "layered.yaml: tiers.integration.litmus: must be text: the question that tells a test belongs to the tier"]


@pytest.mark.parametrize("tiers", [
    pytest.param([], id="a list is refused"),
    pytest.param({}, id="a mapping holding no tier is refused"),
    pytest.param("unit", id="a text is refused"),
])
def test_tiers_that_are_no_mapping_of_tiers_are_refused(tiers):
    assert problems(covered(tiers=tiers)) == [TIERS_PROBLEM]


@pytest.mark.parametrize("untested", [
    pytest.param("", id="an empty reason is refused"),
    pytest.param("two\nlines", id="a reason of two lines is refused"),
    pytest.param(3, id="a reason that is no text is refused"),
])
def test_a_bad_untested_reason_is_refused(untested):
    document = covered()
    document["parts"]["shared"]["untested"] = untested
    assert problems(document) == [UNTESTED_PROBLEM]


@pytest.mark.parametrize("example, expected", [
    pytest.param("tests/../x.py", [EXAMPLE_PROBLEM], id="a path climbing out is refused"),
    pytest.param("tests/src/*/test_x.py", [EXAMPLE_PROBLEM], id="a path naming no instance is refused"),
    pytest.param("", [EXAMPLE_PROBLEM], id="an empty path is refused"),
    pytest.param("tests/nowhere.py", ["layered.yaml: tiers.unit.docs.example: no file 'tests/nowhere.py' in any "
                                      "folder of docs.examples"], id="a file that is not in the example project is refused"),
])
def test_a_bad_example_is_refused(example, expected):
    assert problems(with_docs(example=example), folders=FILES) == expected


@pytest.mark.parametrize("helpers, expected", [
    pytest.param({"path": BUILDERS}, ["layered.yaml: tiers.unit.docs.helpers: must be a list of paths in an example "
                                      "project"], id="helpers that are not a list are refused"),
    pytest.param([BUILDERS, "tests/../b.py"], ["layered.yaml: tiers.unit.docs.helpers[1]: must be a path in an example "
                                               "project, such as src/billing/charge.py"],
                 id="a bad helper is reported by its place in the list"),
])
def test_bad_helpers_are_refused(helpers, expected):
    assert problems(with_docs(helpers=helpers), folders=FILES) == expected


def test_the_helpers_of_a_tier_load_in_order_each_with_its_note():
    document = covered(docs={"examples": ["ex"], "example_notes": {BUILDERS: "shared"}})
    document["tiers"]["unit"]["docs"] = {"helpers": [BUILDERS, CONFTEST]}
    assert parse(document).tiers[0].helpers == (
        TierExample(("tests", "src", "builders.py"), "ex/" + BUILDERS, "shared"),
        TierExample(("tests", "src", "conftest.py"), "ex/" + CONFTEST))


TIER_TEXTS = {"unit": "def test_a_rule():\n    assert decide()\n\n", "integration": "def test_a_request(): ...\n"}


def rendered(template: str, document: dict | None = None, texts: dict | None = None) -> str:
    return fill(template, parse(document or tiered()), "testing.md",
                tier_examples=TIER_TEXTS if texts is None else texts, file_types=FILE_TYPES)


def template_problems(template: str, document: dict | None = None, texts: dict | None = None) -> list[str]:
    with pytest.raises(InvalidTemplate) as caught:
        rendered(template, document, texts)
    return list(caught.value.problems)


def test_the_tiers_table_shows_each_subject_by_the_path_of_its_parts_or_the_text_the_docs_give():
    assert rendered("{{tiers}}") == (
        "| Tier | Subject | Proves | May touch |\n|---|---|---|---|\n"
        "| unit | `service/` | a rule | nothing |\n"
        "| integration | `src/` but `service/` | a request | the database |")
    assert rendered("{{tiers}}", covered()).splitlines()[3] == "| integration | `api/`, `store/` | a request |  |"


def test_a_tier_with_a_folder_and_no_part_is_shown_by_the_text_of_the_docs():
    document = covered()
    document["tiers"]["guard"] = {"folder": "checks", "docs": {"subject": "the source tree"}}
    assert rendered("{{tiers}}", document).splitlines()[4] == "| guard | the source tree |  |  |"


def test_untested_parts_say_why_in_one_line_each():
    assert rendered("{{untested}}") == "`shared/` gets no tier of its own: reached through the parts that use it."
    document = tiered()
    del document["parts"]["shared"]["untested"]
    document["parts"]["shared"]["tests"] = "integration"
    assert rendered("{{untested}}", document) == ""


def test_each_tiers_litmus_is_a_tip_panel_under_its_numbered_subsection_its_lines_joined():
    assert rendered("{{tier_litmus:3}}") == (
        "### 3.1 unit\n\n> [!TIP]\n> **Litmus test.** Does it decide? If yes, it is a unit test.\n\n"
        "### 3.2 integration\n\n> [!TIP]\n> **Litmus test.** Does it need the database?")
    assert rendered("{{tier_index:3}}") == "  - [[#3.1 unit]]\n  - [[#3.2 integration]]"


def test_the_helpers_of_all_tiers_share_one_block_under_their_paths_each_note_in_parentheses():
    document = tiered()
    document["tiers"]["unit"]["docs"]["helpers"] = [BUILDERS]
    document["tiers"]["integration"]["docs"]["helpers"] = [CONFTEST]
    texts = {**TIER_TEXTS, "ex/" + BUILDERS: "A = 1\n", "ex/" + CONFTEST: "B = 2\n\n"}
    assert rendered("{{tier_helpers}}", document, texts) == (
        "```python\n# tests/src/builders.py (shared)\nA = 1\n\n# tests/src/conftest.py\nB = 2\n```")
    assert template_problems("{{tier_helpers}}") == ["testing.md: {{tier_helpers}}: no tier has `helpers`"]
    assert template_problems("{{tier_helpers}}", document, TIER_TEXTS) == [
        "testing.md: {{tier_helpers}}: the helper file 'ex/tests/src/builders.py', 'ex/tests/src/conftest.py' was "
        "not read"]


def test_the_files_and_data_tables():
    assert rendered("{{tier_files}}") == (
        "| Tier | One file per | Its cases come from |\n|---|---|---|\n"
        "| unit | rule | the invariants |\n| integration | route | its arguments |")
    assert rendered("{{tier_data}}") == (
        "| Tier | Where its data comes from |\n|---|---|\n| unit | built in the test |\n| integration | the seed |")


def test_the_example_tests_share_one_block_each_under_its_tier_and_path_a_note_in_parentheses():
    assert rendered("x\n\n{{tier_examples}}\n") == (
        "x\n\n```python\n"
        "# unit: tests/src/billing/service/test_rules.py (one per rule)\ndef test_a_rule():\n    assert decide()\n\n"
        "# integration: tests/src/test_api.py\ndef test_a_request(): ...\n```\n")
    assert rendered("```python\n{{tier_examples}}\n```").startswith("```python\n# unit: tests/")


def test_a_tier_with_no_example_has_no_entry_in_the_block():
    document = tiered()
    del document["tiers"]["unit"]["docs"]["example"]
    assert rendered("{{tier_examples}}", document) == (
        "```python\n# integration: tests/src/test_api.py\ndef test_a_request(): ...\n```")


def test_what_the_tier_placeholders_need_and_the_file_leaves_out_is_reported():
    document = covered()
    assert template_problems("{{tier_files}}\n{{tier_data}}\n{{tier_examples}}", document) == [
        "testing.md: {{tier_files}}: tier 'unit' has no `one_file_per`, tier 'unit' has no `cases_from`, "
        "tier 'integration' has no `one_file_per`, tier 'integration' has no `cases_from`",
        "testing.md: {{tier_data}}: tier 'unit' has no `data`, tier 'integration' has no `data`",
        "testing.md: {{tier_examples}}: no tier has an `example`"]


def test_every_tier_placeholder_says_when_the_profile_has_no_tiers():
    placeholders = ["{{tiers}}", "{{untested}}", "{{tier_litmus:3}}", "{{tier_files}}", "{{tier_data}}",
                    "{{tier_examples}}"]
    assert template_problems(" ".join(placeholders), layered()) == [
        f"testing.md: {p}: the architecture has no `tiers`" for p in placeholders]


def test_tier_examples_not_read_or_of_mixed_kinds_are_reported():
    assert template_problems("{{tier_examples}}", texts={"unit": "x"}) == [
        "testing.md: {{tier_examples}}: the example of tier 'integration' was not read"]
    document = tiered()
    files = {"ex": (*FILES["ex"], "tests/src/test_api.sql")}
    document["tiers"]["integration"]["docs"]["example"] = "tests/src/test_api.sql"
    with pytest.raises(InvalidTemplate) as caught:
        fill("{{tier_examples}}", parsed(document, folders=files), "testing.md", tier_examples=TIER_TEXTS, file_types=FILE_TYPES)
    assert caught.value.problems == (
        "testing.md: {{tier_examples}}: one block cannot mix files of different kinds (.py, .sql)",)


def test_a_tier_placeholder_with_an_argument_is_unknown():
    assert template_problems("{{tiers:unit}} {{tier_litmus}}")[0].startswith(
        "testing.md: unknown placeholder {{tiers:unit}}")


def test_a_tier_may_name_the_folder_its_tests_live_in_and_has_none_otherwise():
    document = covered()
    document["tiers"]["unit"]["folder"] = "checks/rules"
    assert parsed(document).tiers[0].folder == ("checks", "rules")
    assert parsed(covered()).tiers[0].folder is None


@pytest.mark.parametrize("folder, expected", [
    pytest.param("", [FOLDER_PROBLEM], id="an empty folder is refused"),
    pytest.param(3, [FOLDER_PROBLEM], id="a folder that is not text is refused"),
    pytest.param("/checks", [FOLDER_PROBLEM], id="an absolute folder is refused"),
    pytest.param("checks/", [FOLDER_PROBLEM], id="a folder with an empty step is refused"),
    pytest.param("checks//rules", [FOLDER_PROBLEM], id="a folder with an empty step inside is refused"),
    pytest.param("../checks", [FOLDER_PROBLEM], id="a folder climbing out is refused"),
    pytest.param(".", [FOLDER_PROBLEM], id="the folder itself is refused"),
    pytest.param("checks/*", [FOLDER_PROBLEM], id="a folder with a wildcard is refused"),
    pytest.param("src/billing/api",
                 ["layered.yaml: tiers.unit.folder: 'src/billing/api' is the folder of part 'api', which places its "
                  "tests: give `folder` only to a folder that mirrors no part"],
                 id="the folder of a part is refused, since the part already places its tests"),
])
def test_a_bad_tier_folder_is_refused(folder, expected):
    document = covered()
    document["tiers"]["unit"]["folder"] = folder
    assert problems(document) == expected


@pytest.mark.parametrize("example, expected", [
    pytest.param("tests/checks/rules/test_x.py", [], id="an example inside the folder is fine"),
    pytest.param("tests/checks/test_x.py", [], id="an example directly in the folder is fine"),
    pytest.param("tests/other/test_x.py", [OUTSIDE.format(path="tests/other/test_x.py")],
                 id="an example outside the folder is refused"),
    pytest.param("tests/test_x.py", [OUTSIDE.format(path="tests/test_x.py")],
                 id="an example directly below the tests folder is refused"),
    pytest.param("test_x.py", [OUTSIDE.format(path="test_x.py")],
                 id="an example with no tests folder in its path is refused"),
    pytest.param("tests/checks", [OUTSIDE.format(path="tests/checks")],
                 id="an example whose file name is the folder is refused"),
])
def test_the_example_of_a_tier_with_a_folder_lies_in_it(example, expected):
    document = covered(docs={"examples": ["ex"]})
    document["tiers"]["unit"]["folder"] = "checks"
    document["tiers"]["unit"]["docs"] = {"example": example}
    assert found(document, {"ex": (example,)}) == expected


@pytest.mark.parametrize("first, second, fakes, expected", [
    pytest.param("fakes", "other", "fakes",
                 ["layered.yaml: tiers: the folder 'fakes' of tier 'unit' overlaps the fakes' folder 'fakes': give "
                  "each its own folder"], id="a folder equal to the fakes' folder is refused"),
    pytest.param("fakes/db", "other", "fakes",
                 ["layered.yaml: tiers: the folder 'fakes/db' of tier 'unit' overlaps the fakes' folder 'fakes': give "
                  "each its own folder"], id="a folder inside the fakes' folder is refused"),
    pytest.param("fakes", "other", "fakes/db",
                 ["layered.yaml: tiers: the folder 'fakes' of tier 'unit' overlaps the fakes' folder 'fakes/db': give "
                  "each its own folder"], id="a folder holding the fakes' folder is refused"),
    pytest.param("checks", "checks", "fakes",
                 ["layered.yaml: tiers: the folder 'checks' of tier 'integration' overlaps the folder 'checks' of "
                  "tier 'unit': give each its own folder"], id="two tiers with the same folder are refused"),
    pytest.param("checks", "checks/rules", "fakes",
                 ["layered.yaml: tiers: the folder 'checks/rules' of tier 'integration' overlaps the folder 'checks' "
                  "of tier 'unit': give each its own folder"], id="a folder inside another tier's is refused"),
    pytest.param("checks", "other", "fakes", [], id="folders that do not overlap are fine"),
    pytest.param("checks", "chec", "fakes", [], id="a folder that only starts like another is not inside it"),
])
def test_the_folders_of_tiers_overlap_neither_the_fakes_nor_each_other(first, second, fakes, expected):
    document = covered(fakes={"folder": fakes, "for": ["store"]})
    document["tiers"]["unit"]["folder"] = first
    document["tiers"]["integration"]["folder"] = second
    assert found(document) == expected


def test_a_tier_with_no_folder_has_no_allowance_of_its_own():
    assert [tier.may_import for tier in parsed(covered()).tiers] == [None, None]
