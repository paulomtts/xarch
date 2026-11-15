"""The test tiers of an architecture file: parsed, validated, and every part covered or marked untested."""
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_architectures, load_architecture
from xarch.modules.spec.application.logic.example_imports import example_problems
from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidArchitecture, InvalidTemplate
from xarch.modules.spec.domain.values import Subject, Tier, TierExample

DOCS = Path(__file__).resolve().parents[4] / "docs"


def layered(*tiers: dict, **parts: dict) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"api": {}, "service": {}, "store": {}}}, "shared": {}},
        "parts": {"api": {"path": "src/*/api", "role": "HTTP handlers"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "store": {"path": "src/*/store", "role": "database access"},
                  "shared": {"path": "shared", "role": "shared code",
                             "untested": "reached through the parts that use it"}} | parts,
        "rules": {},
        "tiers": list(tiers) or [unit(), integration()],
    }


def unit(**extra) -> dict:
    return {"name": "unit", "subject": ["service", "service/rules"], "proves": "a rule", "may_touch": "nothing",
            "litmus": "Does it decide?\nIf yes, it is a unit test.\n"} | extra


def integration(**extra) -> dict:
    return {"name": "integration", "subject": ["api", "store"], "proves": "a request", "may_touch": "the database",
            "litmus": "Does it need the database?"} | extra


def parsed(document: dict, has_file=lambda relative: True):
    return parse_architecture(document, "layered.yaml", has_file)


def problems(document: dict, has_file=lambda relative: True) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        parsed(document, has_file)
    return list(caught.value.problems)


