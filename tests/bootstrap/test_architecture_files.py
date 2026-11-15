"""Architecture files loaded through the wiring: from disk as YAML or JSON, with the files they name beside them, and
by bundled name."""
import json
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_architectures, load_architecture
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Doc, Example, Naming, Part, Target
from xarch.platform.data_files import DataFileReader

LAYERED = """\
xarch: 1
name: layered
layout:
  src:
    singular: module
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


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_a_valid_file_loads(tmp_path):
    architecture = load_architecture(write(tmp_path / "layered.yaml", LAYERED))
    assert architecture.name == "layered"
    assert architecture.instance_root() == ("src",)
    assert architecture.singular == "module"
    assert architecture.instance_tree() == {"api": {}, "service": {}, "store": {}}
    assert architecture.top_level_tree() == {"src": {}}
    assert architecture.parts["api"] == Part("api", ("src", "*", "api"), "HTTP handlers",
                                             "Does it parse a request and call a service?")
    assert architecture.rules["service"] == (Target("service", "own"), Target("store", "own"))
    assert architecture.docs == () and architecture.examples == {}


def test_an_equivalent_json_file_loads_the_same(tmp_path):
    """Tab-indented: valid JSON, but not valid YAML."""
    yaml_file = write(tmp_path / "layered.yaml", LAYERED)
    json_file = write(tmp_path / "layered.json", json.dumps(DataFileReader().parse(LAYERED), indent="\t"))
    assert "\t" in json_file.read_text()
    assert load_architecture(json_file) == load_architecture(yaml_file)
    assert load_architecture(str(json_file)) == load_architecture(yaml_file)


def test_docs_template_and_examples_resolve_next_to_the_file(tmp_path):
    write(tmp_path / "layered.md", "# {name}\n")
    write(tmp_path / "examples" / "charge.py", "def charge(): ...\n")
    text = LAYERED + ("docs:\n  architecture.md: {from: layered.md}\n"
                      "examples:\n"
                      "  charge: { part: service, path: src/billing/service/charge.py, file: examples/charge.py }\n"
                      "  refund: { part: service, path: src/billing/service/refund.py, file: examples/charge.py,\n"
                      "            note: 'the same file, shown twice' }\n")
    architecture = load_architecture(write(tmp_path / "layered.yaml", text))
    assert architecture.docs == (Doc(("architecture.md",), "layered.md"),)
    assert architecture.examples == {
        "charge": Example("charge", "service", ("src", "billing", "service", "charge.py"), "examples/charge.py"),
        "refund": Example("refund", "service", ("src", "billing", "service", "refund.py"), "examples/charge.py",
                          "the same file, shown twice"),
    }


def test_the_entry_point_an_untested_part_notes_layers_placement_and_naming_load(tmp_path):
    text = LAYERED.replace('  api:     { path: "src/*/api",', '  api:     { entry: true, path: "src/*/api",').replace(
        '  store:   { path: "src/*/store",', '  store:   { untested: "reached through the service", path: "src/*/store",') + (
        "notes:\n  src: every module\n"
        "layers:\n  inside: [store, service, api]\n"
        "placement: [store, service, api]\n"
        "naming:\n  - {kind: service, where: service/, pattern: thing and `Service`, example: [BillingService]}\n")
    architecture = load_architecture(write(tmp_path / "layered.yaml", text))
    assert architecture.entry == Part("api", ("src", "*", "api"), "HTTP handlers",
                                      "Does it parse a request and call a service?", True)
    assert architecture.parts["store"].untested == "reached through the service"
    assert [part.name for part in architecture.parts.values() if part.entry] == ["api"]
    assert architecture.notes == {("src",): "every module"}
    assert architecture.layers == {"inside": ("store", "service", "api")}
    assert architecture.placement == ("store", "service", "api")
    assert architecture.naming == (Naming("service", ("service/",), "thing and `Service`", ("BillingService",)),)


def test_a_missing_docs_template_or_example_file_is_rejected(tmp_path):
    text = LAYERED + ("docs:\n  architecture.md: {from: layered.md}\n"
                      "examples:\n"
                      "  charge: { part: service, path: src/billing/service/charge.py, file: examples/charge.py }\n")
    path = write(tmp_path / "layered.yaml", text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: docs.architecture.md.from: no file 'layered.md' next to the architecture file",
        f"{path}: examples.charge.file: no file 'examples/charge.py' next to the architecture file",
    )


def test_duplicate_part_names_are_rejected(tmp_path):
    text = LAYERED.replace('  store:   { path: "src/*/store"', '  api:     { path: "src/*/store"')
    path = write(tmp_path / "layered.yaml", text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (f"{path}: line 13: duplicate key 'api'",)


def test_duplicate_keys_in_json_are_rejected(tmp_path):
    path = write(tmp_path / "layered.json", '{"xarch": 1, "parts": {"api": {}, "api": {}}}')
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (f"{path}: duplicate key 'api'",)


@pytest.mark.parametrize("text", [
    "", "null", "[]", "3", "just a string", "xarch: 1", "xarch: 1\nname: [a]\nlayout: 3\nparts: [1]\nrules: x\n",
    "xarch: 1\nname: n\nlayout: {each: file}\nparts: {}\n",
    "xarch: 1\nname: n\nlayout: {a: {each: {b: {each: {}}}}}\nparts: {}\n",
    "xarch: 1\nname: n\nlayout: {1: {}, null: {}, yes: file}\nparts: {1: {path: 1}, p: {path: [a]}, q: 3}\n",
    "xarch: 1\nname: n\nlayout: {}\nparts: {}\nrules: {x: [1, null, {}]}\ndocs: [1]\nexamples: {x: 1}\n",
    "xarch: 1\nname: n\nlayout: {a: {}}\nparts: {a: {path: a, role: r}}\ndocs: {template: 3}\n"
    "examples: {a: {path: 1, file: [x], part: [a], note: 2}, 3: {}}\n",
    "xarch: 1\nname: n\nlayout: {a: {}}\nparts: {a: {path: a, role: r, entry: 1, untested: 3}}\n"
    "notes: [1]\nlayers: 3\nplacement: x\nnaming: {a: 1}\n",
    "xarch: 1\nname: n\nlayout: {a: {}}\nparts: {a: {path: a, role: r, untested: [1]}}\n"
    "notes: {1: x, null: y, a: [z]}\nlayers: {1: [a], x: [[1]], y: a}\nplacement: [[1], null]\n"
    "naming: [{kind: 1, where: [1], pattern: [], example: {}}, null]\n",
    "xarch: 1\nname: n\nlayout: {a: {}}\nparts: {a: {path: a, role: r}}\ndocs: {testing: [1]}\n"
    "tiers: [1, {name: [x], subject: [[1], {}], proves: 1, litmus: [], example: {path: [1], file: 3, note: {}}}]\n",
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
