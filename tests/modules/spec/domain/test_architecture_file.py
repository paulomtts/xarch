"""Loading and validating an architecture file: every problem reported, prefixed by the file, never a traceback."""

import pytest

from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.errors import InvalidArchitecture
from xarch.modules.spec.domain.values import Doc, ProjectFile, Target


def layered() -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"api": {}, "service": {}, "store": {}}}},
        "parts": {"api": {"path": "src/*/api", "role": "HTTP handlers"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "store": {"path": "src/*/store", "role": "database access"}},
        "rules": {"api": ["service@own"], "service": ["store@own"], "store": []},
    }


def problems(document, has_file=lambda relative: True, folder_files=None) -> list[str]:
    with pytest.raises(InvalidArchitecture) as caught:
        parse_architecture(document, "layered.yaml", has_file, folder_files)
    assert caught.value.reason == "\n".join(caught.value.problems)
    return list(caught.value.problems)


DROP = object()
"""A change's value that removes the key."""


def edited(*changes: tuple[tuple, object]) -> dict:
    """layered() with each (path of keys, value) change made: the value set at the path, or the key dropped."""
    document = layered()
    for path, value in changes:
        holder = document
        for key in path[:-1]:
            holder = holder[key]
        if value is DROP:
            del holder[path[-1]]
        else:
            holder[path[-1]] = value
    return document


EACH_PARTS_UNMATCHED = [f"parts.{p}.path: 'src/*/{p}' matches no folder or file in layout" for p in ("api", "service", "store")]


@pytest.mark.parametrize("document, expected", [
    pytest.param(["xarch", 1], ["must be a mapping of keys, starting with `xarch: 1`"],
                 id="a document that is not a mapping stops at once"),
    pytest.param(edited((("name",), "")), ["`name` must be a non-empty string"], id="an empty name"),
    pytest.param(edited((("name",), "  ")), ["`name` must be a non-empty string"], id="a blank name"),
    pytest.param(edited((("name",), 3)), ["`name` must be a non-empty string"], id="a name that is not a string"),
    pytest.param(edited((("layout", "lib"), {"singular": "lib", "each": {}})), ["layout: `each` may appear only once"],
                 id="a second each folder"),
    pytest.param(edited((("layout", "src", "lib"), {"singular": "lib", "each": {}})),
                 ["layout: `each` may appear only once"], id="an each folder beside another one"),
    pytest.param(edited((("layout",), "src")), ["layout: must be a mapping of folder and file names",
                                                *EACH_PARTS_UNMATCHED], id="a layout that is not a mapping"),
    pytest.param(edited((("layout", "src", "each"), "x")),
                 ["layout.src.each: must be a mapping of what every `each` folder holds, not 'x'",
                  *EACH_PARTS_UNMATCHED], id="an each folder that is not a mapping"),
    pytest.param(edited((("parts",), [])), ["parts: must be a mapping of part names to {path, role, litmus}",
                                            "rules.api: no part named 'api'", "rules.service: no part named 'service'",
                                            "rules.store: no part named 'store'"], id="parts that are not a mapping"),
    pytest.param(edited((("parts", "9x"), {"path": "src", "role": "r"})),
                 ["parts: '9x' is not a part name: use letters, digits, '_' and '-'"], id="a part name that is no name"),
    pytest.param(edited((("parts", "api"), "x")),
                 ["parts.api: must be a mapping with `path` and `role`, and optionally `litmus`"],
                 id="a part that is not a mapping"),
    pytest.param(edited((("parts", "api"), {})), ["parts.api: missing `path`", "parts.api: missing `role`"],
                 id="a part missing its path and role"),
    pytest.param(edited((("parts", "api", "role"), 3), (("parts", "api", "litmus"), ["a"])),
                 ["parts.api.role: must be a string", "parts.api.litmus: must be a string"],
                 id="a role and a litmus that are not strings"),
    pytest.param(edited((("parts", "api", "path"), "")), ["parts.api.path: must be a path such as 'src/*/api'"],
                 id="an empty part path"),
    pytest.param(edited((("parts", "api", "colour"), 1), (("parts", "api", "size"), 2)),
                 ["parts.api: unknown keys 'colour', 'size': use entry, litmus, path, role, untested"],
                 id="two unknown keys of a part are named together"),
    pytest.param(edited((("notes",), [])),
                 ["notes: must be a mapping of layout paths to one line of text, such as {src/shared: ...}"],
                 id="notes that are not a mapping"),
    pytest.param(edited((("notes",), {3: "x"})), ["notes: 3: must be a path such as 'src/*/api'"],
                 id="a note whose key is not a path"),
    pytest.param(edited((("rules",), [])), ["rules: must be a mapping of part names to lists of targets"],
                 id="rules that are not a mapping"),
    pytest.param(edited((("rules", "api"), "api@own")),
                 ["rules.api: must be a list of targets such as [api@own, shared]"], id="a rule that is not a list"),
    pytest.param(edited((("layers",), [])),
                 ["layers: must be a mapping of names to lists of parts, from the inside out"],
                 id="layers that are not a mapping"),
    pytest.param(edited((("layers",), {"a b": ["api"]})),
                 ["layers: 'a b' is not a name: use letters, digits, '_' and '-'"], id="a layer name that is no name"),
    pytest.param(edited((("placement",), "api")),
                 ["placement: must be a list of every part, in the order their litmus tests run"],
                 id="a placement that is not a list"),
    pytest.param(edited((("placement",), ["api", "service"])),
                 ["placement: missing part 'store': list every part once"], id="a placement missing one part"),
    pytest.param(edited((("naming",), {})), ["naming: must be a list of rows such as {kind, where, pattern, example}"],
                 id="naming that is not a list"),
    pytest.param(edited((("naming",), [{"kind": "k", "where": "w", "pattern": 3, "example": "e"}])),
                 ["naming[0].pattern: must be a string"], id="a naming pattern that is not a string"),
    pytest.param(edited((("examples",), [])), ["examples: must be a mapping of example names to {part, path, file}"],
                 id="examples that are not a mapping"),
    pytest.param(edited((("examples",), {"x": {"part": "api", "path": "src/*/api/x.py", "file": "x.py"}})),
                 ["examples.x.path: must be a path such as 'src/billing/service/charge.py'"],
                 id="an example path naming no instance"),
    pytest.param(edited((("examples",), {"x": {"part": "api", "path": "", "file": "x.py"}})),
                 ["examples.x.path: must be a path such as 'src/billing/service/charge.py'"],
                 id="an empty example path"),
    pytest.param(edited((("examples",), {"x": {"part": "api", "path": "src/b/api/x.py", "file": ""}})),
                 ["examples.x.file: must be a file name"], id="an empty example file name"),
])
def test_a_bad_value_is_rejected(document, expected):
    assert problems(document) == [f"layered.yaml: {line}" for line in expected]


