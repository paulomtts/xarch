"""Loading and validating an architecture file: every problem reported, prefixed by the file, never a traceback."""
import json
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_architectures, load_architecture
from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Example, Naming, Part, Target
from xarch.platform.data_files import DataFileReader

LAYERED = """\
xarch: 1
name: layered
layout:
  src:
    each:
      api: {}
      service: {}
      store: {}
parts:
  api:     { path: "src/*/api",     role: "HTTP handlers",   litmus: "Does it parse a request and call a service?" }
  service: { path: "src/*/service", role: "business logic",  litmus: "Does it decide what is allowed?" }
  store:   { path: "src/*/store",   role: "database access", litmus: "Does it touch the database?" }
rules:
  api:     [api@own, service@own]
  service: [service@own, store@own]
  store:   [store@own]
"""


def layered() -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"each": {"api": {}, "service": {}, "store": {}}}},
        "parts": {"api": {"path": "src/*/api", "role": "HTTP handlers"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "store": {"path": "src/*/store", "role": "database access"}},
        "rules": {"api": ["api@own", "service@own"], "service": ["service@own", "store@own"], "store": ["store@own"]},
    }


def problems(document, has_file=lambda relative: True) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        parse_architecture(document, "layered.yaml", has_file)
    assert caught.value.reason == "\n".join(caught.value.problems)
    return list(caught.value.problems)


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


# --- the model ---


def test_a_valid_file_loads(tmp_path):
    architecture = load_architecture(write(tmp_path / "layered.yaml", LAYERED))
    assert architecture.name == "layered"
    assert architecture.module_root() == ("src",)
    assert architecture.module_tree() == {"api": {}, "service": {}, "store": {}}
    assert architecture.top_level_tree() == {"src": {}}
    assert architecture.parts["api"] == Part("api", ("src", "*", "api"), "HTTP handlers",
                                             "Does it parse a request and call a service?")
    assert architecture.rules["service"] == (Target("service", "own"), Target("store", "own"))
    assert architecture.docs_template is None and architecture.examples == {}


def test_targets_carry_scope_and_sub_path():
    document = layered()
    document["layout"]["shared"] = {}
    document["parts"]["shared"] = {"path": "shared", "role": "shared code"}
    document["rules"]["api"] = ["service@any/values/ids", "shared/text", "*"]
    rules = parse_architecture(document, "layered.yaml", lambda r: True).rules
    assert rules["api"] == (Target("service", "any", ("values", "ids")), Target("shared", "none", ("text",)),
                            Target("*"))
    assert rules["shared"] == ()                            # a part with no row may import nothing


def test_a_file_in_the_layout_and_a_part_on_it():
    document = layered()
    document["layout"]["src"]["each"]["main.py"] = "file"
    document["parts"]["main"] = {"path": "src/*/main.py", "role": "the entry"}
    architecture = parse_architecture(document, "layered.yaml", lambda r: True)
    assert architecture.module_tree()["main.py"] is None
    assert architecture.parts["main"].path == ("src", "*", "main.py")


def test_an_equivalent_json_file_loads_the_same(tmp_path):
    yaml_file = write(tmp_path / "layered.yaml", LAYERED)
    json_file = write(tmp_path / "layered.json", json.dumps(DataFileReader().parse(LAYERED), indent="\t"))
    assert "\t" in json_file.read_text()                    # tab-indented: valid JSON, but not valid YAML
    assert load_architecture(json_file) == load_architecture(yaml_file)
    assert load_architecture(str(json_file)) == load_architecture(yaml_file)


def test_docs_template_and_examples_resolve_next_to_the_file(tmp_path):
    write(tmp_path / "layered.md", "# {name}\n")
    write(tmp_path / "examples" / "charge.py", "def charge(): ...\n")
    text = LAYERED + ("docs:\n  template: layered.md\n"
                      "examples:\n  service: { path: src/billing/service/charge.py, file: examples/charge.py }\n")
    architecture = load_architecture(write(tmp_path / "layered.yaml", text))
    assert architecture.docs_template == "layered.md"
    assert architecture.examples == {"service": Example(("src", "billing", "service", "charge.py"),
                                                        "examples/charge.py")}


