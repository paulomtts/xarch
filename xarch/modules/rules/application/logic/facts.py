"""The facts of a run, read once from the parsed files: where each file sits (placement, worked out once per file), and
what it says, by kind, each fact as a rule reads it (see Fact). A file that does not parse says only its error, and
a file of the app no part and no folder of the layout governs, which is not read, only that it is there.

    error     how a file fails to parse: the line, text the parser's message
    file      the file as a whole, at line 0
    import    each import as written: the module it names (path), relative, standard
    imported  each name an import takes, path the module and the name (the module alone for an import of a whole
              module), the name it takes (None for a whole module); its traits are the import's
    use       each name read, path the dotted path it reaches, bound how many steps the binding import bound
    method    each call of an attribute no import binds, name the attribute; held when it is on the object a method is
              called on
    call      each call whose callee an import binds, path the callee; at where the callee sits when it is the app's
    edge      each import into the app's own package, the target the file or package it reaches below the root and
              at where that sits (None when no part and no folder of the layout governs it), name the name it takes
              when that is no file; a test's relative imports are its own and none is an edge
    suite_edge each import of a test file into the tests' own package, the target it reaches below the tests root
    comment   each line comment, text as written
    class     each class defined at the top level, name its name; exception and record when it is one (below)
    function  each function defined at the top level or in a class of the top level, name its name, path its class
              and its name; top-level when it is in no class
    callback  each call of a function's own parameter by its bare name, path the function, name the parameter;
              receiver when the parameter is the first of a method, annotated when its annotation says it is a callable

and the facts derived from them over the whole app:

    build     a call of a class the app defines at the top level of a file, read through the import that binds the
              callee: path the callee, at where the class's file sits
    reference a use that reaches a function the app defines at the top level of a file (the first prefix, from the
              one its import bound, whose last name the file binds to a function alone): target that function below
              the root, at where its file sits
    exception a class that derives from one of the language's builtin exceptions, as the reader says, or from a
              class of the app that is an exception, however far that goes (a base read through the absolute import
              that binds it)
    record    a class with no method but the language's special methods that a top-level function of its file names
              in its return annotation
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import replace

from xarch.kernel.logic.placement import Place
from xarch.modules.rules.application.logic.filters import in_scope
from xarch.modules.rules.application.logic.imports import dotted, named_targets, targets
from xarch.modules.rules.application.logic.places import place
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.rule import Defined, Fact, Facts, Read, Rule
from xarch.modules.rules.domain.values import Class, Profile, SourceFile

Placements = dict[tuple[str, ...], Place | None]
"""Where each path below the root placed so far sits."""

KINDS = ("error", "file", "import", "imported", "use", "method", "call", "build", "reference", "edge", "suite_edge",
         "comment", "class", "function", "callback")
"""Every kind of fact, in the order a file's facts are worked out."""

_TRAITS = {(relative, standard, held): frozenset(name for name, on in (("relative", relative), ("standard", standard),
                                                                       ("held", held)) if on)
           for relative in (False, True) for standard in (False, True) for held in (False, True)}
"""The traits of a fact, by whether it is relative, of the standard library and held."""
_TOP = frozenset({"top-level"})


def facts_of(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
             tests_root: str = "", rules: Iterable[Rule] | None = None, unread: Iterable[SourceFile] = ()) -> Facts:
    """The facts of the app's files, below the root package root, then of the files of the app that are not read
    (unread), then of the test files, below the package tests_root: every kind of each file, or (rules given) the
    kinds the rules whose scope holds the file read."""
    marks = profile.language.marks
    app, tests = [(f, *dotted(f.path, marks)) for f in app], [(f, *dotted(f.path, marks)) for f in tests]
    known = frozenset(steps for f, steps, _ in app if f.error is None)
    known_tests = frozenset(steps for f, steps, _ in tests if f.error is None)
    cache: Placements = {}
    parsed = [(f, steps) for f, steps, _ in app if f.error is None]
    defined = Defined(root, {(root, *steps, c.name): _placed(profile, cache, steps) for f, steps in parsed
                             for c in f.classes},
                      {steps: frozenset(f.module_functions) for f, steps in parsed},
                      frozenset(exceptions(parsed, root)))
    placed = [Read(file, steps, package, False, _placed(profile, cache, steps)) for file, steps, package in app]
    placed += [Read(file, steps, package, False) for file, steps, package in
               ((f, *dotted(f.path, marks)) for f in unread)]
    placed += [_tested(file, steps, package, profile) for file, steps, package in tests]
    bare = Facts((), root, tests_root, known, known_tests,
                 frozenset(r.steps for r in placed if r.test and r.is_test and r.file.error is None))
    rules = tuple(rules) if rules is not None else None
    read = tuple(replace(r, facts={kind: _facts(kind, r, profile, cache, defined, bare)
                                   for kind in (KINDS if rules is None else _read(r, rules, bare, profile))})
                 for r in placed)
    return replace(bare, files=read)


def _tested(file: SourceFile, steps: tuple[str, ...], package: bool, profile: Profile) -> Read:
    where = tested(profile, file.path)
    return Read(file, steps, package, True, None, where.tier.name if where.tier is not None else "", where.instance,
                where.own, where.parts, where.is_test, where.is_fake)