def test_targets_carry_scope_and_sub_path():
    """A part with no row may import only itself."""
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
                                  "use docs, examples, excluded, fakes, files, forbidden, guards, hints, layers, layout, "
                                  "libraries, name, naming, notes, parts, placement, rules, tests, tiers, xarch"]


def test_missing_required_keys_are_reported():
    assert problems({"xarch": 1}) == ["layered.yaml: missing `name`", "layered.yaml: missing `layout`",
                                      "layered.yaml: missing `parts`"]


def test_a_rule_for_an_undefined_part_is_rejected():
    document = layered()
    document["rules"]["repo"] = ["store@own"]
    assert problems(document) == ["layered.yaml: rules.repo: no part named 'repo'"]


def test_a_rule_target_naming_an_undefined_part_is_rejected():
    document = layered()
    document["rules"]["api"] = ["repo@own"]
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


IMPLIED_IN_INSTANCE = ("a part may always import itself, its own instance of the `each` folder; remove it "
                       "(store@any, another instance's too, stays allowed)")


@pytest.mark.parametrize("owner, target, problem", [
    pytest.param("store", "store@own", f"layered.yaml: rules.store: 'store@own' is implied: {IMPLIED_IN_INSTANCE}",
                 id="a part in the each folder naming its own instance is rejected as implied"),
    pytest.param("store", "store@own/sql", f"layered.yaml: rules.store: 'store@own/sql' is implied: {IMPLIED_IN_INSTANCE}",
                 id="so is a sub-path of it, which says less than the whole"),
    pytest.param("shared", "shared",
                 "layered.yaml: rules.shared: 'shared' is implied: a part may always import itself; remove it",
                 id="a part outside the each folder naming itself is rejected as implied"),
    pytest.param("shared", "shared/text",
                 "layered.yaml: rules.shared: 'shared/text' is implied: a part may always import itself; remove it",
                 id="so is a sub-path of it"),
])
def test_a_rule_that_only_says_a_part_may_import_itself_is_rejected(owner, target, problem):
    document = layered()
    document["layout"]["shared"] = {}
    document["parts"]["shared"] = {"path": "shared", "role": "shared code"}
    document["rules"][owner] = [target]
    assert problems(document) == [problem]


