"""Filling a docs template from a profile file: the prose is the author's, the file supplies the structure."""
import pytest

from tests.modules.spec.profiles_v2 import parsed
from xarch.modules.spec.domain.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidTemplate

PARTS = {
    "store": {"path": "src/<module>/store", "role": "database access", "litmus": "Does it touch the database?",
              "may_import": ["shared/text"], "folders": {"sql": "the queries"}},
    "service": {"path": "src/<module>/service", "role": "business logic", "litmus": "Does it decide?",
                "may_import": ["store", "api@any", "shared"]},
    "api": {"path": "src/<module>/api.py", "role": "HTTP handlers", "litmus": "Does it parse a request?",
            "may_import": "everything"},
    "shared": {"path": "shared", "role": "code every module uses", "litmus": "Is it shared?", "may_import": []},
}
NAMING = [{"kind": "service", "where": ["service/"], "pattern": "thing and `Service`",
           "example": ["BillingService", "TaxService"]}]
CHARGE = "src/billing/service/charge.py"
STORE = "src/billing/store/__init__.py"
SCHEMA = "src/billing/store/schema.sql"
EXAMPLES = {"ex": (CHARGE, STORE, SCHEMA)}
TEXTS = {CHARGE: "from app.src.billing.store import save\n\ndef charge(): ...\n\n\n", STORE: "save = ...\n",
         SCHEMA: "create table bills ();\n"}
DOCS = {"entry": "api", "naming": NAMING, "examples": ["ex"], "example_notes": {STORE: "the store's public names"}}


def layered(**extra) -> dict:
    return {"xarch": 2, "name": "layered", "parts": PARTS, "layers": {"inside": ["store", "service"]},
            "docs": DOCS} | extra


def parts(**changes) -> dict:
    return {name: part | changes.get(name, {}) for name, part in PARTS.items()}


def filled(template: str, **extra) -> str:
    return fill(template, parsed(layered(**extra), folder_files=EXAMPLES.get), "layered.md", TEXTS)


def problems(template: str, document: dict | None = None) -> list[str]:
    with pytest.raises(InvalidTemplate) as caught:
        fill(template, parsed(document or layered(), folder_files=EXAMPLES.get), "layered.md", TEXTS)
    assert caught.value.reason == "\n".join(caught.value.problems)
    return list(caught.value.problems)


def test_the_tree_shows_each_folder_once_with_its_role_or_note_aligned():
    """Each note starts three spaces after the tree's longest line."""
    assert filled("app/\n{{tree}}\n") == (
        "app/\n"
        "├── src/\n"
        "│   └── <module>/\n"
        "│       ├── store/     database access\n"
        "│       │   └── sql/   the queries\n"
        "│       ├── service/   business logic\n"
        "│       └── api.py     HTTP handlers\n"
        "└── shared/            code every module uses\n")


def test_the_rules_table_lists_each_part_in_order_without_itself():
    assert filled("{{rules_table}}") == (
        "| Part | May import |\n"
        "|---|---|\n"
        "| `store/` | `shared/text` |\n"
        "| `service/` | its own module's `store/`, any module's `api.py`, `shared/` |\n"
        "| `api.py` | everything |\n"
        "| `shared/` | nothing |")


def test_a_part_naming_its_own_kind_in_any_module_shows_it():
    table = filled("{{rules_table}}", parts=parts(store={"may_import": ["store@any"]}))
    assert table.splitlines()[2] == "| `store/` | any module's `store/` |"


def test_consecutive_targets_in_one_scope_share_their_phrase():
    table = filled("{{rules_table}}", parts=parts(service={"may_import": ["store", "api", "shared", "store@any",
                                                                          "api@any"]}))
    assert table.splitlines()[3] == (
        "| `service/` | its own module's `store/` and `api.py`, `shared/`, any module's `store/` and `api.py` |")


def test_layers_placement_litmus_and_naming():
    assert filled("{{layers:inside}}") == "`store/` → `service/`"
    assert filled("{{placement}}") == "`store` → `service` → `api` → `shared`"
    assert filled("x\n{{litmus:store}}\ny") == "x\n> [!TIP]\n> **Litmus test.** Does it touch the database?\ny"
    assert filled("{{naming}}") == ("| Kind | Where | Pattern | Example |\n|---|---|---|---|\n"
                                    "| service | `service/` | thing and `Service` | `BillingService`, `TaxService` |")


