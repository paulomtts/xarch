"""Filling a docs template from an architecture: the author writes the prose, the file supplies the structure.

A template is markdown with placeholders, each `{{name}}` or `{{name:argument}}`, replaced by text built from the
architecture. Prose, diagrams and code examples stay as the author wrote them; only these are generated:

    {{tree}}               the layout, one line per folder and file, below a root line the template writes itself;
                           a part's line carries its role, any other line its note from `folders`
    {{rules_table}}        the dependency rules as a table: one row per part, in the order of `parts`, saying what
                           the part may import (its own part is implied, so it is not listed)
    {{layers:<name>}}      the chain `layers.<name>` as `a/` → `b/` → ..., each part by its path
    {{placement}}          the order of `parts` as `a` → `b` → ..., each part by its name
    {{litmus:<part>}}      the part's litmus test, as a "> [!TIP]" block
    {{naming}}             the `naming` rows as a table
    {{entry}}              the entry point's path, e.g. web
    {{docs_tree}}          the `docs` of the architecture as the contents of the project docs folder, one line per
                           file and folder, each as the file declares it, indented to sit below a folder the
                           template writes itself, with the notes aligned: a folder holding one file and declared no
                           note of its own shows as `<file>; <note>` on its own line
    {{example:<path>}}     a file of an example project of `docs.examples`, by its path in the project: its header
                           line, `# <path>` (`: <note>` after it if `docs.example_notes` has one), then its file as the
                           file holds it, without trailing blank lines
    {{example:<a>, <b>}}   several examples one after another in one block, one blank line between them
    {{tiers}}              the `tiers` as a table, one row per tier in order: its name, its subject (each part by its
                           path; or its `docs.subject`), what it proves and what it may touch
    {{untested}}           one paragraph per part marked `untested`: "`<part>/` gets no tier of its own: <reason>."
    {{tier_index:<n>}}     the index entries of {{tier_litmus:<n>}}, one per tier, indented as a subsection of section <n>
    {{tier_litmus:<n>}}    each tier as a subsection of section <n>, "### <n>.<i> <tier>", holding its litmus test as
                           a "> [!TIP]" block, its lines joined into one
    {{tier_files}}         each tier's `one_file_per` and `cases_from`, as a table
    {{tier_data}}          each tier's `data`, as a table
    {{tier_helpers}}       the helper files of all tiers in one block, each under its header line, `# <path>` (its
                           note after it, in parentheses)
    {{guards}}             one line per check `xarch check` runs: the structure, the rules, the libraries (with
                           `libraries`), what each part may not use (with `forbidden`), the tiers (with `tiers`), types-only
                           (one line per tier with `types_only`), the test tree and the cycles (with a repeating folder),
                           then each guard of `guards`, in order
    {{tier_examples}}      each tier's example test in one block, under its header line `# <tier>: <path>` (its note
                           after the path, in parentheses), as {{example:...}} writes them; a tier with no example
                           is left out

Where {{example:...}} or {{tier_examples}} stands alone, it writes the whole fenced block, whose language comes from the
files' extension (the language of the app names its own, and the data file of file types names the others, see
file_types), so the examples of one block share an extension. Written inside a fenced block of the template's own, it
writes only the examples, and the template adds the rest of the block: an excerpt that is not a file of the example
project, such as a few lines of a function, stays in the template as the author wrote it.

A placeholder the template does not use is fine. One that is unknown, or that needs what the architecture does not
define (a part, a layer, an entry point, a placement, an example, the tiers or what a tier leaves out), fails the whole
template with every problem listed.
"""
from __future__ import annotations

import bisect
import re
from collections.abc import Callable, Mapping

from xarch.kernel.logic.imports import may_import, shown_target
from xarch.kernel.placement import EACH, EVERYTHING
from xarch.modules.spec.application.logic.layout_walk import docs_name, is_file
from xarch.modules.spec.domain.errors import InvalidTemplate
from xarch.modules.spec.domain.published import DEFAULT_TESTS
from xarch.modules.spec.domain.values import (
    NAME,
    Architecture,
    ClosedTree,
    DeadCode,
    Doc,
    FileType,
    Guard,
    Language,
    Layout,
    NoDuplicates,
    NoTwins,
    PackageOnly,
    Part,
    PassThrough,
    PrivateImports,
    Subject,
    Tier,
)
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import ScenarioCoverage, StandIns