def test_the_entry_point_its_driver_notes_layers_placement_and_naming_load(tmp_path):
    write(tmp_path / "examples" / "driver.py", "def test_api(): ...\n")
    text = LAYERED.replace('  api:     { path: "src/*/api",', '  api:     { entry: true, driver_proves: "routing",'
                           ' driver_test: { file: examples/driver.py }, path: "src/*/api",') + (
        "notes:\n  src: every module\n"
        "layers:\n  inside: [store, service, api]\n"
        "placement: [store, service, api]\n"
        "naming:\n  - {kind: service, where: service/, pattern: thing and `Service`, example: [BillingService]}\n")
    architecture = load_architecture(write(tmp_path / "layered.yaml", text))
    assert architecture.entry == Part("api", ("src", "*", "api"), "HTTP handlers",
                                      "Does it parse a request and call a service?", True, "routing",
                                      "examples/driver.py")
    assert [part.name for part in architecture.parts.values() if part.entry] == ["api"]
    assert architecture.notes == {("src",): "every module"}
    assert architecture.layers == {"inside": ("store", "service", "api")}
    assert architecture.placement == ("store", "service", "api")
    assert architecture.naming == (Naming("service", ("service/",), "thing and `Service`", ("BillingService",)),)


def test_the_new_keys_are_optional():
    architecture = parse_architecture(layered(), "layered.yaml", lambda r: True)
    assert architecture.entry is None and architecture.notes == {} and architecture.layers == {}
    assert architecture.placement == () and architecture.naming == ()


# --- the errors, one kind at a time ---


def test_two_entry_points_are_rejected():
    document = layered()
    document["parts"]["api"]["entry"] = True
    document["parts"]["store"]["entry"] = True
    document["parts"]["service"]["entry"] = "yes"
    assert problems(document) == ["layered.yaml: parts.service.entry: must be true or false",
                                  "layered.yaml: parts: only one part may be the entry point, not 'api', 'store'"]


def test_a_driver_on_a_part_that_is_not_the_entry_point_is_rejected():
    document = layered()
    document["parts"]["store"] |= {"driver_proves": "queries", "driver_test": {"file": "x.py"}}
    assert problems(document) == [
        "layered.yaml: parts.store.driver_proves: only the entry point (`entry: true`) has a driver",
        "layered.yaml: parts.store.driver_test: only the entry point (`entry: true`) has a driver",
    ]


def test_a_bad_driver_test_is_rejected():
    document = layered()
    document["parts"]["api"] |= {"entry": True, "driver_proves": 3, "driver_test": {"file": "nowhere.py", "x": 1}}
    assert problems(document, has_file=lambda relative: False) == [
        "layered.yaml: parts.api.driver_proves: must be a string",
        "layered.yaml: parts.api.driver_test: unknown key 'x': use file",
        "layered.yaml: parts.api.driver_test.file: no file 'nowhere.py' next to the architecture file",
    ]
    document["parts"]["api"]["driver_test"] = "examples/driver.py"
    assert problems(document)[-1] == ("layered.yaml: parts.api.driver_test: must be a mapping such as "
                                      "{file: examples/driver.py}")


def test_a_note_off_the_layout_on_a_part_or_not_one_line_is_rejected():
    document = layered() | {"notes": {"src/*/nope": "x", "src/*/api": "handlers", "src": "two\nlines", "src/*": ""}}
    assert problems(document) == [
        "layered.yaml: notes.src/*/nope: 'src/*/nope' matches no folder or file in layout",
        "layered.yaml: notes.src/*/api: 'src/*/api' is part 'api', whose note is its role",
        "layered.yaml: notes.src: must be one line of text",
        "layered.yaml: notes.src/*: must be one line of text",
    ]