def test_tiers_load_in_order_with_their_subjects_and_example():
    """A litmus test keeps its lines as written, with the trailing newline trimmed."""
    example = {"path": "tests/src/test_api.py", "file": "examples/api.py", "note": " (one per route)"}
    architecture = parsed(layered(unit(), integration(subject_text="the edges", one_file_per="route",
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
    document = layered()
    del document["tiers"]
    assert parsed(document).tiers == ()


def test_a_tier_with_no_part_in_its_subject_is_shown_by_its_text():
    guard = {"name": "guard", "subject": [], "subject_text": "the source tree", "proves": "a rule holds",
             "may_touch": "the tree", "litmus": "Does it read the source?"}
    assert parsed(layered(unit(), integration(), guard)).tiers[2].subject == ()
    del guard["subject_text"]
    assert problems(layered(unit(), integration(), guard)) == [
        "layered.yaml: tiers[2]: a subject with no part needs `subject_text`, such as 'the source tree'"]


def test_a_part_no_tier_tests_is_rejected_naming_it():
    assert problems(layered(unit(), integration(subject=["api"]))) == [
        "layered.yaml: tiers: no tier tests part 'store': add it to a tier's subject, "
        "or give the part `untested: <reason>`"]


def test_a_part_both_tested_and_untested_is_rejected():
    assert problems(layered(unit(), integration(subject=["api", "store", "shared"]))) == [
        "layered.yaml: tiers: part 'shared' is in the subject of tier 'integration' and is marked `untested`: drop one"]


def test_a_sub_path_of_a_part_covers_the_part():
    assert parsed(layered(unit(subject=["service/rules"]), integration())).tiers[0].subject == (
        Subject("service", ("rules",)),)


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_every_part_of_a_bundled_architecture_is_tested_or_says_why_not(profile):
    """Rendering tests the entry point."""
    architecture = load_architecture(profile)
    tested = {subject.part for tier in architecture.tiers for subject in tier.subject}
    untested = {name for name, part in architecture.parts.items() if part.untested}
    assert tested | untested == set(architecture.parts) and not tested & untested
    assert untested == {"platform", "bootstrap"}
    assert [tier.name for tier in architecture.tiers] == ["unit", "integration", "rendering",
                                                          "guard"]
    assert architecture.tiers[2].subject[0] == Subject(profile)
    assert all(tier.litmus and tier.example for tier in architecture.tiers)


def test_a_subject_naming_no_part_or_a_bad_path_is_rejected():
    assert problems(layered(unit(subject=["service", "repo", "service/../x", "store/", 3]), integration())) == [
        "layered.yaml: tiers[0].subject: no part named 'repo'",
        "layered.yaml: tiers[0].subject: 'service/../x' has an invalid path after the part",
        "layered.yaml: tiers[0].subject: 'store/' has an invalid path after the part",
        "layered.yaml: tiers[0].subject: no part named 3",
    ]
    assert problems(layered(unit(subject="service"), integration(subject=["api", "store", "service"]))) == [
        "layered.yaml: tiers[0].subject: must be a list of parts, each optionally followed by /<path>, "
        "such as [api, shared/text]"]


def test_duplicate_tier_names_are_rejected():
    assert problems(layered(unit(), integration(), unit(subject=["api"]))) == [
        "layered.yaml: tiers[2]: tier 'unit' is listed twice"]


def test_a_tier_missing_its_litmus_or_another_required_key_is_rejected():
    tier = unit()
    del tier["litmus"], tier["proves"]
    assert problems(layered(tier, integration())) == [
        "layered.yaml: tiers[0]: missing `proves`", "layered.yaml: tiers[0]: missing `litmus`"]
    assert problems(layered(unit(litmus="  "), integration())) == [
        "layered.yaml: tiers[0].litmus: must be text: the question that tells a test belongs to the tier"]


def test_bad_tier_keys_and_texts_are_rejected():
    assert problems(layered(unit(colour="red", proves="two\nlines", data=3, name=""), integration())) == [
        "layered.yaml: tiers[0]: unknown key 'colour': use cases_from, data, example, helpers, litmus, may_touch, name, "
        "one_file_per, proves, subject, subject_text",
        "layered.yaml: tiers[0].name: must be one line of text, such as 'unit'",
        "layered.yaml: tiers[0].proves: must be one line of text",
        "layered.yaml: tiers[0].data: must be one line of text",
    ]
    assert problems(layered(unit(), integration(), "unit")) == [
        "layered.yaml: tiers[2]: must be a mapping with `name`, `subject`, `proves`, `may_touch` and `litmus`"]
    for value in ([], {}, "unit"):
        document = layered()
        document["tiers"] = value
        assert problems(document) == [
            "layered.yaml: tiers: must be a list of tiers such as {name, subject, proves, may_touch, litmus}, "
            "in the order their litmus tests run"]


def test_a_bad_untested_reason_is_rejected():
    assert problems(layered(shared={"path": "shared", "role": "r", "untested": ""})) == [
        "layered.yaml: parts.shared.untested: must be one line of text: why no tier tests the part",
        "layered.yaml: tiers: no tier tests part 'shared': add it to a tier's subject, "
        "or give the part `untested: <reason>`",
    ]


def test_a_bad_example_path_or_file_is_rejected():
    bad = [{"path": "tests/../x.py", "file": "examples/x.py"}, {"path": "tests/x.py", "file": "nowhere.py"},
           {"file": "examples/x.py", "code": "pass", "note": "two\nlines"}, "examples/x.py"]
    for i, example in enumerate(bad):
        document = layered(unit(example=example), integration())
        assert problems(document, lambda relative: relative != "nowhere.py") == [
            ["layered.yaml: tiers[0].example.path: must be a path such as "
             "'tests/src/billing/api/test_invoice.py'"],
            ["layered.yaml: tiers[0].example.file: no file 'nowhere.py' next to the architecture file"],
            ["layered.yaml: tiers[0].example: unknown key 'code': use file, note, path",
             "layered.yaml: tiers[0].example: missing `path`",
             "layered.yaml: tiers[0].example.note: must be one line of text"],
            ["layered.yaml: tiers[0].example: must be a mapping with `path` and `file`, and optionally `note`"],
        ][i]


def test_a_missing_testing_template_is_rejected():
    document = layered() | {"docs": {"architecture.md": {"from": "layered.md"}, "testing.md": {"from": "testing.md"}}}
    assert problems(document, lambda relative: relative == "layered.md") == [
        "layered.yaml: docs.testing.md.from: no file 'testing.md' next to the architecture file"]


def tiered() -> dict:
    example = {"path": "tests/src/billing/service/test_rules.py", "file": "x/unit.py", "note": " (one per rule)"}
    return layered(
        unit(one_file_per="rule", cases_from="the invariants", data="built in the test", example=example),
        integration(subject_text="`src/` but `service/`", one_file_per="route", cases_from="its arguments",
                    data="the seed", example={"path": "tests/src/test_api.py", "file": "x/integration.py"}))


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
    document = layered(unit(subject=["store", "service", "service/rules", "service/x.py"]), integration())
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
    document = layered()
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


def test_a_tier_example_under_tests_is_only_parsed_and_one_in_a_part_obeys_its_rules():
    """A tier example whose path lies in a part (here service) obeys that part's rules."""
    document = tiered()
    document["rules"] = {"service": ["service@own"]}
    document["tiers"][1]["example"]["path"] = "src/billing/service/test_api.py"
    architecture = parsed(document)
    texts = {"unit": "from app.src.tax.store import anything\n", "integration": "from app.src.tax.store import x\n"}
    assert example_problems(architecture, {}, texts) == [
        "tier integration's example (src/billing/service/test_api.py): imports app.src.tax.store which service may "
        "not import (rules.service)"]
    assert example_problems(architecture, {}, {"unit": "def f(:\n"}) == [
        "tier unit's example (tests/src/billing/service/test_rules.py): is not valid Python: invalid syntax (line 1)"]


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_bundled_tier_examples_pass_the_example_check(profile):
    assert build_architectures().check_examples(profile) == ()


CUSTOM = """\
xarch: 1
name: layered
layout: {src: {singular: module, each: {api: {}, store: {}}}, shared: {}}
parts:
  api:    {path: "src/*/api", role: handlers, entry: true}
  store:  {path: "src/*/store", role: database access}
  shared: {path: shared, role: helpers, untested: reached through the parts that use it}
rules: {api: [store@own]}
tiers:
  - name: unit
    subject: [store]
    proves: a query
    may_touch: an in-memory database
    litmus: |
      Does it query?
      If yes, it is a unit test.
    data: built in the test
    example: {path: tests/store/test_store.py, file: examples/unit.py}
  - name: driver
    subject: [api]
    proves: routing
    may_touch: a fake store
    litmus: Does it route?
    data: none
    example: {path: tests/api/test_api.py, file: examples/driver.py, note: ", one per route"}
docs:
  architecture.md: {from: layered.md}
  testing.md: {from: layered-testing.md}
"""


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_a_custom_architecture_with_its_own_tiers_gets_its_own_testing_md(tmp_path):
    write(tmp_path / "layered.md", "# Layered\n")
    write(tmp_path / "layered-testing.md", "# Testing of {{entry}}\n\n{{tiers}}\n\n{{untested}}\n\n{{tier_litmus:3}}\n\n"
                                          "Run it: `<command>`\n\n{{tier_data}}\n\n{{tier_examples}}\n")
    write(tmp_path / "examples" / "unit.py", "def test_a_query(): ...\n")
    write(tmp_path / "examples" / "driver.py", "def test_a_route(): ...\n")
    docs = build_architectures().docs(write(tmp_path / "layered.yaml", CUSTOM))
    texts = {"/".join(f.path): f.template for f in docs.files}
    assert texts["testing.md"] == (
        "# Testing of src/*/api\n\n"
        "| Tier | Subject | Proves | May touch |\n|---|---|---|---|\n"
        "| unit | `store/` | a query | an in-memory database |\n"
        "| driver | `api/` | routing | a fake store |\n\n"
        "`shared/` gets no tier of its own: reached through the parts that use it.\n\n"
        "### 3.1 unit\n\n> [!TIP]\n> **Litmus test.** Does it query? If yes, it is a unit test.\n\n"
        "### 3.2 driver\n\n> [!TIP]\n> **Litmus test.** Does it route?\n\n"
        "Run it: `<command>`\n\n"
        "| Tier | Where its data comes from |\n|---|---|\n| unit | built in the test |\n| driver | none |\n\n"
        "```python\n# unit: tests/store/test_store.py\ndef test_a_query(): ...\n\n"
        "# driver: tests/api/test_api.py, one per route\ndef test_a_route(): ...\n```\n")
    assert [f.path for f in docs.files] == [("architecture.md",), ("testing.md",)]


def test_a_custom_testing_template_with_a_bad_placeholder_fails_naming_it(tmp_path):
    write(tmp_path / "layered.md", "# Layered\n")
    write(tmp_path / "layered-testing.md", "{{tier_files}}\n{{tier}}\n")
    write(tmp_path / "examples" / "unit.py", "")
    write(tmp_path / "examples" / "driver.py", "")
    with pytest.raises(InvalidTemplate) as caught:
        build_architectures().docs(write(tmp_path / "layered.yaml", CUSTOM))
    assert caught.value.problems[0] == (
        "layered-testing.md: {{tier_files}}: tier 'unit' has no `one_file_per`, tier 'unit' has no `cases_from`, "
        "tier 'driver' has no `one_file_per`, tier 'driver' has no `cases_from`")
    assert caught.value.problems[1].startswith("layered-testing.md: unknown placeholder {{tier}}: use {{tree}}")


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_bundled_tiers_and_testing_template_generate_the_checked_in_testing_md(profile):
    generated = {"/".join(f.path): f.template for f in build_architectures().docs(profile).files}
    assert generated["testing.md"] == (DOCS / profile / "testing.md").read_text(encoding="utf-8")
