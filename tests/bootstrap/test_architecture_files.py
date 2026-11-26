"""Architecture files loaded through the wiring: from disk as YAML or JSON, with the files they name beside them, and
by bundled name."""
import json
from pathlib import Path

import pytest

from tests.bootstrap.project import bundled_profiles
from xarch.bootstrap.wiring import load_architecture
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.profile_values.placement import Repeat, Target

LAYERED = """\
name: layered
parts:
  src/<module>/:
    api/:
      role: "HTTP handlers"
      litmus: "Does it parse a request and call a service?"
      imports:
        may: [module.service]
    service/:
      role: "business logic"
      litmus: "Does it decide what is allowed?"
      imports:
        may: [module.store]
    store/:
      role: "database access"
      litmus: "Does it touch the database?"
"""
LAYERED_DATA = {
    "name": "layered",
    "parts": {"src/<module>/": {
        "api/": {"role": "HTTP handlers", "litmus": "Does it parse a request and call a service?",
                 "imports": {"may": ["module.service"]}},
        "service/": {"role": "business logic", "litmus": "Does it decide what is allowed?",
                     "imports": {"may": ["module.store"]}},
        "store/": {"role": "database access", "litmus": "Does it touch the database?"}}},
}
"""LAYERED as data, as its YAML reads."""
MUST_BE_A_MAPPING = "must be a mapping of keys"


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_a_valid_file_loads(tmp_path):
    architecture = load_architecture(write(tmp_path / "layered.yaml", LAYERED))
    assert architecture.name == "layered"
    assert architecture.repeats == (Repeat("module", ("src",)),)
    assert architecture.instance_tree(architecture.repeats[0]) == {"api": {}, "service": {}, "store": {}}
    assert architecture.top_level_tree() == {"src": {}}
    api = architecture.parts["api"]
    assert (api.name, api.path, api.role, api.litmus, api.entry) == (
        "api", ("src", "*", "api"), "HTTP handlers", "Does it parse a request and call a service?", False)
    assert architecture.rules["service"] == (Target("store", "own"),)
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
    write(tmp_path / "examples" / "src" / "billing" / "service" / "charge.py", "def charge(): ...\n")
    write(tmp_path / "examples" / "src" / "billing" / "store" / "repo.py", "class Repo: ...\n")
    text = LAYERED + ("docs:\n  pages:\n    architecture.md: {from: layered.md}\n"
                      "  examples: [examples]\n"
                      "  example_notes: {src/billing/service/charge.py: charged once}\n")
    architecture = load_architecture(write(tmp_path / "layered.yaml", text))
    assert [(doc.path, doc.source, doc.note) for doc in architecture.docs] == [(("architecture.md",), "layered.md", "")]
    assert {name: (e.part, e.path, e.file, e.note) for name, e in architecture.examples.items()} == {
        "src/billing/service/charge.py": ("service", ("src", "billing", "service", "charge.py"),
                                          "examples/src/billing/service/charge.py", "charged once"),
        "src/billing/store/repo.py": ("store", ("src", "billing", "store", "repo.py"),
                                      "examples/src/billing/store/repo.py", ""),
    }


def test_the_entry_point_an_untested_part_folder_notes_layers_and_naming_load(tmp_path):
    text = LAYERED.replace(
        'role: "HTTP handlers"\n', 'role: "HTTP handlers"\n      routes/: one file per route\n').replace(
        'role: "database access"\n', 'role: "database access"\n      untested: "reached through the service"\n') + (
        "layers:\n  inside: [store, service, api]\n"
        "docs:\n  entry: api\n"
        "  naming:\n"
        "    - {kind: service, where: service/, pattern: thing and `Service`, example: [BillingService]}\n")
    architecture = load_architecture(write(tmp_path / "layered.yaml", text))
    entry = architecture.entry
    assert entry is not None and (entry.name, entry.path, entry.role, entry.litmus, entry.entry) == (
        "api", ("src", "*", "api"), "HTTP handlers", "Does it parse a request and call a service?", True)
    assert architecture.parts["store"].untested == "reached through the service"
    assert [part.name for part in architecture.parts.values() if part.entry] == ["api"]
    assert architecture.notes == {("src", "*", "api", "routes"): "one file per route"}
    assert architecture.layers == {"inside": ("store", "service", "api")}
    assert architecture.placement == ("api", "service", "store")
    assert [(n.kind, n.where, n.pattern, n.example) for n in architecture.naming] == [
        ("service", ("service/",), "thing and `Service`", ("BillingService",))]