def test_a_layer_naming_no_part_twice_or_importing_outward_is_rejected():
    document = layered() | {"layers": {"inside": ["store", "service", "api"], "again": ["store", "repo"],
                                       "wrong": ["api"], "empty": []}}
    document["layers"]["inside"] = ["api", "service", "store"]           # api imports service: outward
    assert problems(document) == [
        "layered.yaml: layers.inside: 'api' imports 'service', which is outward of it",
        "layered.yaml: layers.inside: 'service' imports 'store', which is outward of it",
        "layered.yaml: layers.again: part 'store' is already in layer 'inside'",
        "layered.yaml: layers.again: no part named 'repo'",
        "layered.yaml: layers.wrong: part 'api' is already in layer 'inside'",
        "layered.yaml: layers.empty: must be a list of parts, from the inside out",
    ]


def test_placement_must_list_every_part_exactly_once():
    document = layered() | {"placement": ["store", "store", "repo"]}
    assert problems(document) == [
        "layered.yaml: placement: part 'store' is listed twice",
        "layered.yaml: placement: no part named 'repo'",
        "layered.yaml: placement: missing parts 'api', 'service': list every part once",
    ]


def test_a_bad_naming_row_is_rejected():
    document = layered() | {"naming": [{"kind": "service", "where": [], "pattern": "x"}, "row",
                                       {"kind": "", "where": "a/", "pattern": "x", "example": "X", "colour": 1}]}
    assert problems(document) == [
        "layered.yaml: naming[0]: missing `example`",
        "layered.yaml: naming[0].where: must be a string or a list of strings",
        "layered.yaml: naming[1]: must be a mapping with `kind`, `where`, `pattern` and `example`",
        "layered.yaml: naming[2]: unknown key 'colour': use example, kind, pattern, where",
        "layered.yaml: naming[2].kind: must be a string",
    ]


def test_a_missing_version_is_rejected():
    document = layered()
    del document["xarch"]
    assert problems(document) == ["layered.yaml: missing format version: start the file with `xarch: 1`"]


@pytest.mark.parametrize("version", [2, 0, "1", True, 1.0, None])
def test_an_unknown_version_is_rejected(version):
    document = layered() | {"xarch": version}
    assert problems(document) == [f"layered.yaml: unknown format version {version!r}: this xarch reads `xarch: 1`"]


def test_unknown_top_level_keys_are_rejected():
    document = layered() | {"profile": "cli", "extra": 1}
    assert problems(document) == ["layered.yaml: unknown keys 'extra', 'profile': "
                                  "use docs, examples, layers, layout, name, naming, notes, parts, placement, rules, xarch"]


def test_missing_required_keys_are_reported():
    assert problems({"xarch": 1}) == ["layered.yaml: missing `name`", "layered.yaml: missing `layout`",
                                      "layered.yaml: missing `parts`"]


def test_a_rule_for_an_undefined_part_is_rejected():
    document = layered()
    document["rules"]["repo"] = ["store@own"]
    assert problems(document) == ["layered.yaml: rules.repo: no part named 'repo'"]


def test_a_rule_target_naming_an_undefined_part_is_rejected():
    document = layered()
    document["rules"]["api"] = ["api@own", "repo@own"]
    assert problems(document) == ["layered.yaml: rules.api: 'repo@own' names no part 'repo'"]


def test_an_example_for_an_undefined_part_is_rejected():
    document = layered() | {"examples": {"repo": {"path": "src/b/repo/x.py", "file": "x.py"}}}
    assert problems(document) == ["layered.yaml: examples.repo: no part named 'repo'"]


