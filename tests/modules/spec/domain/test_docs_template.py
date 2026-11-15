"""Filling a docs template from an architecture file: the bundled ones reproduce the checked-in docs byte for byte."""
from importlib import resources
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_architectures, load_architecture
from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidTemplate

DOCS = Path(__file__).resolve().parents[4] / "docs"


def layered(**extra) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"api.py": "file", "service": {}, "store": {"sql": {}}}}, "shared": {}},
        "notes": {"src/*/store/sql": "the queries"},
        "parts": {"shared": {"path": "shared", "role": "code every module uses", "litmus": "Is it shared?"},
                  "store": {"path": "src/*/store", "role": "database access", "litmus": "Does it touch the database?"},
                  "service": {"path": "src/*/service", "role": "business logic", "litmus": "Does it decide?"},
                  "api": {"path": "src/*/api.py", "role": "HTTP handlers", "litmus": "Does it parse a request?",
                          "entry": True}},
        "rules": {"shared": ["shared"], "store": ["store@own", "shared/text"],
                  "service": ["service@own", "store@own", "api@any", "shared"], "api": ["*"]},
        "layers": {"inside": ["store", "service"]},
        "placement": ["store", "service", "api", "shared"],
        "naming": [{"kind": "service", "where": ["service/"], "pattern": "thing and `Service`",
                    "example": ["BillingService", "TaxService"]}],
    } | extra


def filled(template: str, **extra) -> str:
    return fill(template, parse_architecture(layered(**extra), "layered.yaml", lambda r: True), "layered.md")


def problems(template: str, **extra) -> list[str]:
    with pytest.raises(InvalidTemplate) as caught:
        filled(template, **extra)
    assert caught.value.reason == "\n".join(caught.value.problems)
    return list(caught.value.problems)


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


def test_the_bundled_testing_template_is_shared_and_holds_no_hand_typed_tiers():
    """The commands that run the tiers are left as `<command>`: they are the project's own."""
    for profile in ("cli", "web"):
        docs = {"/".join(doc.path): doc.source for doc in load_architecture(profile).docs}
        assert docs["testing.md"] == "testing.md"
    template = resources.files("xarch").joinpath("architectures", "testing.md").read_text(encoding="utf-8")
    for placeholder in ["{{tiers}}", "{{untested}}", "{{tier_litmus:3}}", "{{tier_index:3}}", "{{tier_examples}}",
                        "{{tier_helpers}}", "{{tier_files}}", "{{tier_data}}"]:
        assert template.count(placeholder) == 1, placeholder
    assert "| unit |" not in template and "> **unit.**" not in template and "# unit:" not in template
    assert "- unit, integration, rendering, guard: `<command>`" in template