Texts = Mapping[str, str]
"""Texts a profile's docs quote from its files, by what names them: each example's file by the example's name, each
tier's example test and helper by the tier's name or the helper's file."""
FileTypes = Mapping[str, FileType]
"""The kinds of file the docs quote besides the language of the app, by the ending of the file's name."""

PLACEHOLDER = re.compile(r"\{\{(.*?)\}\}")
FENCE = re.compile(r"^```", re.MULTILINE)
"""A line that opens or closes a fenced block."""
DOCS_NOTE_GAP = 8
"""Spaces between the longest line of the docs tree and its notes."""
NOTE_GAP = 3
"""Spaces between the longest line of the tree and its note."""
ARROW = " → "


def fill(template: str, architecture: Architecture, source: str, examples: Mapping[str, str] | None = None,
         tier_examples: Mapping[str, str] | None = None, *, file_types: FileTypes) -> str:
    """The template with every placeholder replaced; raises InvalidTemplate listing every problem.

    examples is the text of each example's file, by name, and tier_examples the text of each tier's example test, by
    tier name; file_types what the docs say of a quoted file that is not of the language of the app, by its ending.
    """
    problems: list[str] = []
    fences = [m.start() for m in FENCE.finditer(template)]

    def replace(match: re.Match[str]) -> str:
        name, _, argument = match[1].strip().partition(":")
        render = _RENDERERS.get(name)
        if render is None or (argument == "") == (name in _WITH_ARGUMENT):
            problems.append(f"unknown placeholder {match[0]}: use {', '.join(_KNOWN)}")
            return match[0]
        in_fence = bisect.bisect(fences, match.start()) % 2 == 1
        try:
            return render(architecture, argument.strip(), examples or {}, tier_examples or {}, in_fence, file_types)
        except _Missing as missing:
            problems.append(f"{match[0]}: {missing}")
            return match[0]

    text = PLACEHOLDER.sub(replace, template)
    if problems:
        raise InvalidTemplate(source, problems)
    return text


class _Missing(Exception):
    """What a placeholder needs and the architecture does not define."""