def test_a_part_path_the_layout_cannot_match_is_rejected():
    document = layered()
    document["parts"]["api"]["path"] = "src/*/handlers"
    document["parts"]["store"]["path"] = "src/each/store"
    assert problems(document) == [
        "layered.yaml: parts.api.path: 'src/*/handlers' matches no folder or file in layout",
        "layered.yaml: parts.store.path: 'src/each/store' matches no folder or file in layout (`*` matches `each`)",
    ]


def test_a_part_path_with_a_misplaced_star_is_rejected():
    document = layered()
    document["parts"]["api"]["path"] = "src/x*/api"
    assert problems(document) == [
        "layered.yaml: parts.api.path: 'src/x*/api' may hold one `*`, standing alone for the module's name"]


def test_a_path_two_parts_claim_is_rejected():
    document = layered()
    document["parts"]["handlers"] = {"path": "src/*/api", "role": "HTTP handlers again"}
    assert problems(document) == ["layered.yaml: parts.handlers.path: 'src/*/api' is already claimed by part 'api'"]


@pytest.mark.parametrize("target, problem", [
    ("store@mine", "'store@mine' has an unknown scope '@mine': use @own (the importer's module) or @any (any module)"),
    ("store@", "'store@' has an unknown scope '@': use @own (the importer's module) or @any (any module)"),
    ("store", "'store' is a part of every module: say store@own or store@any"),
    ("store@own/", "'store@own/' has an invalid path after the part"),
    ("store@own//x", "'store@own//x' has an invalid path after the part"),
    ("@own", "'@own' is not a target: use <part>, <part>@own, <part>@any, optionally followed by /<path>, or *"),
    ("*@own", "'*@own' names no part '*'"),
    (3, "3 is not a target: use <part>, <part>@own, <part>@any, optionally followed by /<path>, or *"),
])
def test_an_invalid_target_is_rejected(target, problem):
    document = layered()
    document["rules"]["store"] = [target]
    assert problems(document) == [f"layered.yaml: rules.store: {problem}"]


def test_a_scope_on_a_part_outside_the_modules_is_rejected():
    document = layered()
    document["layout"]["shared"] = {}
    document["parts"]["shared"] = {"path": "shared", "role": "shared code"}
    document["rules"]["api"] = ["shared@own"]
    assert problems(document) == ["layered.yaml: rules.api: 'shared@own' is not a part of a module: drop '@own'"]


def test_a_missing_docs_template_or_example_file_is_rejected(tmp_path):
    text = LAYERED + ("docs:\n  template: layered.md\n"
                      "examples:\n  service: { path: src/billing/service/charge.py, file: examples/charge.py }\n")
    path = write(tmp_path / "layered.yaml", text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: docs.template: no file 'layered.md' next to the architecture file",
        f"{path}: examples.service.file: no file 'examples/charge.py' next to the architecture file",
    )


def test_an_example_outside_its_part_or_with_inline_code_is_rejected():
    document = layered() | {"examples": {"service": {"path": "src/billing/api/x.py", "code": "pass"}}}
    assert problems(document) == [
        "layered.yaml: examples.service: unknown key 'code': use file, path",
        "layered.yaml: examples.service: missing `file`",
        "layered.yaml: examples.service.path: 'src/billing/api/x.py' is not inside part 'service' (src/*/service)",
    ]