def test_the_entry_point():
    assert filled("tests/{{entry}}/") == "tests/src/*/api.py/"


def test_an_example_alone_is_a_fenced_block_of_its_file_under_its_path():
    assert filled("x\n\n{{example:" + CHARGE + "}}\n\ny") == (
        "x\n\n```python\n# src/billing/service/charge.py\nfrom app.src.billing.store import save\n\ndef charge(): ..."
        "\n```\n\ny")
    assert filled("{{example:" + SCHEMA + "}}") == "```sql\n-- src/billing/store/schema.sql\ncreate table bills ();\n```"


def test_an_example_with_a_note_shows_it_after_its_path_behind_a_colon():
    assert filled("{{example:" + STORE + "}}") == (
        "```python\n# src/billing/store/__init__.py: the store's public names\nsave = ...\n```")


def test_several_examples_share_one_block_a_blank_line_apart_each_under_its_path_and_note():
    assert filled(f"{{{{example: {STORE} , {CHARGE}}}}}") == (
        "```python\n# src/billing/store/__init__.py: the store's public names\nsave = ...\n\n"
        "# src/billing/service/charge.py\nfrom app.src.billing.store import save\n\ndef charge(): ...\n```")


def test_an_example_inside_the_templates_own_block_leaves_the_block_to_the_template():
    template = f"```python\n{{{{example:{STORE}}}}}\n\n# an excerpt\n    save()\n```\n{{{{example:{STORE}}}}}"
    assert filled(template) == (
        "```python\n# src/billing/store/__init__.py: the store's public names\nsave = ...\n\n# an excerpt\n    save()\n"
        "```\n```python\n# src/billing/store/__init__.py: the store's public names\nsave = ...\n```")


def test_an_unknown_example_or_a_block_of_mixed_files_is_rejected():
    assert problems(f"{{{{example:{CHARGE}, refund, credit}}}}\n{{{{example:{CHARGE}, {SCHEMA}}}}}") == [
        f"layered.md: {{{{example:{CHARGE}, refund, credit}}}}: the architecture has no example 'refund', 'credit' "
        f"(its examples: {CHARGE}, {STORE}, {SCHEMA})",
        f"layered.md: {{{{example:{CHARGE}, {SCHEMA}}}}}: one block cannot mix files of different kinds (.py, .sql)"]


def test_unused_placeholders_and_single_braces_are_fine():
    assert filled("def f(): return {}  # {x} {{ not one }") == "def f(): return {}  # {x} {{ not one }"
    assert filled("{{ placement }}") == filled("{{placement}}")


def test_an_unknown_placeholder_is_rejected():
    found = problems("{{tree}} {{trees}} {{litmus}} {{tree:x}}")
    assert [message.split(": use ")[0] for message in found] == [
        f"layered.md: unknown placeholder {p}" for p in ["{{trees}}", "{{litmus}}", "{{tree:x}}"]]
    assert all(message.split(": use ")[1].startswith("{{tree}}, {{rules_table}}, {{layers:<name>}}")
               for message in found)


def test_a_part_or_layer_the_file_does_not_define_is_rejected():
    assert problems("{{litmus:repo}}\n{{litmus:store}}\n{{layers:outside}}") == [
        "layered.md: {{litmus:repo}}: the architecture defines no part 'repo'",
        "layered.md: {{layers:outside}}: the architecture has no layer 'outside' (its layers: inside)"]


def test_what_the_file_leaves_out_is_reported_when_a_placeholder_needs_it():
    shared = {key: value for key, value in PARTS["shared"].items() if key != "litmus"}
    document = layered(docs={}, parts={**PARTS, "shared": shared})
    assert problems("{{naming}}{{entry}}{{litmus:shared}}", document) == [
        "layered.md: {{naming}}: the architecture has no `docs.naming`",
        "layered.md: {{entry}}: no part is the entry point: set `docs.entry` to a part",
        "layered.md: {{litmus:shared}}: part 'shared' has no litmus test"]


