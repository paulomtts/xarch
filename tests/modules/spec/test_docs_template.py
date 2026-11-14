"""Filling a docs template from an architecture file: the bundled ones reproduce the checked-in docs byte for byte."""
from importlib import resources
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_architectures, load_architecture
from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidTemplate

DOCS = Path(__file__).resolve().parents[3] / "docs"


def layered(**extra) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"each": {"api.py": "file", "service": {}, "store": {"sql": {}}}}, "shared": {}},
        "notes": {"src/*/store/sql": "the queries"},
        "parts": {"shared": {"path": "shared", "role": "code every module uses", "litmus": "Is it shared?"},
                  "store": {"path": "src/*/store", "role": "database access", "litmus": "Does it touch the database?"},
                  "service": {"path": "src/*/service", "role": "business logic", "litmus": "Does it decide?"},
                  "api": {"path": "src/*/api.py", "role": "HTTP handlers", "litmus": "Does it parse a request?",
                          "entry": True, "driver_proves": "routing", "driver_test": {"file": "driver.py"}}},
        "rules": {"shared": ["shared"], "store": ["store@own", "shared/text"],
                  "service": ["service@own", "store@own", "api@any", "shared"], "api": ["*"]},
        "layers": {"inside": ["store", "service"]},
        "placement": ["store", "service", "api", "shared"],
        "naming": [{"kind": "service", "where": ["service/"], "pattern": "thing and `Service`",
                    "example": ["BillingService", "TaxService"]}],
    } | extra


def filled(template: str, driver_test: str | None = "def test_api(): ...\n", **extra) -> str:
    return fill(template, parse_architecture(layered(**extra), "layered.yaml", lambda r: True), "layered.md",
                driver_test)


def problems(template: str, **extra) -> list[str]:
    with pytest.raises(InvalidTemplate) as caught:
        filled(template, **extra)
    assert caught.value.reason == "\n".join(caught.value.problems)
    return list(caught.value.problems)


# --- the bundled architectures are the checked-in docs ---


@pytest.mark.parametrize("profile", ["cli", "web"])
@pytest.mark.parametrize("doc", ["architecture.md", "testing.md"])
def test_the_bundled_architecture_and_template_generate_the_checked_in_docs(profile, doc):
    generated = {"/".join(f.path): f.template for f in build_architectures().docs(profile).files}
    assert generated[doc] == (DOCS / profile / doc).read_text(encoding="utf-8")


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_bundled_template_holds_no_hand_typed_structure(profile):
    template = resources.files("xarch").joinpath("architectures", f"{profile}.md").read_text(encoding="utf-8")
    for placeholder in ["{{tree}}", "{{rules_table}}", "{{layers:application}}", "{{layers:edge}}", "{{placement}}",
                        "{{naming}}"]:
        assert template.count(placeholder) == 1, placeholder
    for part in load_architecture(profile).parts:
        assert template.count(f"{{{{litmus:{part}}}}}") == 1, part
    assert "**Litmus test.** Does it" not in template and "├──" not in template.split("tests/")[0]


# --- each placeholder ---


def test_the_tree_shows_each_folder_once_with_its_role_or_note_aligned():
    assert filled("app/\n{{tree}}\n") == (
        "app/\n"
        "├── src/\n"
        "│   └── <module>/\n"
        "│       ├── api.py     HTTP handlers\n"
        "│       ├── service/   business logic\n"
        "│       └── store/     database access\n"
        "│           └── sql/   the queries\n"                   # the longest line, then three spaces
        "└── shared/            code every module uses\n")


def test_the_rules_table_lists_each_part_in_order_without_itself():
    assert filled("{{rules_table}}") == (
        "| Part | May import |\n"
        "|---|---|\n"
        "| `shared/` | nothing |\n"
        "| `store/` | `shared/text` |\n"
        "| `service/` | its own module's `store/`, any module's `api.py`, `shared/` |\n"
        "| `api.py` | everything |")


def test_consecutive_targets_in_one_scope_share_their_phrase():
    rules = {"shared": [], "store": [], "api": [],
             "service": ["store@own", "api@own", "shared", "store@any", "api@any"]}
    assert filled("{{rules_table}}", rules=rules).splitlines()[4] == (
        "| `service/` | its own module's `store/` and `api.py`, `shared/`, any module's `store/` and `api.py` |")


def test_layers_placement_litmus_and_naming():
    assert filled("{{layers:inside}}") == "`store/` → `service/`"
    assert filled("{{placement}}") == "`store` → `service` → `api` → `shared`"
    assert filled("x\n{{litmus:store}}\ny") == "x\n> [!TIP]\n> **Litmus test.** Does it touch the database?\ny"
    assert filled("{{naming}}") == ("| Kind | Where | Pattern | Example |\n|---|---|---|---|\n"
                                    "| service | `service/` | thing and `Service` | `BillingService`, `TaxService` |")


def test_the_entry_point_and_its_driver():
    assert filled("tests/{{entry}}/: {{driver_proves}}\n{{driver_test}}") == (
        "tests/src/*/api.py/: routing\ndef test_api(): ...\n")


