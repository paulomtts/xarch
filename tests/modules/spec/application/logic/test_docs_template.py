"""Filling a docs template from a profile file: the prose is the author's, the file supplies the structure."""

from copy import deepcopy

import pytest

from tests.modules.spec.format_files import FILE_TYPES
from tests.modules.spec.languages import BRACE, PYTHON
from tests.modules.spec.profiles import parsed, part_of
from xarch.modules.spec.application.logic.docs_template import fill
from xarch.modules.spec.domain.errors import InvalidTemplate
from xarch.modules.spec.domain.values import FileType

PARTS = {
    "src/<module>/": {
        "store/": {"role": "database access", "litmus": "Does it touch the database?",
                   "imports": {"may": ["parts.shared/text"]}, "sql/": "the queries"},
        "service/": {"role": "business logic", "litmus": "Does it decide?",
                     "imports": {"may": ["module.store", "parts.api", "parts.shared"]}},
        "api.py": {"role": "HTTP handlers", "litmus": "Does it parse a request?", "imports": {"may": "everything"}},
    },
    "shared/": {"role": "code every module uses", "litmus": "Is it shared?", "imports": {"may": []}},
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
    return {"name": "layered", "parts": PARTS, "layers": {"inside": ["store", "service"]},
            "docs": DOCS} | extra


def brace(document: dict) -> dict:
    """The document with its file part ending in .ts, the ending of the language brace."""
    parts = deepcopy(document["parts"])
    parts["src/<module>/"] = {key.replace("api.py", "api.ts"): value for key, value in parts["src/<module>/"].items()}
    return document | {"parts": parts, "language": "brace"}


def parts(**changes) -> dict:
    document = {"parts": deepcopy(PARTS)}
    for name, change in changes.items():
        part_of(document, name).update(change)
    return document["parts"]


def filled(template: str, **extra) -> str:
    return fill(template, parsed(layered(**extra), folders=EXAMPLES), "layered.md", TEXTS, file_types=FILE_TYPES)


def problems(template: str, document: dict | None = None) -> list[str]:
    with pytest.raises(InvalidTemplate) as caught:
        fill(template, parsed(document or layered(), folders=EXAMPLES), "layered.md", TEXTS, file_types=FILE_TYPES)
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
    table = filled("{{rules_table}}", parts=parts(store={"imports": {"may": ["parts.store"]}}))
    assert table.splitlines()[2] == "| `store/` | any module's `store/` |"


def test_consecutive_targets_in_one_scope_share_their_phrase():
    table = filled("{{rules_table}}", parts=parts(service={"imports": {"may": ["module.store", "module.api", "parts.shared",
                                                                                    "parts.store", "parts.api"]}}))
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


RUN, MAIN, NOTES = "scripts/run.sh", "src/billing/main.go", "src/billing/notes.txt"
KINDS = {"ex": (SCHEMA, RUN, MAIN, NOTES)}
KIND_TEXTS = {SCHEMA: "create table bills ();\n", RUN: "make\n", MAIN: "package main\n", NOTES: "a note\n"}


@pytest.mark.parametrize("file, types, block", [
    pytest.param(SCHEMA, FILE_TYPES, "```sql\n-- src/billing/store/schema.sql\ncreate table bills ();\n```",
                 id="a kind whose comment the data file gives is named by its ending"),
    pytest.param(RUN, FILE_TYPES, "```bash\n# scripts/run.sh\nmake\n```",
                 id="a kind whose fence and comment the data file gives"),
    pytest.param(RUN, {".sh": FileType("bash")}, "```bash\n# scripts/run.sh\nmake\n```",
                 id="a kind whose fence alone the data file gives takes the comment of the language of the app"),
    pytest.param(MAIN, FILE_TYPES, "```go\n// src/billing/main.go\npackage main\n```",
                 id="a kind whose comment alone the data file gives"),
    pytest.param(NOTES, FILE_TYPES, "```txt\n# src/billing/notes.txt\na note\n```",
                 id="a kind the data file does not list is named by its ending, with the comment of the app's language"),
    pytest.param(NOTES, {".txt": FileType("text", ";")}, "```text\n; src/billing/notes.txt\na note\n```",
                 id="what the data file says is what the block is written with"),
])
def test_a_quoted_file_of_another_language_is_fenced_and_commented_as_the_data_file_of_file_types_says(file, types, block):
    architecture = parsed(layered(docs=DOCS | {"example_notes": {}}), folders=KINDS)
    assert fill("{{example:" + file + "}}", architecture, "layered.md", KIND_TEXTS, file_types=types) == block


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
    document = {"parts": deepcopy(PARTS)}
    del part_of(document, "shared")["litmus"]
    document = layered(docs={}, parts=document["parts"])
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
    feature = {key.replace("<module>", "<feature>"): value for key, value in deepcopy(PARTS).items()}
    feature["src/<feature>/"]["service/"]["imports"]["may"] = ["feature.store", "parts.api", "parts.shared"]
    text = filled("{{tree}}\n\n{{rules_table}}", parts=feature)
    assert "└── <feature>/" in text
    assert "its own feature's `store/`, any feature's `api.py`" in text
    assert "<module>" not in text and "module's" not in text


TWO = {
    "src/<module>/": {"service/": {"role": "business logic", "litmus": "Does it decide?",
                                   "imports": {"may": ["parts.hooks", "parts.shared"]}}},
    "ext/<plugin>/": {
        "hooks/": {"role": "what a plugin runs", "litmus": "Does a plugin run it?",
                   "imports": {"may": ["parts.service", "plugin.manifest", "parts.shared"], "libraries": ["yaml"]}},
        "manifest.py": {"role": "what a plugin declares", "litmus": "Does it declare?"},
    },
    "shared/": {"role": "code both use", "litmus": "Is it shared?"},
}


def two(template: str, **extra) -> str:
    document = {"name": "two", "parts": TWO, "docs": {"entry": "shared"}} | extra
    return fill(template, parsed(document), "two.md", file_types=FILE_TYPES)


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
        "- `may-import`: every import between parts is one that the `imports.may` of the importing part allows "
        "(architecture.md, section 5).",
        "- `libraries`: a part imports only the outside packages listed for it (`hooks/`: yaml); the standard "
        "library is always allowed, and tests are not checked.",
        "- `test tree`: every folder below `tests/src/` and `tests/ext/` mirrors a folder of the app.",
        "- `cycles`: no `src/<name>/` or `ext/<name>/` imports from another that imports, directly or through "
        "others, from it; each group of them that import each other is reported once, with the dependencies to cut "
        "and their imports."]