def test_a_missing_docs_template_example_folder_or_file_is_rejected(tmp_path):
    text = LAYERED + ("docs:\n  pages:\n    architecture.md: {from: layered.md}\n"
                      "  examples: [examples]\n"
                      "files:\n  tests/guard.py: {from: guard.py}\n")
    path = write(tmp_path / "layered.yaml", text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (
        f"{path}: docs.examples[0]: no folder 'examples' holding a file next to the profile file",
        f"{path}: docs.pages.architecture.md.from: no file 'layered.md' next to the architecture file",
        f"{path}: files.tests/guard.py.from: no file 'guard.py' next to the architecture file",
    )


def test_duplicate_part_names_are_rejected(tmp_path):
    text = LAYERED.replace('    store/:\n', '    api/:\n')
    path = write(tmp_path / "layered.yaml", text)
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (f"{path}: line 14: duplicate key 'api/'",)


def test_duplicate_keys_in_json_are_rejected(tmp_path):
    path = write(tmp_path / "layered.json", '{"parts": {"api": {}, "api": {}}}')
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(path)
    assert caught.value.problems == (f"{path}: duplicate key 'api'",)


@pytest.mark.parametrize("text, expected", [
    pytest.param('', [MUST_BE_A_MAPPING], id='an empty file'),
    pytest.param('null', [MUST_BE_A_MAPPING], id='null'),
    pytest.param('[]', [MUST_BE_A_MAPPING], id='a list'),
    pytest.param('3', [MUST_BE_A_MAPPING], id='a number'),
    pytest.param('just a string', [MUST_BE_A_MAPPING], id='a string'),
    pytest.param('xarch: 2', ["unknown key 'xarch': use based_on, checks, docs, evals, excluded, fakes, files, guards, "
                              "hints, language, layers, name, never, parts, reserved, review, structure, testing, tiers",
                              'missing `name`', 'missing `parts`'], id='a version line is an unknown key'),
    pytest.param('name: [a]\nparts: [1]\nnever: x\nlayers: 3\ntiers: 4\nfakes: 5\nguards: 6\n'
                 'excluded: 7\nhints: 8\nfiles: 9\ndocs: 10\n',
                 ['`name` must be a non-empty string',
                  'never: must be a mapping of list names to lists of dotted names, such as '
                  '{pure: [datetime.datetime.now, socket]}',
                  'parts: must be the folder tree of the app: folders ending in /, files with their extension',
                  'layers: must be a mapping of names to lists of parts, from the inside out',
                  'tiers: must be a mapping of tier names to {proves, litmus, ...}, in the order their litmus tests run',
                  "fakes: must be a mapping {folder, for} and optionally prefix and tiers: the folder of the fakes "
                  "below the tests folder, the parts they stand in for, how a fake's name starts, and the tiers that "
                  "may import them besides",
                  'guards: must be a mapping of guard names to their parameters, such as {no-comments: {}}',
                  'missing `testing`: `tiers` must recognise a test file by its name: write testing: <preset>, or '
                  'testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}',
                  'docs: must be a mapping of {entry, pages, naming, examples, example_notes}',
                  'files: must be a mapping of paths to {from}, such as {tests/rules.py: {from: guard.py}}',
                  'excluded: must be a mapping of folders below the app to the reason each is not its source, such as '
                  '{vendor: copied code}',
                  'hints: must be a mapping of rule ids to one line of text, such as {may-import: see the docs}'],
                 id='every top-level value of the wrong type'),
    pytest.param('name: n\nparts: {a/<x>/<y>/: {name: p, role: r}}\n',
                 ["parts.p: 'a/<x>/<y>/' has two repeating steps, <x> and <y>: a repeating folder cannot sit inside "
                  "another, so give each its own folder"],
                 id='a path with two repeating folders'),
    pytest.param('name: n\nparts: {1/: {role: r}, p/: {litmus: [a]}, q: 3}\n',
                 ["parts: '1/' is named '1', which is not a part name: write name: with letters, digits, '_' and '-'",
                  'parts.p: missing `role`',
                  "parts: unknown key 'q': a key under parts is a folder ending in / or a file ending in .py",
                  'parts.p.litmus: must be a string'],
                 id='keys that are not names'),
    pytest.param('name: n\nparts: {1: {role: a}, null: {}, yes: {role: b}}\n',
                 ["line 2: duplicate key 'True'"],
                 id='a key 1 and a key yes are one key, True'),
    pytest.param('name: n\nparts: {a/: {role: r, imports: {may: [parts.a]}}}\n',
                 ["parts.a.imports.may: 'parts.a' is implied: a part may always import itself; remove it"],
                 id='an imports.may that only says a part may import itself'),
    pytest.param('name: n\nparts: {a/: {role: r, uses: {never: l}}}\nnever: {l: [open]}\n',
                 ["never.l: 'open' is a Python builtin, which a bare name does not ban: write builtins.open"],
                 id='a bare builtin in a never list'),
    pytest.param('name: n\nparts: {a/: {role: r, untested: 3, litmus: 4}}\n'
                 'docs: {entry: 1, pages: 2, naming: 3, examples: 4}\n',
                 ['parts.a.litmus: must be a string',
                  'parts.a.untested: must be one line of text: why no tier tests the part',
                  'docs.examples: must be a list of folders next to the profile file, each an example project, such '
                  'as [examples/shared]',
                  'docs.entry: no part named 1',
                  'docs.pages: must be a mapping of paths to {from, note}, such as {statement.md: {from: '
                  'docs/statement.md}}',
                  'docs.naming: must be a list of rows such as {kind, where, pattern, example}'],
                 id='the optional keys of a part and of docs of the wrong type'),
    pytest.param('name: n\nparts: {a/: {role: r, untested: [1]}}\n'
                 'layers: {1: [a], x: [[1]], y: a}\n'
                 'docs: {naming: [{kind: 1, where: [1], pattern: [], example: {}}, null]}\n',
                 ['parts.a.untested: must be one line of text: why no tier tests the part',
                  "layers: 1 is not a name: use letters, digits, '_' and '-'",
                  'layers.x: no part named [1]',
                  'layers.y: must be a list of parts, from the inside out',
                  'docs.naming[0].kind: must be a string',
                  'docs.naming[0].pattern: must be a string',
                  'docs.naming[0].where: must be a string or a list of strings',
                  'docs.naming[0].example: must be a string or a list of strings',
                  'docs.naming[1]: must be a mapping with `kind`, `where`, `pattern` and `example`'],
                 id='the entries of the optional keys of the wrong type'),
    pytest.param('name: n\nparts: {a/: {role: r}}\n'
                 'tiers: {unit: 3, 1: {}, integ: {proves: 1, litmus: [], docs: {example: 3, helpers: x, subject: 1}}}\n',
                 ["parts.a: no tier tests it: give it `tests: <tier>`, or `untested: <reason>`",
                  'tiers.unit: must be a mapping, {} if it takes nothing',
                  'tiers: 1 is not a tier name: one line of text',
                  'tiers.integ.proves: must be one line of text',
                  'tiers.integ.litmus: must be text: the question that tells a test belongs to the tier',
                  'tiers.integ.docs.subject: must be one line of text',
                  'tiers.integ.docs.example: must be a path in an example project, such as src/billing/charge.py',
                  'tiers.integ.docs.helpers: must be a list of paths in an example project',
                  'missing `testing`: `tiers` must recognise a test file by its name: write testing: <preset>, or '
                  'testing: {files: [<pattern>, ...], declared: [{function: <pattern>}]}'],
                 id='tiers of the wrong shape'),
    pytest.param('name: n\nparts: {a/: {role: r}}\nfiles: {1: {from: 2}, x: [1], y: {z: 1}}\n',
                 ['files.1: must be a path of plain names below the project root',
                  'files.x: must be a mapping such as {from: <file>}',
                  "files.y: unknown key 'z': use fill, from, pinned",
                  'files.y: missing `from`, the template file'],
                 id='files of the wrong shape'),
    pytest.param('name: n\ntesting: pytest\ntiers: {unit: {}}\nparts: {a/: {role: r, tier: secret-value}}\n',
                 ["parts.a: unknown key 'tier': renamed in 0.3.0: write tests; use holds, imports, "
                  "litmus, name, optional, package_only, role, shared, tests, untested, uses",
                  "parts.a: no tier tests it: give it `tests: <tier>`, or `untested: <reason>`"],
                 id='a part still writing tier'),
    pytest.param('name: n\nnever: {pure: [socket]}\nparts: {a/: {role: r, forbidden: secret-list}}\n',
                 ["parts.a: unknown key 'forbidden': moved in 0.3.0: write uses: {never: <list>}; use holds, "
                  "imports, litmus, name, optional, package_only, role, shared, tests, untested, uses"],
                 id='a part still writing forbidden'),
    pytest.param('name: n\nparts: {a/: {role: r}}\nxarch2: 1\nrules: {a: []}\n',
                 ["unknown keys 'rules', 'xarch2': use based_on, checks, docs, evals, excluded, fakes, files, guards, hints, "
                  "language, layers, name, never, parts, reserved, review, structure, testing, tiers"],
                 id='two keys that are nowhere'),
    pytest.param('name: n\n  bad: indentation\n',
                 ['not valid YAML: line 2, column 6: mapping values are not allowed here'],
                 id='bad indentation'),
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
    assert bundled_profiles() == ("cli", "web")