def test_unused_placeholders_and_single_braces_are_fine():
    assert filled("def f(): return {}  # {x} {{ not one }") == "def f(): return {}  # {x} {{ not one }"
    assert filled("{{ placement }}") == filled("{{placement}}")


# --- a template that cannot be filled fails with every problem, never a traceback ---


def test_an_unknown_placeholder_is_rejected():
    assert problems("{{tree}} {{trees}} {{litmus}} {{tree:x}}") == [
        f"layered.md: unknown placeholder {p}: use {{{{tree}}}}, {{{{rules_table}}}}, {{{{layers:<name>}}}}, "
        "{{placement}}, {{litmus:<part>}}, {{naming}}, {{entry}}, {{driver_proves}}, {{driver_test}}"
        for p in ["{{trees}}", "{{litmus}}", "{{tree:x}}"]]


def test_a_part_or_layer_the_file_does_not_define_is_rejected():
    assert problems("{{litmus:repo}}\n{{litmus:store}}\n{{layers:outside}}") == [
        "layered.md: {{litmus:repo}}: the architecture defines no part 'repo'",
        "layered.md: {{layers:outside}}: the architecture has no layer 'outside' (its layers: inside)",
    ]


def test_what_the_file_leaves_out_is_reported_when_a_placeholder_needs_it():
    document = layered()
    for key in ("placement", "naming"):
        del document[key]
    api = document["parts"]["api"]
    for key in ("entry", "driver_proves", "driver_test"):
        del api[key]
    document["parts"]["shared"]["litmus"] = ""
    with pytest.raises(InvalidTemplate) as caught:
        fill("{{placement}}{{naming}}{{entry}}{{litmus:shared}}", parse_architecture(document, "l.yaml", lambda r: True),
             "layered.md")
    assert caught.value.problems == (
        "layered.md: {{placement}}: the architecture has no `placement`",
        "layered.md: {{naming}}: the architecture has no `naming`",
        "layered.md: {{entry}}: no part is the entry point: mark one `entry: true`",
        "layered.md: {{litmus:shared}}: part 'shared' has no litmus test",
    )


def test_a_driver_test_the_file_does_not_give_is_reported():
    assert problems("{{driver_test}}", driver_test=None) == [
        "layered.md: {{driver_test}}: the entry point 'api' has no `driver_test`"]


# --- through the service, from files on disk ---


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


ARCHITECTURE = """\
xarch: 1
name: layered
layout: {src: {each: {api: {}, store: {}}}}
parts:
  api:   {path: "src/*/api", role: handlers, litmus: "Does it parse?", entry: true, driver_proves: routing,
          driver_test: {file: examples/driver.py}}
  store: {path: "src/*/store", role: database access, litmus: "Does it query?"}
rules: {api: [store@own]}
docs: {template: layered.md}
"""


def test_a_custom_architecture_brings_its_own_template(tmp_path):
    write(tmp_path / "layered.md", "# Layered\n\nsrc/\n{{tree}}\n\n{{rules_table}}\n\n{{litmus:api}}\n")
    write(tmp_path / "examples" / "driver.py", "def test_api(): ...\n")
    docs = build_architectures().docs(write(tmp_path / "layered.yaml", ARCHITECTURE))
    texts = {"/".join(f.path): f.template for f in docs.files}
    assert texts["architecture.md"] == (
        "# Layered\n\nsrc/\n"
        "└── src/\n    └── <module>/\n        ├── api/     handlers\n        └── store/   database access\n\n"
        "| Part | May import |\n|---|---|\n| `api/` | its own module's `store/` |\n| `store/` | nothing |\n\n"
        "> [!TIP]\n> **Litmus test.** Does it parse?\n")
    assert "| driver | `src/*/api/`, `bootstrap/jobs/` | routing;" in texts["testing.md"]
    assert "# driver: tests/src/*/api/test_publish.py\ndef test_api(): ...\n" in texts["testing.md"]


def test_a_template_with_a_bad_placeholder_fails_naming_the_template(tmp_path):
    write(tmp_path / "layered.md", "{{litmus:repo}} {{tables}}\n")
    write(tmp_path / "examples" / "driver.py", "def test_api(): ...\n")
    with pytest.raises(InvalidTemplate) as caught:
        build_architectures().docs(write(tmp_path / "layered.yaml", ARCHITECTURE))
    assert caught.value.problems[0] == "layered.md: {{litmus:repo}}: the architecture defines no part 'repo'"
    assert caught.value.problems[1].startswith("layered.md: unknown placeholder {{tables}}: use {{tree}}")


def test_an_architecture_without_a_template_has_no_docs(tmp_path):
    write(tmp_path / "examples" / "driver.py", "def test_api(): ...\n")
    path = write(tmp_path / "layered.yaml", ARCHITECTURE.replace("docs: {template: layered.md}\n", ""))
    with pytest.raises(InvalidTemplate) as caught:
        build_architectures().docs(path)
    assert caught.value.problems == (f"{path}: the architecture has no `docs: {{template: <file>}}` to fill",)
