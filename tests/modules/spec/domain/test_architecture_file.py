"""Loading and validating an architecture file: every problem reported, prefixed by the file, never a traceback."""

import pytest

from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Doc, Target


def layered() -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"api": {}, "service": {}, "store": {}}}},
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


def test_targets_carry_scope_and_sub_path():
    """A part with no row may import nothing."""
    document = layered()
    document["layout"]["shared"] = {}
    document["parts"]["shared"] = {"path": "shared", "role": "shared code"}
    document["rules"]["api"] = ["service@any/values/ids", "shared/text", "*"]
    rules = parse_architecture(document, "layered.yaml", lambda r: True).rules
    assert rules["api"] == (Target("service", "any", ("values", "ids")), Target("shared", "none", ("text",)),
                            Target("*"))
    assert rules["shared"] == ()


def test_a_file_in_the_layout_and_a_part_on_it():
    document = layered()
    document["layout"]["src"]["each"]["main.py"] = "file"
    document["parts"]["main"] = {"path": "src/*/main.py", "role": "the entry"}
    architecture = parse_architecture(document, "layered.yaml", lambda r: True)
    assert architecture.instance_tree()["main.py"] is None
    assert architecture.parts["main"].path == ("src", "*", "main.py")


def test_the_new_keys_are_optional():
    architecture = parse_architecture(layered(), "layered.yaml", lambda r: True)
    assert architecture.entry is None and architecture.notes == {} and architecture.layers == {}
    assert architecture.placement == () and architecture.naming == ()


def test_two_entry_points_are_rejected():
    document = layered()
    document["parts"]["api"]["entry"] = True
    document["parts"]["store"]["entry"] = True
    document["parts"]["service"]["entry"] = "yes"
    assert problems(document) == ["layered.yaml: parts.service.entry: must be true or false",
                                  "layered.yaml: parts: only one part may be the entry point, not 'api', 'store'"]


def test_a_note_off_the_layout_on_a_part_or_not_one_line_is_rejected():
    document = layered() | {"notes": {"src/*/nope": "x", "src/*/api": "handlers", "src": "two\nlines", "src/*": ""}}
    assert problems(document) == [
        "layered.yaml: notes.src/*/nope: 'src/*/nope' matches no folder or file in layout",
        "layered.yaml: notes.src/*/api: 'src/*/api' is part 'api', whose note is its role",
        "layered.yaml: notes.src: must be one line of text",
        "layered.yaml: notes.src/*: must be one line of text",
    ]


def test_a_layer_naming_no_part_twice_or_importing_outward_is_rejected():
    """With api inside service in a layer, api imports service, which is outward of it."""
    document = layered() | {"layers": {"inside": ["store", "service", "api"], "again": ["store", "repo"],
                                       "wrong": ["api"], "empty": []}}
    document["layers"]["inside"] = ["api", "service", "store"]
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
                                  "use docs, examples, fakes, guards, layers, layout, libraries, name, naming, notes, parts, "
                                  "placement, rules, tiers, xarch"]


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
    document = layered() | {"examples": {"x": {"part": "repo", "path": "src/b/repo/x.py", "file": "x.py"}}}
    assert problems(document) == ["layered.yaml: examples.x.part: no part named 'repo'"]


def test_an_example_needs_a_name_part_path_and_file_and_a_one_line_note():
    document = layered() | {"examples": {"a b": {}, "y": 1, "z": {"note": "two\nlines"}}}
    assert problems(document) == [
        "layered.yaml: examples: 'a b' is not an example name: use letters, digits, '_' and '-'",
        "layered.yaml: examples.y: must be a mapping with `part`, `path` and `file`, and optionally `note`",
        "layered.yaml: examples.z: missing `part`",
        "layered.yaml: examples.z: missing `path`",
        "layered.yaml: examples.z: missing `file`",
        "layered.yaml: examples.z.note: must be one line of text",
    ]


