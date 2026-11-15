"""The test tiers of an architecture file: parsed, validated, and every part covered or marked untested."""

import pytest

from tests.modules.spec.builders import integration, layered_tiers, parsed, problems, tiered, unit
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidTemplate
from xarch.modules.spec.domain.values import Subject, Tier, TierExample


def test_tiers_load_in_order_with_their_subjects_and_example():
    """A litmus test keeps its lines as written, with the trailing newline trimmed."""
    example = {"path": "tests/src/test_api.py", "file": "examples/api.py", "note": " (one per route)"}
    architecture = parsed(layered_tiers(unit(), integration(subject_text="the edges", one_file_per="route",
                                                      cases_from="its arguments", data="the test", example=example)))
    assert architecture.tiers == (
        Tier("unit", (Subject("service"), Subject("service", ("rules",))), "a rule", "nothing",
             "Does it decide?\nIf yes, it is a unit test."),
        Tier("integration", (Subject("api"), Subject("store")), "a request", "the database",
             "Does it need the database?", "the edges", "route", "its arguments", "the test",
             TierExample(("tests", "src", "test_api.py"), "examples/api.py", " (one per route)")),
    )
    assert architecture.parts["shared"].untested == "reached through the parts that use it"


def test_tiers_are_optional_and_without_them_no_part_needs_a_tier():
    document = layered_tiers()
    del document["tiers"]
    assert parsed(document).tiers == ()


def test_a_tier_with_no_part_in_its_subject_is_shown_by_its_text():
    guard = {"name": "guard", "subject": [], "subject_text": "the source tree", "proves": "a rule holds",
             "may_touch": "the tree", "litmus": "Does it read the source?"}
    assert parsed(layered_tiers(unit(), integration(), guard)).tiers[2].subject == ()
    del guard["subject_text"]
    assert problems(layered_tiers(unit(), integration(), guard)) == [
        "layered.yaml: tiers[2]: a subject with no part needs `subject_text`, such as 'the source tree'"]


def test_a_part_no_tier_tests_is_rejected_naming_it():
    assert problems(layered_tiers(unit(), integration(subject=["api"]))) == [
        "layered.yaml: tiers: no tier tests part 'store': add it to a tier's subject, "
        "or give the part `untested: <reason>`"]


def test_a_part_both_tested_and_untested_is_rejected():
    assert problems(layered_tiers(unit(), integration(subject=["api", "store", "shared"]))) == [
        "layered.yaml: tiers: part 'shared' is in the subject of tier 'integration' and is marked `untested`: drop one"]


def test_a_sub_path_of_a_part_covers_the_part():
    assert parsed(layered_tiers(unit(subject=["service/rules"]), integration())).tiers[0].subject == (
        Subject("service", ("rules",)),)


def test_a_subject_naming_no_part_or_a_bad_path_is_rejected():
    assert problems(layered_tiers(unit(subject=["service", "repo", "service/../x", "store/", 3]), integration())) == [
        "layered.yaml: tiers[0].subject: no part named 'repo'",
        "layered.yaml: tiers[0].subject: 'service/../x' has an invalid path after the part",
        "layered.yaml: tiers[0].subject: 'store/' has an invalid path after the part",
        "layered.yaml: tiers[0].subject: no part named 3",
    ]
    assert problems(layered_tiers(unit(subject="service"), integration(subject=["api", "store", "service"]))) == [
        "layered.yaml: tiers[0].subject: must be a list of parts, each optionally followed by /<path>, "
        "such as [api, shared/text]"]


def test_a_tier_names_the_parts_its_tests_use_as_types_only():
    assert parsed(layered_tiers(unit(), integration(types_only=["service"]))).tiers[1].types_only == ("service",)
    assert parsed(layered_tiers()).tiers[1].types_only == ()


def test_a_bad_types_only_entry_is_rejected():
    assert problems(layered_tiers(unit(), integration(types_only=["repo", "service", "service"]))) == [
        "layered.yaml: tiers[1].types_only: no part named 'repo'",
        "layered.yaml: tiers[1].types_only: 'service' is listed twice"]
    assert problems(layered_tiers(unit(), integration(types_only="service"))) == [
        "layered.yaml: tiers[1].types_only: must be a list of part names"]
    assert problems(layered_tiers(unit(), integration(types_only=[]))) == [
        "layered.yaml: tiers[1].types_only: must be a list of part names"]