def test_the_tree_shows_each_folder_once_with_its_role_or_note_aligned():
    """Each note starts three spaces after the tree's longest line."""
    assert filled("app/\n{{tree}}\n") == (
        "app/\n"
        "├── src/\n"
        "│   └── <module>/\n"
        "│       ├── api.py     HTTP handlers\n"
        "│       ├── service/   business logic\n"
        "│       └── store/     database access\n"
        "│           └── sql/   the queries\n"
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


def test_the_entry_point():
    assert filled("tests/{{entry}}/") == "tests/src/*/api.py/"


EXAMPLES = {"charge": {"part": "service", "path": "src/billing/service/charge.py", "file": "x/charge.py"},
            "store": {"part": "store", "path": "src/billing/store/__init__.py", "file": "x/store.py",
                      "note": "the store's public names"},
            "schema": {"part": "store", "path": "src/billing/store/schema.sql", "file": "x/schema.sql"}}
TEXTS = {"charge": "from app.src.billing.store import save\n\ndef charge(): ...\n\n\n", "store": "save = ...\n",
         "schema": "create table bills ();\n"}


def filled_examples(template: str) -> str:
    return fill(template, parse_architecture(layered(examples=EXAMPLES), "layered.yaml", lambda r: True),
                "layered.md", TEXTS)


def test_an_example_alone_is_a_fenced_block_of_its_file_under_its_path():
    assert filled_examples("x\n\n{{example:charge}}\n\ny") == (
        "x\n\n```python\n# src/billing/service/charge.py\nfrom app.src.billing.store import save\n\ndef charge(): ..."
        "\n```\n\ny")
    assert filled_examples("{{example:schema}}") == "```sql\n-- src/billing/store/schema.sql\ncreate table bills ();\n```"


def test_several_examples_share_one_block_a_blank_line_apart_each_under_its_path_and_note():
    assert filled_examples("{{example: store , charge}}") == (
        "```python\n# src/billing/store/__init__.py: the store's public names\nsave = ...\n\n"
        "# src/billing/service/charge.py\nfrom app.src.billing.store import save\n\ndef charge(): ...\n```")


def test_an_example_inside_the_templates_own_block_leaves_the_block_to_the_template():
    assert filled_examples("```python\n{{example:store}}\n\n# an excerpt\n    save()\n```\n{{example:store}}") == (
        "```python\n# src/billing/store/__init__.py: the store's public names\nsave = ...\n\n# an excerpt\n    save()\n"
        "```\n```python\n# src/billing/store/__init__.py: the store's public names\nsave = ...\n```")


def test_an_unknown_example_or_a_block_of_mixed_files_is_rejected():
    with pytest.raises(InvalidTemplate) as caught:
        filled_examples("{{example:charge, refund, credit}}\n{{example:charge, schema}}")
    assert caught.value.problems == (
        "layered.md: {{example:charge, refund, credit}}: the architecture has no example 'refund', 'credit' "
        "(its examples: charge, store, schema)",
        "layered.md: {{example:charge, schema}}: one block cannot mix files of different kinds (.py, .sql)",
    )


def test_unused_placeholders_and_single_braces_are_fine():
    assert filled("def f(): return {}  # {x} {{ not one }") == "def f(): return {}  # {x} {{ not one }"
    assert filled("{{ placement }}") == filled("{{placement}}")


def test_an_unknown_placeholder_is_rejected():
    assert problems("{{tree}} {{trees}} {{litmus}} {{tree:x}}") == [
        f"layered.md: unknown placeholder {p}: use {{{{tree}}}}, {{{{rules_table}}}}, {{{{layers:<name>}}}}, "
        "{{placement}}, {{litmus:<part>}}, {{naming}}, {{entry}}, {{docs_tree}}, {{example:<name>, ...}}, {{tiers}}, {{untested}}, "
        "{{tier_litmus:<section>}}, {{tier_files}}, {{tier_helpers}}, {{tier_index:<section>}}, {{tier_data}}, {{tier_examples}}, "
        "{{guards}}"
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
    del document["parts"]["api"]["entry"]
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


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


ARCHITECTURE = """\
xarch: 1
name: layered
layout: {src: {singular: module, each: {api: {}, store: {}}}}
parts:
  api:   {path: "src/*/api", role: handlers, litmus: "Does it parse?", entry: true}
  store: {path: "src/*/store", role: database access, litmus: "Does it query?"}
rules: {api: [store@own]}
docs:
  architecture.md: {from: layered.md, note: this file}
"""


def test_a_custom_architecture_brings_its_own_template(tmp_path):
    """It names no testing template, so it gets no testing.md."""
    write(tmp_path / "notes.md", "# Notes\n")
    write(tmp_path / "layered.md", "# Layered\n\nsrc/\n{{tree}}\n\n{{rules_table}}\n\n{{litmus:api}}\n")
    docs = build_architectures().docs(write(tmp_path / "layered.yaml", ARCHITECTURE + "  notes.md: {from: notes.md}\n"))
    texts = {"/".join(f.path): f.template for f in docs.files}
    assert texts["architecture.md"] == (
        "# Layered\n\nsrc/\n"
        "└── src/\n    └── <module>/\n        ├── api/     handlers\n        └── store/   database access\n\n"
        "| Part | May import |\n|---|---|\n| `api/` | its own module's `store/` |\n| `store/` | nothing |\n\n"
        "> [!TIP]\n> **Litmus test.** Does it parse?\n")
    assert list(texts) == ["architecture.md", "notes.md"] and texts["notes.md"] == "# Notes\n"


def test_a_template_with_a_bad_placeholder_fails_naming_the_template(tmp_path):
    write(tmp_path / "layered.md", "{{litmus:repo}} {{tables}}\n")
    with pytest.raises(InvalidTemplate) as caught:
        build_architectures().docs(write(tmp_path / "layered.yaml", ARCHITECTURE))
    assert caught.value.problems[0] == "layered.md: {{litmus:repo}}: the architecture defines no part 'repo'"
    assert caught.value.problems[1].startswith("layered.md: unknown placeholder {{tables}}: use {{tree}}")


def test_an_architecture_that_declares_no_docs_gets_none(tmp_path):
    path = write(tmp_path / "layered.yaml", ARCHITECTURE.split("docs:")[0])
    assert build_architectures().docs(path).files == ()


def test_the_docs_tree_lists_the_declared_docs_with_their_notes(tmp_path):
    document = {"docs": {
        "a.md": {"from": "x.md", "note": "first"},
        "long-name.md": {"from": "x.md"},
        "adrs/": {"note": "decisions"},
        "adrs/0000.md": {"from": "x.md"},
        "kinds/one/_t.md": {"from": "x.md", "note": "one of each"},
        "kinds/two/_t.md": {"from": "x.md"},
    }}
    assert filled("{{docs_tree}}", **document) == (
        "    ├── a.md                first\n"
        "    ├── long-name.md\n"
        "    ├── adrs/               decisions\n"
        "    │   └── 0000.md\n"
        "    └── kinds/\n"
        "        ├── one/            _t.md; one of each\n"
        "        └── two/            _t.md")


def test_the_docs_tree_of_an_architecture_without_docs_is_refused():
    assert problems("{{docs_tree}}") == ["layered.md: {{docs_tree}}: the architecture declares no `docs`"]


def test_the_instance_is_named_by_the_architectures_singular_not_by_xarch():
    layout = {"src": {"singular": "feature", "each": {"api.py": "file", "service": {}, "store": {"sql": {}}}},
              "shared": {}}
    text = filled("{{tree}}\n\n{{rules_table}}", layout=layout)
    assert "└── <feature>/" in text
    assert "its own feature's `store/`, any feature's `api.py`" in text
    assert "<module>" not in text and "module's" not in text