def test_an_example_inside_a_part_nested_in_its_part_is_rejected():
    document = layered()
    document["layout"]["src"]["each"]["store"] = {"sql": {}}
    document["parts"]["sql"] = {"path": "src/*/store/sql", "role": "queries"}
    document["examples"] = {"q": {"part": "store", "path": "src/b/store/sql/q.py", "file": "q.py"},
                            "r": {"part": "store", "path": "src/b/store/repo.py", "file": "r.py"}}
    assert problems(document) == [
        "layered.yaml: examples.q.path: 'src/b/store/sql/q.py' is inside part 'sql' (src/*/store/sql), "
        "which lies within part 'store'"]


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
        "layered.yaml: parts.api.path: 'src/x*/api' may hold one `*`, standing alone for the name of an `each` folder"]


def test_a_path_two_parts_claim_is_rejected():
    document = layered()
    document["parts"]["handlers"] = {"path": "src/*/api", "role": "HTTP handlers again"}
    assert problems(document) == ["layered.yaml: parts.handlers.path: 'src/*/api' is already claimed by part 'api'"]


@pytest.mark.parametrize("target, problem", [
    ("store@mine", "'store@mine' has an unknown scope '@mine': use @own (the importer's own `each` folder) or @any (any `each` folder)"),
    ("store@", "'store@' has an unknown scope '@': use @own (the importer's own `each` folder) or @any (any `each` folder)"),
    ("store", "'store' lies in the `each` folder: say store@own or store@any"),
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
    assert problems(document) == ["layered.yaml: rules.api: 'shared@own' does not lie in the `each` folder: drop '@own'"]


def test_an_example_outside_its_part_or_with_inline_code_is_rejected():
    document = layered() | {"examples": {"x": {"part": "service", "path": "src/billing/api/x.py", "code": "pass"}}}
    assert problems(document) == [
        "layered.yaml: examples.x: unknown key 'code': use file, note, part, path",
        "layered.yaml: examples.x: missing `file`",
        "layered.yaml: examples.x.path: 'src/billing/api/x.py' is not inside part 'service' (src/*/service)",
    ]


def test_unknown_keys_inside_a_part_and_docs_are_rejected():
    document = layered() | {"docs": {"a.md": {"from": "layered.md", "style": "short"}}}
    document["parts"]["api"]["colour"] = "blue"
    assert problems(document) == [
        "layered.yaml: parts.api: unknown key 'colour': use entry, litmus, path, role, untested",
        "layered.yaml: docs.a.md: unknown key 'style': use from, note",
    ]


def test_every_problem_is_listed_at_once():
    """The rules naming api, a part already reported, are not reported again."""
    document = layered() | {"extra": 1}
    document["parts"]["api"]["path"] = "src/*/nope"
    document["rules"]["store"] = ["store@mine"]
    assert problems(document) == [
        "layered.yaml: unknown key 'extra': use docs, examples, fakes, guards, layers, layout, libraries, name, naming, notes, "
        "parts, placement, rules, tiers, xarch",
        "layered.yaml: parts.api.path: 'src/*/nope' matches no folder or file in layout",
        "layered.yaml: rules.store: 'store@mine' has an unknown scope '@mine': use @own (the importer's own `each` "
        "folder) or @any (any `each` folder)",
    ]


def test_a_bad_layout_entry_is_rejected():
    document = layered()
    document["layout"]["src"]["each"]["api"] = None
    document["layout"]["src"]["each"]["a/b"] = {}
    assert problems(document) == [
        "layered.yaml: layout.src.each.api: must be a folder (a mapping, {} if empty) or `file`, not None",
        "layered.yaml: layout.src.each: 'a/b' is not a folder or file name",
        "layered.yaml: parts.api.path: 'src/*/api' matches no folder or file in layout",
    ]


def test_docs_files_and_folders_keep_their_order_and_notes():
    document = layered() | {"docs": {
        "statement.md": {"from": "docs/statement.md", "note": "what and why"},
        "adrs/": {"note": "decisions"},
        "adrs/0000.md": {"from": "docs/adr.md"},
        "artifacts/guards/_template.md": {"from": "docs/guard.md"},
    }}
    assert parse_architecture(document, "layered.yaml", lambda r: True).docs == (
        Doc(("statement.md",), "docs/statement.md", "what and why"),
        Doc(("adrs",), None, "decisions"),
        Doc(("adrs", "0000.md"), "docs/adr.md"),
        Doc(("artifacts", "guards", "_template.md"), "docs/guard.md"),
    )


@pytest.mark.parametrize("docs, expected", [
    ([], ["docs: must be a mapping of paths to {from, note}, such as {statement.md: {from: docs/statement.md}}"]),
    ({"a.md": "x.md"}, ["docs.a.md: must be a mapping such as {from: <file>, note: <text>}"]),
    ({"a.md": {}}, ["docs.a.md: missing `from`, the template file"]),
    ({"a.md": {"from": 3}}, ["docs.a.md.from: must be a file name"]),
    ({"a.md": {"from": "x.md", "extra": 1}}, ["docs.a.md: unknown key 'extra': use from, note"]),
    ({"a.md": {"from": "x.md", "note": ["no"]}}, ["docs.a.md.note: must be one line of text"]),
    ({"d/": {"from": "x.md"}}, ["docs.d/: a folder takes only `note`"]),
    ({"d/": {"note": "n"}}, ["docs.d/: holds no file"]),
    ({"../a.md": {"from": "x.md"}}, ["docs.../a.md: must be a path of plain names below the docs folder"]),
    ({"/a.md": {"from": "x.md"}}, ["docs./a.md: must be a path of plain names below the docs folder"]),
    ({"a//b.md": {"from": "x.md"}}, ["docs.a//b.md: must be a path of plain names below the docs folder"]),
    ({"a.md": {"from": "x.md"}, "a.md/b.md": {"from": "x.md"}}, ["docs.a.md/b.md: 'a.md' is a file, not a folder"]),
    ({"a.md": {"from": "nowhere.md"}}, ["docs.a.md.from: no file 'nowhere.md' next to the architecture file"]),
])
def test_bad_docs_are_rejected(docs, expected):
    assert problems(layered() | {"docs": docs}, lambda relative: relative == "x.md") == [
        f"layered.yaml: {line}" for line in expected]


def test_the_singular_name_of_an_instance_sits_beside_each_and_is_not_a_folder():
    document = layered()
    document["layout"]["src"]["singular"] = "feature"
    architecture = parse_architecture(document, "layered.yaml", lambda r: True)
    assert architecture.singular == "feature"
    assert architecture.instance_tree() == {"api": {}, "service": {}, "store": {}}
    assert architecture.top_level_tree() == {"src": {}}
    assert "singular" not in architecture.layout["src"]


def test_a_layout_with_no_each_folder_has_no_singular_name():
    document = layered()
    document["layout"] = {"src": {}}
    document["parts"] = {"api": {"path": "src", "role": "everything"}}
    document["rules"] = {}
    assert parse_architecture(document, "layered.yaml", lambda r: True).singular == ""


def test_an_each_folder_needs_a_singular_name():
    document = layered()
    del document["layout"]["src"]["singular"]
    assert problems(document) == [
        "layered.yaml: layout.src: `each` needs `singular` beside it, the name of one instance of the folder"]


@pytest.mark.parametrize("value", [None, 3, "", "two words", "a/b", ["feature"]])
def test_a_malformed_singular_name_is_a_problem(value):
    document = layered()
    document["layout"]["src"]["singular"] = value
    assert problems(document) == [
        f"layered.yaml: layout.src.singular: must be one word naming an instance of the `each` folder, not {value!r}"]