def test_duplicate_tier_names_are_rejected():
    assert problems(layered_tiers(unit(), integration(), unit(subject=["api"]))) == [
        "layered.yaml: tiers[2]: tier 'unit' is listed twice"]


def test_a_tier_missing_its_litmus_or_another_required_key_is_rejected():
    tier = unit()
    del tier["litmus"], tier["proves"]
    assert problems(layered_tiers(tier, integration())) == [
        "layered.yaml: tiers[0]: missing `proves`", "layered.yaml: tiers[0]: missing `litmus`"]
    assert problems(layered_tiers(unit(litmus="  "), integration())) == [
        "layered.yaml: tiers[0].litmus: must be text: the question that tells a test belongs to the tier"]


def test_bad_tier_keys_and_texts_are_rejected():
    assert problems(layered_tiers(unit(colour="red", proves="two\nlines", data=3, name=""), integration())) == [
        "layered.yaml: tiers[0]: unknown key 'colour': use cases_from, data, example, forbidden, helpers, litmus, may_touch, name, "
        "one_file_per, proves, subject, subject_text, types_only",
        "layered.yaml: tiers[0].name: must be one line of text, such as 'unit'",
        "layered.yaml: tiers[0].proves: must be one line of text",
        "layered.yaml: tiers[0].data: must be one line of text",
    ]
    assert problems(layered_tiers(unit(), integration(), "unit")) == [
        "layered.yaml: tiers[2]: must be a mapping with `name`, `subject`, `proves`, `may_touch` and `litmus`"]


@pytest.mark.parametrize("value", [pytest.param([], id="an empty list"), pytest.param({}, id="a mapping"),
                                   pytest.param("unit", id="a string")])
def test_tiers_that_are_not_a_list_of_tiers_are_rejected(value):
    assert problems(layered_tiers() | {"tiers": value}) == [
        "layered.yaml: tiers: must be a list of tiers such as {name, subject, proves, may_touch, litmus}, "
        "in the order their litmus tests run"]


def test_a_bad_untested_reason_is_rejected():
    assert problems(layered_tiers(shared={"path": "shared", "role": "r", "untested": ""})) == [
        "layered.yaml: parts.shared.untested: must be one line of text: why no tier tests the part",
        "layered.yaml: tiers: no tier tests part 'shared': add it to a tier's subject, "
        "or give the part `untested: <reason>`",
    ]


@pytest.mark.parametrize("example, expected", [
    pytest.param({"path": "tests/../x.py", "file": "examples/x.py"},
                 ["layered.yaml: tiers[0].example.path: must be a path such as "
                  "'tests/src/billing/api/invoice_checks.py'"], id="a path climbing out is rejected"),
    pytest.param({"path": "tests/src/*/test_x.py", "file": "examples/x.py"},
                 ["layered.yaml: tiers[0].example.path: must be a path such as "
                  "'tests/src/billing/api/invoice_checks.py'"], id="a path naming no instance is rejected"),
    pytest.param({"path": "", "file": "examples/x.py"},
                 ["layered.yaml: tiers[0].example.path: must be a path such as "
                  "'tests/src/billing/api/invoice_checks.py'"], id="an empty path is rejected"),
    pytest.param({"path": "tests/x.py", "file": "nowhere.py"},
                 ["layered.yaml: tiers[0].example.file: no file 'nowhere.py' next to the architecture file"],
                 id="a file that is not there is rejected"),
    pytest.param({"path": "tests/x.py", "file": ""}, ["layered.yaml: tiers[0].example.file: must be a file name"],
                 id="an empty file name is rejected"),
    pytest.param({"file": "examples/x.py", "code": "pass", "note": "two\nlines"},
                 ["layered.yaml: tiers[0].example: unknown key 'code': use file, note, path",
                  "layered.yaml: tiers[0].example: missing `path`",
                  "layered.yaml: tiers[0].example.note: must be one line of text"],
                 id="an unknown key, a missing path and a note of two lines are rejected"),
    pytest.param("examples/x.py",
                 ["layered.yaml: tiers[0].example: must be a mapping with `path` and `file`, and optionally `note`"],
                 id="an example that is not a mapping is rejected"),
])
def test_a_bad_example_is_rejected(example, expected):
    assert problems(layered_tiers(unit(example=example), integration()), lambda relative: relative != "nowhere.py") == expected