def test_a_rule_naming_another_instance_of_the_part_itself_says_more_and_is_kept():
    document = layered()
    document["rules"]["store"] = ["store@any"]
    assert parse_architecture(document, "layered.yaml", lambda r: True).rules["store"] == (Target("store", "any"),)


def test_a_rule_naming_another_part_of_the_same_kind_is_not_implied():
    document = layered()
    document["rules"]["store"] = ["service@own"]
    assert parse_architecture(document, "layered.yaml", lambda r: True).rules["store"] == (Target("service", "own"),)


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
        "layered.yaml: unknown key 'extra': use docs, examples, excluded, fakes, files, forbidden, guards, hints, "
        "layers, layout, libraries, name, naming, notes, parts, placement, rules, tests, tiers, xarch",
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
    ({"g/a.md": {"from": "x.md"}, "g/a.md/b.md": {"from": "x.md"}},
     ["docs.g/a.md/b.md: 'g/a.md' is a file, not a folder"]),
    ({"a.md": {"from": "nowhere.md"}}, ["docs.a.md.from: no file 'nowhere.md' next to the architecture file"]),
])
def test_bad_docs_are_rejected(docs, expected):
    assert problems(layered() | {"docs": docs}, lambda relative: relative == "x.md") == [
        f"layered.yaml: {line}" for line in expected]


def test_files_keep_their_order_and_name_their_template():
    document = layered() | {"files": {
        "tests/architecture/test_rules.py": {"from": "guard.py"},
        "Makefile": {"from": "make.txt"},
    }}
    assert parse_architecture(document, "layered.yaml", lambda r: True).files == (
        ProjectFile(("tests", "architecture", "test_rules.py"), "guard.py"),
        ProjectFile(("Makefile",), "make.txt"),
    )


def test_an_architecture_without_files_declares_none():
    assert parse_architecture(layered(), "layered.yaml", lambda r: True).files == ()


@pytest.mark.parametrize("files, expected", [
    ([], ["files: must be a mapping of paths to {from}, such as {tests/rules.py: {from: guard.py}}"]),
    ({"a.py": "x.py"}, ["files.a.py: must be a mapping such as {from: <file>}"]),
    ({"a.py": {}}, ["files.a.py: missing `from`, the template file"]),
    ({"a.py": {"from": 3}}, ["files.a.py.from: must be a file name"]),
    ({"a.py": {"from": "x.py", "note": "n"}}, ["files.a.py: unknown key 'note': use fill, from, pinned"]),
    ({"a.py": {"from": "nowhere.py"}}, ["files.a.py.from: no file 'nowhere.py' next to the architecture file"]),
    ({"../a.py": {"from": "x.py"}}, ["files.../a.py: must be a path of plain names below the project root"]),
    ({"/a.py": {"from": "x.py"}}, ["files./a.py: must be a path of plain names below the project root"]),
    ({"a//b.py": {"from": "x.py"}}, ["files.a//b.py: must be a path of plain names below the project root"]),
    ({"/": {"from": "x.py"}}, ["files./: must be a path of plain names below the project root"]),
    ({3: {"from": "x.py"}}, ["files.3: must be a path of plain names below the project root"]),
    ({"docs/project/a.md": {"from": "x.py"}, "docs/project/a.md/b": {"from": "x.py"}},
     ["files.docs/project/a.md/b: 'docs/project/a.md' is a file, not a folder"]),
])
def test_bad_files_are_rejected(files, expected):
    assert problems(layered() | {"files": files}, lambda relative: relative == "x.py") == [
        f"layered.yaml: {line}" for line in expected]



def folders(relative):
    return {"preset": ("a.txt", "sub/b.bin"), "empty": ()}.get(relative.rstrip("/"))


def files_of(entries):
    return parse_architecture(layered() | {"files": entries}, "layered.yaml",
                              lambda relative: relative == "x.py", folders).files


def test_a_key_ending_in_a_slash_is_a_folder_entry_which_is_not_filled_unless_it_says_so():
    found = files_of({"{{app}}/web/ui/design/": {"from": "preset/"}, "docs/": {"from": "preset", "fill": True},
                      "x.txt": {"from": "x.py"}, "y.txt": {"from": "x.py", "fill": False}})
    assert found == (ProjectFile(("{{app}}", "web", "ui", "design"), "preset", False, True, False),
                     ProjectFile(("docs",), "preset", False, True, True),
                     ProjectFile(("x.txt",), "x.py", False, False, True),
                     ProjectFile(("y.txt",), "x.py", False, False, False))


