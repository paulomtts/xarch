"""Architecture files loaded through the wiring: from disk as YAML or JSON, with the files they name beside them, and
by bundled name."""
import json
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_architectures, load_architecture
from xarch.modules.spec.contract import Part, Target
from xarch.modules.spec.domain.errors import InvalidArchitecture

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
LAYERED_DATA = {
    "xarch": 1, "name": "layered",
    "layout": {"src": {"singular": "module", "each": {"api": {}, "service": {}, "store": {}}}},
    "parts": {"api": {"path": "src/*/api", "role": "HTTP handlers", "litmus": "Does it parse a request and call a service?"},
              "service": {"path": "src/*/service", "role": "business logic", "litmus": "Does it decide what is allowed?"},
              "store": {"path": "src/*/store", "role": "database access", "litmus": "Does it touch the database?"}},
    "rules": {"api": ["api@own", "service@own"], "service": ["service@own", "store@own"], "store": ["store@own"]},
}
"""LAYERED as data, as its YAML reads."""


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
    json_file = write(tmp_path / "layered.json", json.dumps(LAYERED_DATA, indent="\t"))
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
    assert [(doc.path, doc.source, doc.note) for doc in architecture.docs] == [(("architecture.md",), "layered.md", "")]
    assert {name: (e.part, e.path, e.file, e.note) for name, e in architecture.examples.items()} == {
        "charge": ("service", ("src", "billing", "service", "charge.py"), "examples/charge.py", ""),
        "refund": ("service", ("src", "billing", "service", "refund.py"), "examples/charge.py",
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
    assert [(n.kind, n.where, n.pattern, n.example) for n in architecture.naming] == [
        ("service", ("service/",), "thing and `Service`", ("BillingService",))]


def test_a_missing_docs_template_or_example_file_is_rejected(tmp_path):
    text = LAYERED + ("docs:\n  architecture.md: {from: layered.md}\n"
                      "files:\n  tests/guard.py: {from: guard.py}\n"
                      "examples:\n"
                      "  charge: { part: service, path: src/billing/service/charge.py, file: examples/charge.py }\n")
    path = write(tmp_path / "layered.yaml", text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: docs.architecture.md.from: no file 'layered.md' next to the architecture file",
        f"{path}: files.tests/guard.py.from: no file 'guard.py' next to the architecture file",
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


@pytest.mark.parametrize("text, expected", [
    pytest.param('',
                 ['must be a mapping of keys, starting with `xarch: 1`'],
                 id='an empty file'),
    pytest.param('null',
                 ['must be a mapping of keys, starting with `xarch: 1`'],
                 id='null'),
    pytest.param('[]',
                 ['must be a mapping of keys, starting with `xarch: 1`'],
                 id='a list'),
    pytest.param('3',
                 ['must be a mapping of keys, starting with `xarch: 1`'],
                 id='a number'),
    pytest.param('just a string',
                 ['must be a mapping of keys, starting with `xarch: 1`'],
                 id='a string'),
    pytest.param('xarch: 1',
                 ['missing `name`', 'missing `layout`', 'missing `parts`'],
                 id='only the version'),
    pytest.param('xarch: 1\nname: [a]\nlayout: 3\nparts: [1]\nrules: x\n',
                 ['`name` must be a non-empty string',
                  'layout: must be a mapping of folder and file names',
                  'parts: must be a mapping of part names to {path, role, litmus}',
                  'rules: must be a mapping of part names to lists of targets'],
                 id='every top-level value of the wrong type'),
    pytest.param('xarch: 1\nname: n\nlayout: {each: file}\nparts: {}\n',
                 ['layout: `each` needs `singular` beside it, the name of one instance of the folder',
                  "layout.each: must be a mapping of what every `each` folder holds, not 'file'"],
                 id='an each folder that is a file and has no singular name'),
    pytest.param('xarch: 1\nname: n\nlayout: {a: {each: {b: {each: {}}}}}\nparts: {}\n',
                 ['layout.a: `each` needs `singular` beside it, the name of one instance of the folder',
                  'layout.a.each.b: `each` needs `singular` beside it, the name of one instance of the folder',
                  'layout: `each` may appear only once'],
                 id='an each folder inside another'),
    pytest.param('xarch: 1\n'
                 'name: n\n'
                 'layout: {1: {}, null: {}, yes: file}\n'
                 'parts: {1: {path: 1}, p: {path: [a]}, q: 3}\n',
                 ["line 3: duplicate key 'True'"],
                 id='a key 1 and a key yes are one key, True'),
    pytest.param('xarch: 1\n'
                 'name: n\n'
                 'layout: {1: {}, null: {}, no: file}\n'
                 'parts: {1: {path: 1}, p: {path: [a]}, q: 3}\n',
                 ['layout: 1 is not a folder or file name',
                  'layout: None is not a folder or file name',
                  'layout: False is not a folder or file name',
                  "parts: 1 is not a part name: use letters, digits, '_' and '-'",
                  'parts.p: missing `role`',
                  "parts.p.path: must be a path such as 'src/*/api'",
                  'parts.q: must be a mapping with `path` and `role`, and optionally `litmus`'],
                 id='keys that are not names'),
    pytest.param('xarch: 1\nname: n\nlayout: {}\nparts: {}\nrules: {x: [1, null, {}]}\ndocs: [1]\nexamples: {x: 1}\n',
                 ["rules.x: no part named 'x'",
                  'docs: must be a mapping of paths to {from, note}, such as {statement.md: {from: docs/statement.md}}',
                  'examples.x: must be a mapping with `part`, `path` and `file`, and optionally `note`'],
                 id='rules, docs and examples of the wrong shape'),
    pytest.param('xarch: 1\n'
                 'name: n\n'
                 'layout: {a: {}}\n'
                 'parts: {a: {path: a, role: r}}\n'
                 'docs: {template: 3}\n'
                 'examples: {a: {path: 1, file: [x], part: [a], note: 2}, 3: {}}\n',
                 ['docs.template: must be a mapping such as {from: <file>, note: <text>}',
                  "examples.a.part: no part named ['a']",
                  "examples.a.path: must be a path such as 'src/billing/service/charge.py'",
                  'examples.a.file: must be a file name',
                  'examples.a.note: must be one line of text',
                  "examples: 3 is not an example name: use letters, digits, '_' and '-'"],
                 id='docs and examples whose values have the wrong type'),
    pytest.param('xarch: 1\n'
                 'name: n\n'
                 'layout: {a: {}}\n'
                 'parts: {a: {path: a, role: r, entry: 1, untested: 3}}\n'
                 'notes: [1]\n'
                 'layers: 3\n'
                 'placement: x\n'
                 'naming: {a: 1}\n',
                 ['parts.a.untested: must be one line of text: why no tier tests the part',
                  'parts.a.entry: must be true or false',
                  'notes: must be a mapping of layout paths to one line of text, such as {src/shared: ...}',
                  'layers: must be a mapping of names to lists of parts, from the inside out',
                  'placement: must be a list of every part, in the order their litmus tests run',
                  'naming: must be a list of rows such as {kind, where, pattern, example}'],
                 id='the optional keys of the wrong type'),
    pytest.param('xarch: 1\n'
                 'name: n\n'
                 'layout: {a: {}}\n'
                 'parts: {a: {path: a, role: r, untested: [1]}}\n'
                 'notes: {1: x, null: y, a: [z]}\n'
                 'layers: {1: [a], x: [[1]], y: a}\n'
                 'placement: [[1], null]\n'
                 'naming: [{kind: 1, where: [1], pattern: [], example: {}}, null]\n',
                 ['parts.a.untested: must be one line of text: why no tier tests the part',
                  "notes: 1: must be a path such as 'src/*/api'",
                  "notes: None: must be a path such as 'src/*/api'",
                  "notes.a: 'a' is part 'a', whose note is its role",
                  "layers: 1 is not a name: use letters, digits, '_' and '-'",
                  'layers.x: no part named [1]',
                  'layers.y: must be a list of parts, from the inside out',
                  'placement: no part named [1]',
                  'placement: no part named None',
                  "placement: missing part 'a': list every part once",
                  'naming[0].kind: must be a string',
                  'naming[0].pattern: must be a string',
                  'naming[0].where: must be a string or a list of strings',
                  'naming[0].example: must be a string or a list of strings',
                  'naming[1]: must be a mapping with `kind`, `where`, `pattern` and `example`'],
                 id='the entries of the optional keys of the wrong type'),
    pytest.param('xarch: 1\n'
                 'name: n\n'
                 'layout: {a: {}}\n'
                 'parts: {a: {path: a, role: r}}\n'
                 'docs: {testing: [1]}\n'
                 'tiers: [1, {name: [x], subject: [[1], {}], proves: 1, litmus: [], example: {path: [1], file: 3, note: {}}}]\n',
                 ['tiers[0]: must be a mapping with `name`, `subject`, `proves`, `may_touch` and `litmus`',
                  'tiers[1]: missing `may_touch`',
                  "tiers[1].name: must be one line of text, such as 'unit'",
                  'tiers[1].proves: must be one line of text',
                  'tiers[1].litmus: must be text: the question that tells a test belongs to the tier',
                  'tiers[1].subject: no part named [1]',
                  'tiers[1].subject: no part named {}',
                  "tiers[1].example.path: must be a path such as 'tests/src/billing/api/invoice_checks.py'",
                  'tiers[1].example.file: must be a file name',
                  'tiers[1].example.note: must be one line of text',
                  "tiers: no tier tests part 'a': add it to a tier's subject, or give the part `untested: <reason>`",
                  'docs.testing: must be a mapping such as {from: <file>, note: <text>}',
                  'missing `tests`: `tiers` must recognise a test file by its name: add '
                  'tests: {files: [<pattern>, ...], functions: <pattern>}'],
                 id='tiers of the wrong shape'),
    pytest.param('xarch: 1\n'
                 'name: n\n'
                 'layout: {a: {}}\n'
                 'parts: {a: {path: a, role: r}}\n'
                 'files: {1: {from: 2}, x: [1], y: {z: 1}}\n',
                 ['files.1: must be a path of plain names below the project root',
                  'files.x: must be a mapping such as {from: <file>}',
                  "files.y: unknown key 'z': use fill, from, pinned",
                  'files.y: missing `from`, the template file'],
                 id='files of the wrong shape'),
    pytest.param('xarch: 1\n  bad: indentation\n',
                 ['not valid YAML: line 2, column 6: mapping values are not allowed here'],
                 id='bad indentation'),
    pytest.param('{unclosed',
                 ["not valid YAML: line 1, column 10: expected ',' or '}', but got '<stream end>'"],
                 id='an unclosed mapping'),
    pytest.param('a: &x [*x]\n',
                 ['not valid YAML: line 1, column 4: found unconstructable recursive node'],
                 id='a recursive anchor'),
    pytest.param('? [a, b]\n: 1\n',
                 ['not valid YAML: line 1, column 3: a mapping key must be a plain value'],
                 id='a key that is a list'),
    pytest.param('xarch: !!python/object:os.system x\n',
                 ["not valid YAML: line 1, column 8: could not determine a constructor for the tag "
                  "'tag:yaml.org,2002:python/object:os.system'"],
                 id='a python tag'),
])
def test_a_bad_file_raises_invalid_architecture_naming_every_problem(tmp_path, text, expected):
    path = write(tmp_path / "bad.yaml", text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == tuple(f"{path}: {problem}" for problem in expected)


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