@pytest.mark.parametrize("helpers, expected", [
    pytest.param({"path": "tests/src/builders.py", "file": "x/builders.py"},
                 ["layered.yaml: tiers[0].helpers: must be a list of files such as {path, file}"],
                 id="helpers that are not a list are rejected"),
    pytest.param([{"path": "tests/src/builders.py", "file": "x/builders.py"}, {"path": "tests/../b.py", "file": "b.py"}],
                 ["layered.yaml: tiers[0].helpers[1].path: must be a path such as "
                  "'tests/src/billing/api/invoice_checks.py'"],
                 id="a bad helper is reported by its place in the list"),
])
def test_bad_helpers_are_rejected(helpers, expected):
    assert problems(layered_tiers(unit(helpers=helpers), integration())) == expected


def test_a_tiers_helpers_load_in_order():
    helpers = [{"path": "tests/src/builders.py", "file": "x/builders.py", "note": " (shared)"},
               {"path": "tests/src/conftest.py", "file": "x/conftest.py"}]
    assert parsed(layered_tiers(unit(helpers=helpers), integration())).tiers[0].helpers == (
        TierExample(("tests", "src", "builders.py"), "x/builders.py", " (shared)"),
        TierExample(("tests", "src", "conftest.py"), "x/conftest.py"))


def test_a_missing_testing_template_is_rejected():
    document = layered_tiers() | {"docs": {"architecture.md": {"from": "layered.md"}, "testing.md": {"from": "testing.md"}}}
    assert problems(document, lambda relative: relative == "layered.md") == [
        "layered.yaml: docs.testing.md.from: no file 'testing.md' next to the architecture file"]


TIER_TEXTS = {"unit": "def test_a_rule():\n    assert decide()\n\n", "integration": "def test_a_request(): ...\n"}


def rendered(template: str, document: dict | None = None, texts: dict | None = None) -> str:
    architecture = parsed(document or tiered())
    return fill(template, architecture, "testing.md", tier_examples=TIER_TEXTS if texts is None else texts)


def template_problems(template: str, document: dict | None = None, texts: dict | None = None) -> list[str]:
    with pytest.raises(InvalidTemplate) as caught:
        rendered(template, document, texts)
    return list(caught.value.problems)


def test_the_tiers_table_shows_each_subject_by_path_a_parts_sub_paths_joined_by_and():
    assert rendered("{{tiers}}") == (
        "| Tier | Subject | Proves | May touch |\n|---|---|---|---|\n"
        "| unit | `service/` and `service/rules/` | a rule | nothing |\n"
        "| integration | `src/` but `service/` | a request | the database |")
    document = layered_tiers(unit(subject=["store", "service", "service/rules", "service/x.py"]), integration())
    document["layout"]["src"]["each"]["service"] = {"x.py": "file"}
    assert rendered("{{tiers}}", document).splitlines()[2] == (
        "| unit | `store/`, `service/`, `service/rules/` and `service/x.py` | a rule | nothing |")


def test_untested_parts_say_why_in_one_line_each():
    assert rendered("{{untested}}") == "`shared/` gets no tier of its own: reached through the parts that use it."
    document = tiered()
    del document["parts"]["shared"]["untested"]
    document["tiers"][1]["subject"].append("shared")
    assert rendered("{{untested}}", document) == ""


def test_each_tiers_litmus_is_a_tip_panel_under_its_numbered_subsection_its_lines_joined():
    assert rendered("{{tier_litmus:3}}") == (
        "### 3.1 unit\n\n> [!TIP]\n> **Litmus test.** Does it decide? If yes, it is a unit test.\n\n"
        "### 3.2 integration\n\n> [!TIP]\n> **Litmus test.** Does it need the database?")
    assert rendered("{{tier_index:3}}") == "  - [[#3.1 unit]]\n  - [[#3.2 integration]]"