def _read(read: Read, rules: tuple[Rule, ...], facts: Facts, profile: Profile) -> tuple[str, ...]:
    """The kinds of fact the rules whose scope holds the file read, a call for those that excuse a reference read as
    the callee of a call."""
    kinds = [kind for rule in rules if in_scope(rule.scope, read, facts, profile)
             for kind in (*rule.facts, *(("call",) if "called" in rule.exempt else ()))]
    return tuple(dict.fromkeys(kinds))


def _facts(kind: str, read: Read, profile: Profile, cache: Placements, defined: Defined,
           facts: Facts) -> tuple[Fact, ...]:
    file, root = read.file, defined.root
    package = read.steps if read.package else read.steps[:-1]
    if file.error is not None:
        return (Fact("error", file.error.line, text=file.error.message),) if kind == "error" else ()
    match kind:
        case "error":
            return ()
        case "file":
            return (Fact("file", 0),)
        case "comment":
            return tuple(Fact("comment", c.line, text=c.text) for c in file.comments)
        case "class":
            return tuple(Fact("class", c.line, (c.name,), c.name, _class(c, file, read, profile, defined))
                         for c in file.classes)
        case "function":
            return tuple(Fact("function", f.line, (f.owner, f.name) if f.owner else (f.name,), f.name,
                              _TOP if not f.owner else frozenset()) for f in file.functions)
        case "callback":
            return tuple(Fact("callback", c.line, (c.function,), c.parameter,
                              frozenset(n for n, on in (("receiver", c.receiver), ("annotated", c.annotated)) if on))
                         for c in file.callbacks)
        case "import":
            return tuple(Fact("import", i.line, i.module, traits=_TRAITS[i.relative, i.standard, False],
                              text=i.written) for i in file.imports)
        case "imported":
            return tuple(_imported(file))
        case "use":
            return tuple(Fact("use", u.line, u.name, bound=u.bound) for u in file.uses)
        case "method":
            return tuple(Fact("method", m.line, name=m.name, traits=_TRAITS[False, False, m.held])
                         for m in file.method_calls)
        case "call":
            return tuple(Fact("call", c.line, c.func,
                              at=_placed(profile, cache, c.func[1:]) if c.func[:1] == (root,) else None)
                         for c in file.calls)
        case "build":
            return tuple(Fact("build", c.line, c.func, at=defined.classes[c.func]) for c in file.calls
                         if c.func in defined.classes)
        case "reference":
            return tuple(_references(file, profile, cache, defined))
        case "edge" if read.test:
            return tuple(Fact("edge", line, target=target, at=_placed(profile, cache, target)) for line, target in
                         targets((i for i in file.imports if not i.relative), (), facts.known, root))
        case "edge":
            return tuple(Fact("edge", line, name=name, target=target, at=_placed(profile, cache, target))
                         for line, target, name in named_targets(file.imports, package, facts.known, root))
        case "suite_edge":
            return tuple(Fact("suite_edge", line, target=target) for line, target in
                         targets(file.imports, package, facts.known_tests, facts.tests_root)) if read.test else ()
    raise ValueError(f"no kind of fact is named {kind!r}")


def _references(file: SourceFile, profile: Profile, cache: Placements, defined: Defined) -> Iterator[Fact]:
    for use in file.uses:
        if use.name[:1] != (defined.root,):
            continue
        for end in range(max(use.bound, 2), len(use.name) + 1):
            module, function = use.name[1:end - 1], use.name[end - 1]
            if function in defined.functions.get(module, ()):
                yield Fact("reference", use.line, use.name, target=(*module, function),
                           at=_placed(profile, cache, module))
                break


def _placed(profile: Profile, cache: Placements, path: tuple[str, ...]) -> Place | None:
    """Where a path below the root sits, worked out once a run."""
    if path not in cache:
        cache[path] = place(profile, path)
    return cache[path]


def _class(cls: Class, file: SourceFile, read: Read, profile: Profile, defined: Defined) -> frozenset[str]:
    exception = (read.steps, cls.name) in defined.exceptions and not read.test
    record = all(profile.language.is_special(m.name) for m in cls.methods) and any(
        cls.name in f.returns_named for f in file.functions if not f.owner)
    return frozenset(n for n, on in (("exception", exception), ("record", record)) if on)


def exceptions(files: Iterable[tuple[SourceFile, tuple[str, ...]]], root: str) -> set[tuple[tuple[str, ...], str]]:
    """Every class of the files, each with its steps below the root, that is an exception, as (its file's steps, its
    name)."""
    classes = {(steps, c.name): c for f, steps in files for c in f.classes}
    found = {key for key, cls in classes.items() if cls.exception}
    grown = True
    while grown:
        grown = False
        for key, cls in classes.items():
            if key not in found and any(base is not None and base[:1] == (root,)
                                        and (base[1:-1], base[-1]) in found for base in cls.bases):
                found.add(key)
                grown = True
    return found


def _imported(file: SourceFile) -> Iterator[Fact]:
    for i in file.imports:
        traits = _TRAITS[i.relative, i.standard, False]
        if i.names is None:
            yield Fact("imported", i.line, i.module, traits=traits, text=i.written)
        else:
            yield from (Fact("imported", i.line, (*i.module, name), name, traits, text=i.written) for name in i.names)