def test_the_docs_tree_lists_the_declared_docs_with_their_notes():
    pages = {
        "a.md": {"from": "x.md", "note": "first"},
        "long-name.md": {"from": "x.md"},
        "adrs/": {"note": "decisions"},
        "adrs/0000.md": {"from": "x.md"},
        "kinds/one/_t.md": {"from": "x.md", "note": "one of each"},
        "kinds/two/_t.md": {"from": "x.md"},
    }
    assert filled("{{docs_tree}}", docs={"pages": pages}) == (
        "    ├── a.md                first\n"
        "    ├── long-name.md\n"
        "    ├── adrs/               decisions\n"
        "    │   └── 0000.md\n"
        "    └── kinds/\n"
        "        ├── one/            _t.md; one of each\n"
        "        └── two/            _t.md")


def test_the_docs_tree_of_an_architecture_without_docs_is_refused():
    document = layered()
    del document["docs"]
    assert problems("{{docs_tree}}", document) == ["layered.md: {{docs_tree}}: the architecture declares no `docs`"]


def test_the_instance_is_named_by_the_word_in_the_paths_not_by_xarch():
    feature = {name: part | {"path": part["path"].replace("<module>", "<feature>")} for name, part in PARTS.items()}
    text = filled("{{tree}}\n\n{{rules_table}}", parts=feature)
    assert "└── <feature>/" in text
    assert "its own feature's `store/`, any feature's `api.py`" in text
    assert "<module>" not in text and "module's" not in text


TWO = {
    "service": {"path": "src/<module>/service", "role": "business logic", "litmus": "Does it decide?",
                "may_import": ["hooks@any", "shared"]},
    "hooks": {"path": "ext/<plugin>/hooks", "role": "what a plugin runs", "litmus": "Does a plugin run it?",
              "may_import": ["service@any", "manifest", "shared"], "libraries": ["yaml"]},
    "manifest": {"path": "ext/<plugin>/manifest.py", "role": "what a plugin declares", "litmus": "Does it declare?"},
    "shared": {"path": "shared", "role": "code both use", "litmus": "Is it shared?"},
}


def two(template: str, **extra) -> str:
    document = {"xarch": 2, "name": "two", "parts": TWO, "docs": {"entry": "shared"}} | extra
    return fill(template, parsed(document), "two.md")


def test_the_tree_shows_every_repeating_folder_by_its_own_word():
    assert two("app/\n{{tree}}\n") == (
        "app/\n"
        "├── src/\n"
        "│   └── <module>/\n"
        "│       └── service/      business logic\n"
        "├── ext/\n"
        "│   └── <plugin>/\n"
        "│       ├── hooks/        what a plugin runs\n"
        "│       └── manifest.py   what a plugin declares\n"
        "└── shared/               code both use\n")


def test_the_rules_table_names_each_part_by_the_word_of_the_folder_it_lies_in():
    assert two("{{rules_table}}") == (
        "| Part | May import |\n"
        "|---|---|\n"
        "| `service/` | any plugin's `hooks/`, `shared/` |\n"
        "| `hooks/` | any module's `service/`, its own plugin's `manifest.py`, `shared/` |\n"
        "| `manifest.py` | nothing |\n"
        "| `shared/` | nothing |")


def test_the_guards_name_every_repeating_folder():
    assert two("{{guards}}").splitlines() == [
        "- `structure`: every folder and file of the layout exists, in the app and in every `src/<name>/` and "
        "`ext/<name>/`.",
        "- `rules`: every import between parts is one that the `may_import` of the importing part allows "
        "(architecture.md, section 5).",
        "- `libraries`: a part imports only the outside packages listed for it (`hooks/`: yaml); the standard "
        "library is always allowed, and tests are not checked.",
        "- `test tree`: every folder below `tests/src/` and `tests/ext/` mirrors a folder of the app.",
        "- `cycles`: no `src/<name>/` or `ext/<name>/` imports from another that imports, directly or through "
        "others, from it; each cycle is reported once, with the imports that close it."]