@pytest.mark.parametrize("files, expected", [
    ({"d/": {}}, ["files.d/: missing `from`, the folder"]),
    ({"d/": {"from": 3}}, ["files.d/.from: must be a folder name"]),
    ({"d/": {"from": "x.py"}}, ["files.d/.from: 'x.py' is a file, not a folder: a folder entry copies a folder"]),
    ({"d/": {"from": "nowhere"}}, ["files.d/.from: no folder 'nowhere' next to the architecture file"]),
    ({"d/": {"from": "empty"}}, ["files.d/.from: the folder 'empty' holds no file"]),
    ({"d/": {"from": "preset", "pinned": True}},
     ["files.d/.pinned: a folder entry cannot be pinned: a project edits what it copies"]),
    ({"d": {"from": "preset"}}, ["files.d.from: 'preset' is a folder, not a file: end the key with / to copy a folder"]),
    ({"d/": {"from": "preset", "fill": "no"}}, ["files.d/.fill: must be true or false: whether `{{app}}` is filled in"]),
    ({"d/": {"from": "preset"}, "d/a.txt": {"from": "x.py"}}, ["files.d/a.txt: lies inside the folder entry 'd/'"]),
    ({"d/": {"from": "preset"}, "d/e/": {"from": "preset"}}, ["files.d/e/: lies inside the folder entry 'd/'"]),
    ({"d/e/": {"from": "preset"}, "d/": {"from": "preset"}}, ["files.d/e/: lies inside the folder entry 'd/'"]),
    ({"d/": {"from": "preset"}, "d": {"from": "x.py"}}, ["files.d: is also a folder entry"]),
    ({"d/{{other}}/": {"from": "preset"}}, ["files.d/{{other}}/: must be a path of plain names below the project root; "
                                            "the only placeholder is {{app}}"]),
    ({"docs/project/": {"from": "preset"}}, ["files.docs/project/: collides with docs.statement.md, written to "
                                             "docs/project/statement.md"]),
])
def test_bad_folder_entries_are_rejected(files, expected):
    document = layered() | {"docs": {"statement.md": {"from": "x.py"}}, "files": files}
    assert problems(document, lambda relative: relative == "x.py", folders) == [
        f"layered.yaml: {line}" for line in expected]


def test_a_file_colliding_with_a_doc_in_a_folder_names_the_docs_path():
    document = layered() | {"docs": {"guides/a.md": {"from": "x.py"}}, "files": {"docs/project/guides/a.md": {"from": "x.py"}}}
    assert problems(document) == ["layered.yaml: files.docs/project/guides/a.md: collides with docs.guides/a.md, "
                                  "written to docs/project/guides/a.md"]


@pytest.mark.parametrize("path", ["docs/project/statement.md", "docs/project/statement.md/more", "docs/project"])
def test_a_file_may_not_collide_with_a_doc(path):
    document = layered() | {"docs": {"statement.md": {"from": "x.py"}}, "files": {path: {"from": "x.py"}}}
    assert problems(document, lambda relative: True) == [
        f"layered.yaml: files.{path}: collides with docs.statement.md, written to docs/project/statement.md"]


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


def test_a_part_is_shown_as_the_docs_show_it_below_its_instance_and_ending_in_a_slash_for_a_folder():
    document = layered()
    document["layout"] = {"src": {"singular": "feature", "each": {"core": {}, "main.py": "file"}}}
    document["parts"] = {"core": {"path": "src/*/core", "role": "r"}, "main": {"path": "src/*/main.py", "role": "r"},
                         "src": {"path": "src", "role": "r"}}
    document["rules"] = {}
    architecture = parse_architecture(document, "layered.yaml", lambda r: True)
    assert {name: architecture.shown(part) for name, part in architecture.parts.items()} == {
        "core": "core/", "main": "main.py", "src": "src/"}


def test_a_file_at_the_top_of_the_layout_is_a_file_and_may_hold_a_part():
    document = layered()
    document["layout"]["__main__.py"] = "file"
    document["parts"]["main"] = {"path": "__main__.py", "role": "the entry shim"}
    architecture = parse_architecture(document, "layered.yaml", lambda r: True)
    assert architecture.top_level_tree()["__main__.py"] is None
    assert architecture.is_file(("__main__.py",)) and architecture.shown(architecture.parts["main"]) == "__main__.py"