def test_the_cycles_line_names_the_folders_the_layout_names_beside_the_instances_as_in_their_graph():
    beside = {"src/": {"<module>/": TWO["src/<module>/"],
                       "web/": {"role": "the web ring", "litmus": "Is it the web?"},
                       "engine.py": {"role": "the engine", "litmus": "Is it the engine?"}},
              **{key: value for key, value in TWO.items() if key != "src/<module>/"}}
    lines = two("{{guards}}", parts=beside).splitlines()
    assert [line for line in lines if line.startswith("- `cycles`")] == [
        "- `cycles`: no `src/<name>/` or `ext/<name>/` imports from another that imports, directly or through "
        "others, from it, nor through `src/web/`, which lies beside them and is held in the same graph though it is "
        "none of them; each group of them that import each other is reported once, with the dependencies to cut "
        "and their imports."]


@pytest.mark.parametrize("guard, said", [
    pytest.param({"min_fields": 3}, "", id="the same fields only"),
    pytest.param({"min_fields": 3, "min_renamed": 4, "min_subset": 3},
                 " Nor is one a copy of another that renames some of its fields (from 4 fields: more than half of its "
                 "names kept in place, and each renamed field's type), or that keeps at least half of its fields in its "
                 "order (from 3 fields).", id="with the renamed and the partial copies"),
    pytest.param({"min_fields": 3, "translated": ["api", "store"]},
                 " A pair is no twin when a file of `api.py` or `store/` builds one of the two "
                 "through an import, imports the other, and holds one function that names both: a translation, which "
                 "every check names in its enforcement section.", id="with the parts whose translations it accepts"),
])
def test_the_no_twins_line_says_the_cases_the_profile_switches_on(guard, said):
    lines = [line for line in filled("{{guards}}", guards={"no-twins": guard}).splitlines() if "`no-twins`" in line]
    assert lines == ["- `no-twins`: no two public classes in parts of different names declare the same fields in the "
                     "same order, when each declares at least 3; types and defaults aside, tests not read." + said]