def _tree(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    roles = {part.path: part.role for part in architecture.parts.values()}
    lines = list(_tree_lines(architecture.layout, (), "", {**architecture.notes, **roles}, architecture.repeats))
    width = max((len(label) for label, note in lines if note), default=0) + NOTE_GAP
    return "\n".join(f"{label:<{width}}{note}" if note else label for label, note in lines)


def _tree_lines(tree: Layout, path: tuple[str, ...], indent: str,
                notes: dict[tuple[str, ...], str], repeats: tuple[Repeat, ...]) -> list[tuple[str, str]]:
    """The tree's lines; a repeating folder is shown as `<word>`, how one instance of it is named."""
    lines: list[tuple[str, str]] = []
    for i, (name, sub) in enumerate(tree.items()):
        last = i == len(tree) - 1
        here = path + (name,)
        word = next((repeat.word for repeat in repeats if repeat.root == path), "")
        shown = (f"<{word}>" if name == EACH else name) + ("" if sub is None else "/")
        lines.append((f"{indent}{'└── ' if last else '├── '}{shown}", notes.get(here, "")))
        if sub:
            lines += _tree_lines(sub, here, indent + ("    " if last else "│   "), notes, repeats)
    return lines


def _docs_tree(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    if not architecture.docs:
        raise _Missing("the architecture declares no `docs`")
    lines = _doc_lines(architecture.docs, (), "    ")
    width = max(len(label) for label, _ in lines) + DOCS_NOTE_GAP
    return "\n".join(f"{label:<{width}}{note}" if note else label for label, note in lines)


def _doc_lines(docs: tuple[Doc, ...], folder: tuple[str, ...], indent: str) -> list[tuple[str, str]]:
    """(label, note) for what lies directly in a folder, in the order the docs declare it."""
    below = [doc for doc in docs if doc.path[:len(folder)] == folder and len(doc.path) > len(folder)]
    names = list(dict.fromkeys(doc.path[len(folder)] for doc in below))
    lines: list[tuple[str, str]] = []
    for i, name in enumerate(names):
        last = i == len(names) - 1
        here = folder + (name,)
        own = next((doc for doc in below if doc.path == here), None)
        inside = [doc for doc in below if doc.path[:len(here)] == here and len(doc.path) > len(here)]
        branch = indent + ("└── " if last else "├── ")
        if own is not None and not own.is_folder:
            lines.append((branch + name, own.note))
        elif own is None and len(inside) == 1 and not inside[0].is_folder and len(inside[0].path) == len(here) + 1:
            note = inside[0].path[-1] + (f"; {inside[0].note}" if inside[0].note else "")
            lines.append((f"{branch}{name}/", note))
        else:
            lines.append((f"{branch}{name}/", own.note if own is not None else ""))
            lines += _doc_lines(docs, here, indent + ("    " if last else "│   "))
    return lines


def _rules_table(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    rows = [f"| `{docs_name(architecture, part)}` | {_may_import(architecture, part)} |"
            for part in architecture.parts.values()]
    return "\n".join(["| Part | May import |", "|---|---|", *rows])


def _may_import(architecture: Architecture, part: Part) -> str:
    """What a part may import besides itself, in the order of its rule."""
    return may_import(architecture.rules.get(part.name, ()), _folders(architecture), architecture.words())


def _folders(architecture: Architecture) -> dict[str, str]:
    return {name: docs_name(architecture, part) for name, part in architecture.parts.items()}


def _target(architecture: Architecture, target: Target) -> str:
    return shown_target(target, _folders(architecture))


def _layers(architecture: Architecture, name: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    if name not in architecture.layers:
        known = ", ".join(architecture.layers) or "none"
        raise _Missing(f"the architecture has no layer '{name}' (its layers: {known})")
    return ARROW.join(f"`{docs_name(architecture, architecture.parts[part])}`" for part in architecture.layers[name])


def _placement(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    if not architecture.placement:
        raise _Missing("the architecture has no placement order: list its `parts` in the order the litmus tests run")
    return ARROW.join(f"`{name}`" for name in architecture.placement)


def _litmus(architecture: Architecture, name: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    part = _part(architecture, name)
    if not part.litmus:
        raise _Missing(f"part '{name}' has no litmus test")
    return f"> [!TIP]\n> **Litmus test.** {part.litmus}"


def _naming(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    if not architecture.naming:
        raise _Missing("the architecture has no `docs.naming`")
    rows = [f"| {row.kind} | {_ticked(row.where)} | {row.pattern} | {_ticked(row.example)} |"
            for row in architecture.naming]
    return "\n".join(["| Kind | Where | Pattern | Example |", "|---|---|---|---|", *rows])


def _entry(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    return "/".join(_entry_part(architecture).path)


def _example(architecture: Architecture, names: str, texts: Texts, _t: Texts, in_fence: bool, file_types: FileTypes) -> str:
    """The example files, each under its header line, one blank line apart; in a fence unless already in one."""
    chosen = [name.strip() for name in names.split(",")]
    unknown = [name for name in chosen if name not in architecture.examples]
    if unknown:
        known = ", ".join(architecture.examples) or "none"
        raise _Missing(f"the architecture has no example {_quoted(unknown)} (its examples: {known})")
    unread = [name for name in chosen if name not in texts]
    if unread:
        raise _Missing(f"the file of example {_quoted(unread)} was not read")
    examples = [architecture.examples[name] for name in chosen]
    return _block([(f"{'/'.join(example.path)}{': ' + example.note if example.note else ''}", example.file,
                    texts[example.name]) for example in examples], in_fence, architecture.language, file_types)


def _block(files: list[tuple[str, str, str]], in_fence: bool, language: Language, file_types: FileTypes) -> str:
    """(header, file, text): each text under its header as a comment, one blank line apart, fenced unless in_fence; a
    file of the language of the app is named by it, any other as file_types says of its ending."""
    suffixes = {_suffix(file) for _, file, _ in files}
    if len(suffixes) > 1:
        raise _Missing(f"one block cannot mix files of different kinds ({', '.join(sorted(suffixes))})")
    suffix = suffixes.pop()
    kind = file_types.get(suffix, FileType())
    comment = kind.comment or language.checked.comment
    body = "\n\n".join(f"{comment} {header}\n" + text.rstrip("\n") for header, _, text in files)
    if in_fence:
        return body
    named = language.name if suffix == language.checked.extension else kind.fence or suffix.lstrip('.')
    return f"```{named}\n{body}\n```"


def _tiers(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    rows = [f"| {tier.name} | {_subject(architecture, tier)} | {tier.proves} | {tier.may_touch} |"
            for tier in _tiers_of(architecture)]
    return "\n".join(["| Tier | Subject | Proves | May touch |", "|---|---|---|---|", *rows])


def _subject(architecture: Architecture, tier: Tier) -> str:
    """The tier's subject_text, or its parts by path: consecutive paths of one part share an "and"."""
    if tier.subject_text:
        return tier.subject_text
    groups: list[tuple[str, list[str]]] = []
    for subject in tier.subject:
        shown = f"`{_subject_path(architecture, subject)}`"
        if groups and groups[-1][0] == subject.part:
            groups[-1][1].append(shown)
        else:
            groups.append((subject.part, [shown]))
    return ", ".join(_and(paths) for _, paths in groups)


def _subject_path(architecture: Architecture, subject: Subject) -> str:
    part = architecture.parts[subject.part]
    shown = docs_name(architecture, part)
    if not subject.sub:
        return shown
    below = shown.removesuffix("/") + "/" + "/".join(subject.sub)
    return below if is_file(architecture.layout, part.path + subject.sub) else below + "/"


def _untested(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    _tiers_of(architecture)
    return "\n\n".join(f"`{docs_name(architecture, part)}` gets no tier of its own: {part.untested.rstrip('.')}."
                     for part in architecture.parts.values() if part.untested)


def _tier_index(architecture: Architecture, section: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    return "\n".join(f"  - [[#{section}.{i} {tier.name}]]" for i, tier in enumerate(_tiers_of(architecture), 1))


def _tier_litmus(architecture: Architecture, section: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    return "\n\n".join(f"### {section}.{i} {tier.name}\n\n> [!TIP]\n> **Litmus test.** "
                        + " ".join(line.strip() for line in tier.litmus.splitlines())
                        for i, tier in enumerate(_tiers_of(architecture), 1))


def _tier_files(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    tiers = _tiers_needing(architecture, "one_file_per", "cases_from")
    rows = [f"| {tier.name} | {tier.one_file_per} | {tier.cases_from} |" for tier in tiers]
    return "\n".join(["| Tier | One file per | Its cases come from |", "|---|---|---|", *rows])


def _tier_data(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    rows = [f"| {tier.name} | {tier.data} |" for tier in _tiers_needing(architecture, "data")]
    return "\n".join(["| Tier | Where its data comes from |", "|---|---|", *rows])


def _tier_examples(architecture: Architecture, _: str, _q: Texts, tier_examples: Texts, in_fence: bool, file_types: FileTypes) -> str:
    tiers = [tier for tier in _tiers_of(architecture) if tier.example is not None]
    if not tiers:
        raise _Missing("no tier has an `example`")
    unread = [tier.name for tier in tiers if tier.name not in tier_examples]
    if unread:
        raise _Missing(f"the example of tier {_quoted(unread)} was not read")
    return _block([(f"{tier.name}: {'/'.join(tier.example.path)}{_aside(tier.example.note)}", tier.example.file,
                    tier_examples[tier.name]) for tier in tiers if tier.example is not None], in_fence,
                  architecture.language, file_types)


def _aside(note: str) -> str:
    return f" ({note})" if note else ""


def _tier_helpers(architecture: Architecture, _: str, _q: Texts, tier_examples: Texts, in_fence: bool, file_types: FileTypes) -> str:
    helpers = [helper for tier in _tiers_of(architecture) for helper in tier.helpers]
    if not helpers:
        raise _Missing("no tier has `helpers`")
    unread = [helper.file for helper in helpers if helper.file not in tier_examples]
    if unread:
        raise _Missing(f"the helper file {_quoted(unread)} was not read")
    return _block([(f"{'/'.join(helper.path)}{_aside(helper.note)}", helper.file, tier_examples[helper.file])
                   for helper in helpers], in_fence, architecture.language, file_types)


def _tiers_of(architecture: Architecture) -> tuple[Tier, ...]:
    if not architecture.tiers:
        raise _Missing("the architecture has no `tiers`")
    return architecture.tiers


def _tiers_needing(architecture: Architecture, *keys: str) -> tuple[Tier, ...]:
    tiers = _tiers_of(architecture)
    lacking = [f"tier '{tier.name}' has no `{key}`" for tier in tiers for key in keys if not getattr(tier, key)]
    if lacking:
        raise _Missing(", ".join(lacking))
    return tiers


def _suffix(file: str) -> str:
    name = file.rsplit("/", 1)[-1]
    return "." + name.rsplit(".", 1)[1] if "." in name else ""


def _entry_part(architecture: Architecture) -> Part:
    if architecture.entry is None:
        raise _Missing("no part is the entry point: set `docs.entry` to a part")
    return architecture.entry


def _part(architecture: Architecture, name: str) -> Part:
    if name not in architecture.parts:
        raise _Missing(f"the architecture defines no part '{name}'")
    return architecture.parts[name]


def _ticked(names: tuple[str, ...]) -> str:
    return ", ".join(f"`{name}`" for name in names)


def _and(items: list[str]) -> str:
    return _joined(items, "and")


def _or(items: list[str]) -> str:
    return _joined(items, "or")


def _joined(items: list[str], word: str) -> str:
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} {word} {items[-1]}"


def _quoted(names: list[str]) -> str:
    return ", ".join(f"'{n}'" for n in names)


def _guards(architecture: Architecture, _: str, _q: Texts, _t: Texts, _f: bool, _k: FileTypes) -> str:
    lines = [_structure_line(architecture),
             "`rules`: every import between parts is one that the `may_import` of the importing part allows "
             "(architecture.md, section 5)."]
    if architecture.libraries is not None:
        listed = "; ".join(f"`{docs_name(architecture, architecture.parts[name])}`: {_packages(packages)}"
                           for name, packages in architecture.libraries.items() if packages)
        reserved = "; ".join(f"`{name}`: {reason}" for name, reason in architecture.reserved.items())
        but = f" but what `reserved` names ({reserved})" if reserved else ""
        lines.append(f"`libraries`: a part imports only the outside packages listed for it ({listed}); the standard "
                     f"library is always allowed{but}, and tests are not checked.")
    if architecture.forbidden:
        lines.append(_forbidden_line(architecture))
    if architecture.tiers:
        fakes = ""
        if architecture.fakes is not None:
            parts = _and([f"`{docs_name(architecture, architecture.parts[p])}`" for p in architecture.fakes.stand_in_for])
            fakes = (f"; only a test whose tier tests {parts} imports the fakes in "
                     f"`{'/'.join((DEFAULT_TESTS, *architecture.fakes.folder))}/`")
        lines.append("`tiers`: a test lives in the folder that mirrors its subject in the app, and imports only that "
                     "part and what it may import (a test in a folder that mirrors no part, its tier's subject and "
                     f"what that may import){fakes}; it imports no other test file.")
        for tier in architecture.tiers:
            if tier.types_only:
                shown = _and([f"`{docs_name(architecture, architecture.parts[p])}`" for p in tier.types_only])
                lines.append(f"`types-only`: a {tier.name} test uses {shown} only as a type: it may import it and "
                             "annotate with it, and never calls it.")
        plain = [tier.name for tier in architecture.tiers if tier.plain_tables]
        if plain:
            lines.append(f"`plain tables`: no table test of the {_and(plain)} tests holds a branch in its body: no "
                         f"{_branches(architecture)}.")
    roots = [repeat.root for repeat in architecture.repeats]
    if roots:
        folders = _and([f"`{'/'.join((DEFAULT_TESTS, *root))}/`" for root in roots])
        lines.append(f"`test tree`: every folder below {folders} mirrors a folder of the app.")
        instances = _or([f"`{'/'.join(root)}/<name>/`" for root in roots])
        lines.append(f"`cycles`: no {instances} imports from another that imports, directly or through "
                     "others, from it; each cycle is reported once, with the imports that close it.")
    lines += [_must_import_line(architecture, part) for part in architecture.parts.values() if part.must_import]
    lines += [_tier_must_import_line(architecture, tier) for tier in architecture.tiers if tier.must_import]
    lines += _part_lines(architecture)
    lines += [_guard_line(architecture, guard) for guard in architecture.guards]
    return "\n".join(f"- {line}" for line in lines)


def _packages(packages: tuple[str, ...]) -> str:
    return "any outside package" if EVERYTHING in packages else ", ".join(packages)


def _forbidden_line(architecture: Architecture) -> str:
    """The parts that share a list are named together, in the order the file lists them."""
    groups: dict[tuple[tuple[str, ...], ...], list[str]] = {}
    for name, names in architecture.forbidden.items():
        groups.setdefault(names, []).append(f"`{docs_name(architecture, architecture.parts[name])}`")
    listed = "; ".join(f"{_and(parts)}: {_ticked(tuple('.'.join(n) for n in names))}" for names, parts in groups.items())
    tiers = [tier.name for tier in architecture.tiers if tier.forbidden]
    tests = f", and neither do the {_and(tiers)} tests of those parts" if tiers else ""
    methods = any(not entry[0] for names in groups for entry in names)
    seen = (", and a method written `.name()` called on anything but the object itself and what it holds;" if methods
            else ",")
    return (f"`forbidden`: a part neither imports nor uses by name what is listed for it ({listed}){tests}. It "
            f"catches what is written in the part's own files, through their imports and aliases{seen} not a name "
            "reached through a variable or `getattr`, nor I/O done on the part's behalf elsewhere.")


def _structure_line(architecture: Architecture) -> str:
    roots = [f"`{'/'.join(repeat.root)}/<name>/`" for repeat in architecture.repeats]
    every = f", in the app and in every {_and(roots)}" if roots else ""
    return f"`structure`: every folder and file of the layout exists{every}."


def _guard_line(architecture: Architecture, guard: Guard) -> str:
    match guard:
        case PackageOnly(parts):
            shown = _and([f"`{docs_name(architecture, architecture.parts[p])}`" for p in parts])
            return (f"`package-only`: {shown} {'is' if len(parts) == 1 else 'are'} imported as a package, never by "
                    "its files, from outside it.")
        case ScenarioCoverage(results, tier, suffix, columns, table, file):
            shown = ", ".join(f"`{c}`" for c in columns)
            return (f"`scenario-coverage`: every variant of a union named `<Name>{suffix}` in "
                    f"`{docs_name(architecture, architecture.parts[results])}` is the `{columns[-1]}` of a row of the "
                    f"table (columns {shown}) in `{file.replace(NAME, '<name>')}` among the {tier} tests (section 5.2), "
                    f"or is named by a standalone test of that file; every row is a `{'.'.join(table.row)}` with "
                    f"an `{table.id}`, and a table test has no {_branches(architecture)}.")
        case StandIns(mocks, _, spec, fixtures):
            built = f"{fixtures[0].name}.{fixtures[0].mocks[0]}" if fixtures else ""
            return _stand_ins_line(architecture, mocks[0][-1], spec[0], built)
        case NoDuplicates(least):
            return (f"`no-duplicates`: no two functions of the app have the same code, names and formatting aside, "
                    f"when each holds at least {least} statements; tests are not compared.")
        case DeadCode(untested, tests_only, known):
            fakes = architecture.fakes
            assert fakes is not None
            ports = _and([f"`{docs_name(architecture, architecture.parts[p])}`" for p in fakes.stand_in_for])
            reached = (" A file of a part with a tier that no test of that tier reaches, directly or through files of "
                       "parts of the same tier, is listed in the enforcement section, and fails `check --strict` "
                       "only." if untested else "")
            reached += (" A public class or function of the app that no other file of the app names, so that only the "
                        "tests use it, or nothing does, is listed in the enforcement section, and fails `check "
                        "--strict` only." if tests_only else "")
            if known:
                reached += (f" {_and([f'`{entry}`' for entry in known])} {'is' if len(known) == 1 else 'are'} accepted "
                            "as only the tests' (`guards.dead-code.known`) and named in the enforcement section instead; "
                            "an entry that no longer holds is listed.")
            interface = architecture.language.interface_name
            return (f"`dead-code`: every `{interface}` in {ports} is named by another file of the app, and every fake in "
                    f"`{'/'.join((DEFAULT_TESTS, *fakes.folder))}/` by a test; the wiring and re-exports do not "
                    f"count.{reached}")
        case PrivateImports():
            return ("`private-imports`: no file of the app or its tests imports a name that starts with "
                    f"`{architecture.language.checked.private}` from another file of them.")
        case NoTwins(least, renamed, subset, translated):
            copies = [said for minimum, said in (
                (renamed, f"renames some of its fields (from {renamed} fields: more than half of its names kept in "
                          "place, and each renamed field's type)"),
                (subset, f"keeps at least half of its fields in its order (from {subset} fields)")) if minimum]
            also = f" Nor is one a copy of another that {', or that '.join(copies)}." if copies else ""
            excused = (" A pair is no twin when a file of "
                       f"{_or([f'`{docs_name(architecture, architecture.parts[p])}`' for p in translated])} "
                       "builds one of the two through an import, imports the other, and holds one function that names "
                       "both: a translation, which every check names in its enforcement section." if translated else "")
            return (f"`no-twins`: no two public classes in parts of different names declare the same fields in the "
                    f"same order, when each declares at least {least}; types and defaults aside, tests not read."
                    f"{also}{excused}")
        case PassThrough(parts):
            shown = _and([f"`{docs_name(architecture, architecture.parts[p])}`" for p in parts])
            return (f"`pass-through`: a method of {shown} whose whole body forwards to one call on a collaborator, or "
                    "returns an attribute of what that call answers, is listed in the enforcement section, and fails "
                    "`check --strict` only.")
        case ClosedTree():
            language = architecture.language
            return (f"`closed-tree`: every {language.checked.title} file of the app lies in a part, or is the package file "
                    f"(`{language.checked.package_file}`) of a folder of the layout.")
        case _:
            comment = architecture.language.checked.comment
            directives = ", ".join(f"`{comment} {word}`" for word in architecture.language.checked.directives)
            return (f"`no-comments`: no `{comment}` comments in the app or its tests; docstrings and tool directives "
                    f"({directives}) stay.")


def _tier_must_import_line(architecture: Architecture, tier: Tier) -> str:
    wanted = _or([f"`{docs_name(architecture, architecture.parts[p])}`" for p in tier.must_import])
    return (f"`must-import`: every {tier.name} test imports from {wanted}, directly or through test code that is no "
            "test file.")


def _part_lines(architecture: Architecture) -> list[str]:
    """One line per check a part's own keys switch on, the parts that share a value named together."""
    def shown(names: list[str]) -> str:
        return _and([f"`{docs_name(architecture, architecture.parts[n])}`" for n in names])

    parts = list(architecture.parts.values())
    lines: list[str] = []
    for part in parts:
        if part.types_only:
            lines.append(f"`types-only`: {shown([part.name])} uses {shown(list(part.types_only))} only as a type: it "
                         "imports it to annotate and never calls it.")
    holds = {kind: [p.name for p in parts if p.holds == kind] for kind in ("classes", "functions")}
    if any(holds.values()):
        said = []
        if holds["classes"]:
            said.append(f"a file of {shown(holds['classes'])} defines classes, never a public function at the top level")
        if holds["functions"]:
            said.append(f"a file of {shown(holds['functions'])} defines functions, never a class (a private one too) but "
                        "exceptions and the records its functions return")
        lines.append(f"`holds`: {'; '.join(said)}; listed in the enforcement section, and fails `check --strict` "
                     "only.")
    immutable = [p.name for p in parts if p.immutable]
    if immutable:
        lines.append(f"`immutable`: every class of {shown(immutable)} is an immutable record, as the "
                     f"{architecture.language.checked.title} data file marks one, or an exception; listed in the "
                     "enforcement section, and fails `check --strict` only.")
    callbacks = [p.name for p in parts if p.no_callbacks]
    if callbacks:
        lines.append(f"`no-callbacks`: no function of {shown(callbacks)} calls a parameter annotated as a callable: it "
                     "is handed values, never a way to fetch them.")
    for part in parts:
        if part.names:
            lines.append(f"`names`: every class of {shown([part.name])} is named "
                         f"{_or([f'`{n}`' for n in part.names])}.")
    for part in parts:
        if part.shared is not None:
            lines.append(f"`shared`: every public name of {shown([part.name])} is used by at least {part.shared} users "
                         "(each instance of a repeating folder, or each part outside them; tests not read), or it "
                         "belongs to the one that uses it.")
    for part in parts:
        if part.built_by:
            lines.append(f"`built-by`: only code of {shown(list(part.built_by))} builds a class of "
                         f"{shown([part.name])}; tests are not read.")
    return lines


def _must_import_line(architecture: Architecture, part: Part) -> str:
    wanted = may_import(part.must_import, _folders(architecture), architecture.words()).replace(" and ", " or ")
    return (f"`must-import`: every file of `{docs_name(architecture, part)}` imports from {wanted}, or an outside "
            "package, or reaches one through a file of its own part; a package file and a file with no code of its own "
            "are exempt.")


def _branches(architecture: Architecture) -> str:
    """What a branch is, in the language of the app: a statement that opens one, or an expression that chooses."""
    checked = architecture.language.checked
    said = [f"{_or([f'`{word}`' for word in checked.branching])} statement"] if checked.branching else []
    said += [f"{_or([f'`{word}`' for word in checked.branching_expressions])} expression"] \
        if checked.branching_expressions else []
    return " and no ".join(said) or "branch"


def _stand_ins_line(architecture: Architecture, mock: str, spec: str, built: str = "") -> str:
    fakes = architecture.fakes
    assert fakes is not None
    parts = _and([f"`{docs_name(architecture, architecture.parts[p])}`" for p in fakes.stand_in_for])
    tiers = _and([t.name for t in architecture.tiers if any(s.part in fakes.stand_in_for for s in t.subject)])
    fixture = f" (or, from a fixture, `{built}({spec}=<Port>)`)" if built else ""
    mocks = (f"; and every mock in the {tiers} tests names what it stands in for, `{mock}({spec}=<Port>)`{fixture}, "
             "never a read port") if tiers else ""
    interface = architecture.language.interface_name
    return (f"`stand-ins`: every `{interface}` in {parts} is fire-only (every method returns "
            f"`{architecture.language.checked.nothing}`) or read (any method returns a value), each method annotated; every "
            f"read port `<Port>` has a fake `{fakes.prefix}<Port>` in `{'/'.join((DEFAULT_TESTS, *fakes.folder))}/`{mocks} "
            "(section 6).")


_RENDERERS: dict[str, Callable[[Architecture, str, Texts, Texts, bool, FileTypes], str]] = {
    "tree": _tree, "rules_table": _rules_table, "layers": _layers, "placement": _placement, "litmus": _litmus,
    "naming": _naming, "entry": _entry, "docs_tree": _docs_tree, "example": _example, "tiers": _tiers,
    "untested": _untested, "tier_litmus": _tier_litmus, "tier_files": _tier_files, "tier_helpers": _tier_helpers,
    "tier_index": _tier_index, "tier_data": _tier_data, "tier_examples": _tier_examples,
    "guards": _guards,
}
_WITH_ARGUMENT = {"layers", "litmus", "example", "tier_index", "tier_litmus"}
_ARGUMENT = {"litmus": "<part>", "example": "<path>, ...", "tier_index": "<section>", "tier_litmus": "<section>"}
_KNOWN = [f"{{{{{name}:{_ARGUMENT.get(name, '<name>')}}}}}" if name in _WITH_ARGUMENT
          else f"{{{{{name}}}}}" for name in _RENDERERS]