def test_the_helpers_of_all_tiers_share_one_block_under_their_paths():
    document = tiered()
    document["tiers"][0]["helpers"] = [{"path": "tests/src/builders.py", "file": "x/builders.py", "note": " (shared)"}]
    document["tiers"][1]["helpers"] = [{"path": "tests/src/conftest.py", "file": "x/conftest.py"}]
    texts = {**TIER_TEXTS, "x/builders.py": "A = 1\n", "x/conftest.py": "B = 2\n\n"}
    assert rendered("{{tier_helpers}}", document, texts) == (
        "```python\n# tests/src/builders.py (shared)\nA = 1\n\n# tests/src/conftest.py\nB = 2\n```")
    assert template_problems("{{tier_helpers}}") == ["testing.md: {{tier_helpers}}: no tier has `helpers`"]
    assert template_problems("{{tier_helpers}}", document, TIER_TEXTS) == [
        "testing.md: {{tier_helpers}}: the helper file 'x/builders.py', 'x/conftest.py' was not read"]


def test_the_files_and_data_tables():
    assert rendered("{{tier_files}}") == (
        "| Tier | One file per | Its cases come from |\n|---|---|---|\n"
        "| unit | rule | the invariants |\n| integration | route | its arguments |")
    assert rendered("{{tier_data}}") == (
        "| Tier | Where its data comes from |\n|---|---|\n| unit | built in the test |\n| integration | the seed |")


def test_the_example_tests_share_one_block_each_under_its_tier_and_path():
    """A tier with no example has no entry in the block."""
    assert rendered("x\n\n{{tier_examples}}\n") == (
        "x\n\n```python\n"
        "# unit: tests/src/billing/service/test_rules.py (one per rule)\ndef test_a_rule():\n    assert decide()\n\n"
        "# integration: tests/src/test_api.py\ndef test_a_request(): ...\n```\n")
    assert rendered("```python\n{{tier_examples}}\n```").startswith("```python\n# unit: tests/")
    document = tiered()
    del document["tiers"][0]["example"]
    assert rendered("{{tier_examples}}", document) == (
        "```python\n# integration: tests/src/test_api.py\ndef test_a_request(): ...\n```")


def test_what_the_tier_placeholders_need_and_the_file_leaves_out_is_reported():
    document = layered_tiers()
    assert template_problems("{{tier_files}}\n{{tier_data}}\n{{tier_examples}}", document) == [
        "testing.md: {{tier_files}}: tier 'unit' has no `one_file_per`, tier 'unit' has no `cases_from`, "
        "tier 'integration' has no `one_file_per`, tier 'integration' has no `cases_from`",
        "testing.md: {{tier_data}}: tier 'unit' has no `data`, tier 'integration' has no `data`",
        "testing.md: {{tier_examples}}: no tier has an `example`",
    ]
    del document["tiers"]
    del document["parts"]["shared"]["untested"]
    placeholders = ["{{tiers}}", "{{untested}}", "{{tier_litmus:3}}", "{{tier_files}}", "{{tier_data}}",
                    "{{tier_examples}}"]
    assert template_problems(" ".join(placeholders), document) == [
        f"testing.md: {p}: the architecture has no `tiers`" for p in placeholders]


def test_tier_examples_not_read_or_of_mixed_kinds_are_reported():
    assert template_problems("{{tier_examples}}", texts={"unit": "x"}) == [
        "testing.md: {{tier_examples}}: the example of tier 'integration' was not read"]
    document = tiered()
    document["tiers"][1]["example"]["file"] = "x/integration.sql"
    assert template_problems("{{tier_examples}}", document) == [
        "testing.md: {{tier_examples}}: one block cannot mix files of different kinds (.py, .sql)"]


def test_a_tier_placeholder_with_an_argument_is_unknown():
    assert template_problems("{{tiers:unit}} {{tier_litmus}}")[0].startswith(
        "testing.md: unknown placeholder {{tiers:unit}}")