def test_a_shared_part_is_said_in_the_guards():
    lines = [line for line in filled("{{guards}}", parts=parts(shared={"shared": 2})).splitlines() if "`shared`" in line]
    assert lines == ["- `shared`: every public name of `shared/` is used by at least 2 users (each instance of a repeating "
                     "folder, or each part outside them; tests not read), or it belongs to the one that uses it."]


CALLBACKS = ("- `no-callbacks`: no function of `store/` and `service/` calls a parameter annotated as a callable: it is "
             "handed values, never a way to fetch them.")
PRIVATE = ("- `private-imports`: no file of the app or its tests imports a name that starts with `_` from another file "
           "of them.")


def test_the_no_callbacks_line_is_a_guard_line_after_the_part_lines():
    lines = filled("{{guards}}", parts=parts(service={"holds": {"functions": {}, "records": {}, "exceptions": {}}}),
                   guards={"no-callbacks": {"parts": ["store", "service"]}, "private-imports": {}}).splitlines()
    assert lines[-2:] == [CALLBACKS, PRIVATE]
    assert [line for line in lines if "`no-callbacks`" in line] == [CALLBACKS]


def test_the_no_callbacks_line_follows_the_order_the_profile_writes_its_guards_in():
    lines = filled("{{guards}}", guards={"no-callbacks": {"parts": ["store", "service"]},
                                         "pass-through": {"parts": ["service"]}}).splitlines()
    assert [line.split(":")[0] for line in lines[-2:]] == ["- `no-callbacks`", "- `pass-through`"]


def test_a_profile_without_the_guard_has_no_no_callbacks_line():
    assert "`no-callbacks`" not in filled("{{guards}}", guards={"private-imports": {}})


def test_a_quoted_file_of_any_ending_of_the_language_of_the_app_is_fenced_with_the_language_s_name():
    view = "src/billing/api/view.tsx"
    architecture = parsed(brace(layered(docs=DOCS | {"example_notes": {}})), folders={"ex": (view,)},
                          languages={"python": PYTHON, "brace": BRACE})
    assert fill("{{example:" + view + "}}", architecture, "layered.md", {view: "x\n"}, file_types=FILE_TYPES) == (
        "```brace\n// src/billing/api/view.tsx\nx\n```")


def test_the_no_comments_line_says_the_first_comment_marker_of_the_language_and_each_directive_after_it():
    view = "src/billing/api/view.tsx"
    architecture = parsed(brace(layered(docs=DOCS | {"example_notes": {}}, guards={"no-comments": {}})),
                          folders={"ex": (view,)}, languages={"python": PYTHON, "brace": BRACE})
    filled_in = fill("{{guards}}", architecture, "layered.md", {view: "x\n"}, file_types=FILE_TYPES)
    assert [line for line in filled_in.splitlines() if "`no-comments`" in line] == [
        "- `no-comments`: no `//` comments in the app or its tests; docstrings and tool directives "
        "(`// @ts-expect-error`, `// eslint-disable`) stay."]


def test_the_private_imports_line_says_the_prefix_the_language_gives():
    lines = [line for line in filled("{{guards}}", guards={"private-imports": {}}).splitlines()
             if "`private-imports`" in line]
    assert lines == ["- `private-imports`: no file of the app or its tests imports a name that starts with `_` from "
                     "another file of them."]


def test_the_private_imports_line_of_a_language_that_gives_no_prefix_says_the_rule_by_what_a_file_keeps_private():
    view = "src/billing/api/view.tsx"
    architecture = parsed(brace(layered(docs=DOCS | {"example_notes": {}}, guards={"private-imports": {}})),
                          folders={"ex": (view,)}, languages={"python": PYTHON, "brace": BRACE})
    filled_in = fill("{{guards}}", architecture, "layered.md", {view: "x\n"}, file_types=FILE_TYPES)
    lines = [line for line in filled_in.splitlines() if "`private-imports`" in line]
    assert lines == ["- `private-imports`: no file of the app or its tests imports a name another file of them keeps "
                     "private."]
    assert "``" not in lines[0]


LOGIC = {"functions": {}, "records": {"immutable": True}, "exceptions": {}}
ENFORCED = "listed in the enforcement section, and fails `check --strict` only."


def keyed(key: str, **changes) -> list[str]:
    """The lines of the guards the parts changed as given say for the key."""
    return [line for line in filled("{{guards}}", parts=parts(**changes)).splitlines() if line.startswith(f"- `{key}`")]