def test_duplicate_part_names_are_rejected(tmp_path):
    text = LAYERED.replace('  store:   { path: "src/*/store"', '  api:     { path: "src/*/store"')
    path = write(tmp_path / "layered.yaml", text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (f"{path}: line 12: duplicate key 'api'",)


def test_duplicate_keys_in_json_are_rejected(tmp_path):
    path = write(tmp_path / "layered.json", '{"xarch": 1, "parts": {"api": {}, "api": {}}}')
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (f"{path}: duplicate key 'api'",)


def test_unknown_keys_inside_a_part_and_docs_are_rejected():
    document = layered() | {"docs": {"template": "layered.md", "style": "short"}}
    document["parts"]["api"]["colour"] = "blue"
    assert problems(document) == [
        "layered.yaml: parts.api: unknown key 'colour': use driver_proves, driver_test, entry, litmus, path, role",
        "layered.yaml: docs: unknown key 'style': use template",
    ]


def test_every_problem_is_listed_at_once():
    document = layered() | {"extra": 1}
    document["parts"]["api"]["path"] = "src/*/nope"
    document["rules"]["store"] = ["store@mine"]
    assert problems(document) == [
        "layered.yaml: unknown key 'extra': use docs, examples, layers, layout, name, naming, notes, parts, placement, "
        "rules, xarch",
        "layered.yaml: parts.api.path: 'src/*/nope' matches no folder or file in layout",
        "layered.yaml: rules.store: 'store@mine' has an unknown scope '@mine': use @own (the importer's module) "
        "or @any (any module)",
    ]                                                       # and the rules on api, a part already reported, are left alone


def test_a_bad_layout_entry_is_rejected():
    document = layered()
    document["layout"]["src"]["each"]["api"] = None
    document["layout"]["src"]["each"]["a/b"] = {}
    assert problems(document) == [
        "layered.yaml: layout.src.each.api: must be a folder (a mapping, {} if empty) or `file`, not None",
        "layered.yaml: layout.src.each: 'a/b' is not a folder or file name",
        "layered.yaml: parts.api.path: 'src/*/api' matches no folder or file in layout",
    ]


# --- a bad file yields errors, never a traceback ---


@pytest.mark.parametrize("text", [
    "", "null", "[]", "3", "just a string", "xarch: 1", "xarch: 1\nname: [a]\nlayout: 3\nparts: [1]\nrules: x\n",
    "xarch: 1\nname: n\nlayout: {each: file}\nparts: {}\n",
    "xarch: 1\nname: n\nlayout: {a: {each: {b: {each: {}}}}}\nparts: {}\n",
    "xarch: 1\nname: n\nlayout: {1: {}, null: {}, yes: file}\nparts: {1: {path: 1}, p: {path: [a]}, q: 3}\n",
    "xarch: 1\nname: n\nlayout: {}\nparts: {}\nrules: {x: [1, null, {}]}\ndocs: [1]\nexamples: {x: 1}\n",
    "xarch: 1\nname: n\nlayout: {a: {}}\nparts: {a: {path: a, role: r}}\ndocs: {template: 3}\n"
    "examples: {a: {path: 1, file: [x]}}\n",
    "xarch: 1\nname: n\nlayout: {a: {}}\nparts: {a: {path: a, role: r, entry: 1, driver_test: 3}}\n"
    "notes: [1]\nlayers: 3\nplacement: x\nnaming: {a: 1}\n",
    "xarch: 1\nname: n\nlayout: {a: {}}\nparts: {a: {path: a, role: r, driver_test: {file: [1]}}}\n"
    "notes: {1: x, null: y, a: [z]}\nlayers: {1: [a], x: [[1]], y: a}\nplacement: [[1], null]\n"
    "naming: [{kind: 1, where: [1], pattern: [], example: {}}, null]\n",
    "xarch: 1\n  bad: indentation\n", "{unclosed", "a: &x [*x]\n", "? [a, b]\n: 1\n", "xarch: !!python/object:os.system x\n",
])
def test_a_bad_file_raises_invalid_architecture(tmp_path, text):
    path = write(tmp_path / "bad.yaml", text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems and all(p.startswith(f"{path}: ") for p in caught.value.problems)


def test_a_missing_file_is_reported(tmp_path):
    path = tmp_path / "nowhere.yaml"
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (f"{path}: cannot read the file: No such file or directory",)


def test_an_unknown_bundled_name_is_reported():
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture("desktop")
    assert caught.value.problems == (
        "desktop: no bundled architecture 'desktop': use one of cli, web, or a path to a .yaml or .json file",)


def test_the_bundled_names_are_listed():
    assert build_architectures().bundled() == ("cli", "web")