def test_the_holds_line_says_the_two_bundled_forms_as_it_always_has():
    assert keyed("holds", store={"holds": {"classes": {}}}, service={"holds": LOGIC}, shared={"holds": {"classes": {}}}) == [
        "- `holds`: a file of `store/` and `shared/` defines classes, never a public function at the top level; a file "
        "of `service/` defines functions, never a class (a private one too) but exceptions and the records its "
        f"functions return; {ENFORCED}"]


def test_the_holds_line_says_any_other_group_by_the_kinds_it_allows_after_the_bundled_forms():
    assert keyed("holds", store={"holds": {"functions": {}, "records": {}}}, service={"holds": {"classes": {}}},
                 shared={"holds": {"classes": {}, "functions": {}}}) == [
        "- `holds`: a file of `service/` defines classes, never a public function at the top level; a file of `store/` "
        "holds functions and records and no other kind at the top level; a file of `shared/` holds classes and "
        f"functions and no other kind at the top level; {ENFORCED}"]


def test_the_immutable_lines_say_the_parts_of_immutable_classes_then_those_of_immutable_records():
    assert keyed("immutable", store={"holds": {"classes": {"immutable": True}}}, service={"holds": LOGIC}) == [
        "- `immutable`: every class of `store/` is an immutable record, as the Python data file marks one, or an "
        f"exception; {ENFORCED}",
        f"- `immutable`: every record of `service/` is an immutable record, as the Python data file marks one; {ENFORCED}"]


def test_the_names_lines_say_each_kind_named_in_the_order_of_the_kinds():
    holds = {"classes": {"names": "*Service"}, "functions": {"names": ["is_*", "has_*"]},
             "exceptions": {"names": "*Error"}}
    assert keyed("names", service={"holds": holds}, store={"holds": {"records": {"names": "*Row"}}}) == [
        "- `names`: every record of `store/` is named `*Row`.",
        "- `names`: every class of `service/` but its exceptions is named `*Service`.",
        "- `names`: every function of `service/` at the top level is named `is_*` or `has_*`.",
        "- `names`: every exception of `service/` is named `*Error`."]


def test_the_names_line_of_classes_beside_records_and_exceptions_leaves_both_out():
    holds = {"classes": {"names": "*Service"}, "records": {"immutable": True}, "exceptions": {"names": "*Error"}}
    assert keyed("names", service={"holds": holds})[0] == (
        "- `names`: every class of `service/` but its records and exceptions is named `*Service`.")


def test_the_built_by_line_reads_the_built_by_of_classes():
    assert keyed("built-by", service={"holds": {"classes": {"built_by": ["api"]}}}) == [
        "- `built-by`: only code of `api.py` builds a class of `service/`; tests are not read."]


def test_a_profile_with_no_part_has_no_placement_order_and_is_told_to_write_its_parts_under_parts():
    assert problems("{{placement}}", {"name": "layered", "parts": {}}) == [
        "layered.md: {{placement}}: the architecture has no placement order: write its parts under `parts`, whose "
        "reading order is the order the litmus tests run"]


def test_a_litmus_list_is_a_tip_of_its_alternatives_then_its_conditions_each_by_its_label():
    document = layered()
    part_of(document, "store")["litmus"] = ["Does it save?", {"ask": "Does it\nload?", "label": "load"},
                                            {"ask": "Is it the store's session?", "label": "session", "mode": "all"}]
    assert fill("{{litmus:store}}", parsed(document, folders=EXAMPLES), "layered.md", TEXTS, file_types=FILE_TYPES) == (
        "> [!TIP]\n> **Litmus tests.** Code belongs here when at least one of these answers yes:\n"
        "> - **1.** Does it save?\n> - **load.** Does it load?\n>\n> and when each of these answers yes:\n"
        "> - **session.** Is it the store's session?")


def test_a_litmus_list_of_conditions_only_says_each_must_answer_yes():
    document = layered()
    part_of(document, "store")["litmus"] = [{"ask": "Is it pure?", "mode": "all"}]
    assert fill("{{litmus:store}}", parsed(document, folders=EXAMPLES), "layered.md", TEXTS, file_types=FILE_TYPES) == (
        "> [!TIP]\n> **Litmus tests.** Code belongs here when each of these answers yes:\n> - **1.** Is it pure?")
