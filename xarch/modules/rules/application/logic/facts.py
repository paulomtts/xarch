"""The facts of a run, read once from the parsed files: where each file sits (placement, worked out once per file), and
what it says, by kind, each fact as a rule reads it (see Fact, and the kinds of the vocabulary). A file that does not
parse says only its error, and a file of the app no part and no folder of the layout governs, which is not read, only
that it is there.

A dotted name starts at a namespace: the app's own code at the app's root package, the tests' at theirs; a reader
turns its language's imports and names into such paths, and a fact into the app or the tests is read below that root.

    syntax-error        how a file fails to parse: the line, text the parser's message; trait unreadable when it
                        could not be read as text at all, text then saying why
    file                the file as a whole, at line 0; traits no-statements when no function or method of it holds
                        a real statement, exceptions-only when it defines classes, every one an exception (below), and no
                        top-level function; lines how many lines it holds
    names-mentioned     every name the file mentions, annotations included, by its last step alone
    import              each import as written: the module it names (path), relative, standard, type-only
    imported-name       each name an import takes, path the module and the name (the module alone for an import of
                        a whole module), the name it takes (None for a whole module); its traits are the import's,
                        and public when the reader says the name it takes is public
    use                 each name read, path the dotted path it reaches, bound how many steps the binding import bound
    method-call         each call of an attribute no import binds, name the attribute; on-own-object when it is
                        on the object a method is called on
    call                each call whose callee an import binds, path the callee and name its last step; at where the
                        callee sits when it is the app's
    import-into-app     each import into the app's own package, the target the file or package it reaches below the
                        root and at where that sits (None when no part and no folder of the layout governs it), name
                        the name it takes when that is no file; a test's relative imports are its own and none is one,
                        but a test beside the code reads them from its own package in the app; type-only when the
                        import is made only for the type checker
    import-to-definition
                        each import as import-into-app reads it, but a name taken from a package file that passes it
                        on (takes it by an import of its own) read where it is defined: through each package file
                        that passes it on in turn, each once, the file it is then, or the module that takes it by no
                        import, with the name it has there
    import-into-tests   each import of a test file into the tests' own package, the target it reaches below the tests
                        root
    comment             each comment, text as written, name the marker it opens with; doc when it is a doc comment
    class               each class defined at the top level, name its name, names those its bases and body mention;
                        exception, record, interface and immutable when it is one (below); public when the reader
                        says it is public; bases every class it derives from, however far (below)
    function            each function defined at the top level or in a class of the top level, name its name, path
                        its class and its name; top-level when it is in no class; public when the reader says it is
                        public; forwards when it is a method the reader says only forwards, text the callee it
                        forwards to and target the attributes it returns of the call's result
    callback            each call of a function's own parameter by its bare name, path the function, name the
                        parameter; receiver when the parameter is the first of a method, annotated-callable when its
                        annotation says it is a callable

and the facts derived from them over the whole app:

    construction        a call of a class the app defines at the top level of a file, read through the import that
                        binds the callee: path the callee, name the class, at where the class's file sits; exception
                        and record when the class it builds is one (below)
    function-reference  a use that reaches a function the app defines at the top level of a file (the first prefix,
                        from the one its import bound, whose last name the file binds to a function alone), other than
                        the callee of a call on its line, once for each such call: target that function below the
                        root, at where its file sits
    exception           a class that derives from one of the language's builtin exceptions, as the reader says, or from
                        a class of the app that is an exception, however far that goes (a base read through the
                        import that binds it)
    record              a class the language's reader says is a record
    interface           a class the reader says is an interface, by the marks of the language's data file, the last
                        of its name in its file
    immutable           a class the reader says is an immutable record, by the marks of the language's data file
    bases               of a class, each base it names: where the import that binds it leads, the class of its own
                        file it names, else the name it is written with alone; then, for each base that is a class of
                        the app or of the tests defined at the top level of a file, that class's bases, however far,
                        each once (a class never derives from itself)
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import replace

from xarch.kernel.logic.source import imported_names
from xarch.kernel.placement import Place
from xarch.kernel.source import Import
from xarch.modules.rules.application.logic.filters import in_scope
from xarch.modules.rules.application.logic.imports import dotted, named_targets, targets
from xarch.modules.rules.application.logic.places import place
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.parsed import Class, Function, SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.rule import AT_LEAST, FILE_REACH, Defined, Fact, Facts, Read, Rule
from xarch.modules.rules.domain.vocabulary import KINDS as VOCABULARY
from xarch.profile_values.checks import Scope

Placements = tuple[dict[tuple[str, ...], Place | None], frozenset[tuple[str, ...]]]
"""Where each path below the root placed so far sits, and the paths of the app's files that are no package file, none
of which is an instance of a repeating folder."""

KINDS = tuple(kind.name for kind in VOCABULARY)
"""Every kind of fact, in the order a file's facts are worked out."""

_TRAITS = {(relative, standard, held): frozenset(name for name, on in (("relative", relative), ("standard", standard),
                                                                       ("on-own-object", held)) if on)
           for relative in (False, True) for standard in (False, True) for held in (False, True)}
"""The traits of a fact, by whether it is relative, of the standard library and held."""
_TOP = frozenset({"top-level"})
_RECEIVER, _ANNOTATED = "receiver", "annotated-callable"
_FORWARDS = frozenset({"forwards"})
_DOC = frozenset({"doc"})
_PUBLIC = frozenset({"public"})
_TYPE_ONLY = frozenset({"type-only"})


def facts_of(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
             tests_root: str = "", rules: Iterable[Rule] | None = None, unread: Iterable[SourceFile] = ()) -> Facts:
    """The facts of the app's files, below the root package root, then of the files of the app that are not read
    (unread), then of the test files, below the package tests_root, a test beside the code below root: every kind of
    each file, or (rules given) the kinds the rules whose scope holds the file read."""
    marks = profile.language.marks
    app, tests = [(f, *dotted(f.path, marks)) for f in app], [(f, *dotted(f.path, marks)) for f in tests]
    known = frozenset(steps for f, steps, _ in app if f.error is None)
    known_tests = frozenset(steps for f, steps, _ in tests if f.error is None)
    near = frozenset(steps for f, steps, _ in tests if f.beside and f.error is None)
    cache: Placements = ({}, frozenset(steps for f, steps, package in app if not package))
    parsed = [(f, steps) for f, steps, _ in app if f.error is None]
    defined = Defined(root, {(root, *steps, c.name): _placed(profile, cache, steps) for f, steps in parsed
                             for c in f.classes},
                      {steps: frozenset(f.module_functions) for f, steps in parsed},
                      frozenset(_exceptions(parsed, root)),
                      frozenset((root, *steps, c.name) for f, steps in parsed for c in f.classes if c.record),
                      _bases([*((f, steps, root) for f, steps in parsed),
                              *((f, steps, root if f.beside else tests_root) for f, steps, _ in tests
                                if f.error is None)]),
                      _passed(app, root))
    covered = {s.part: tier.name for tier in reversed(profile.tiers) for s in tier.subject}
    placed = [_covered(Read(file, steps, package, False, _placed(profile, cache, steps)), covered)
              for file, steps, package in app]
    placed += [Read(file, steps, package, False, _placed(profile, cache, steps)) for file, steps, package in
               ((f, *dotted(f.path, marks)) for f in unread)]
    placed += [_tested(file, steps, package, profile) for file, steps, package in tests]
    bare = Facts((), root, tests_root, known, known_tests,
                 frozenset(r.steps for r in placed if r.in_tests and r.is_test and r.file.error is None),
                 {r.steps: r.tier for r in placed if not r.in_tests and r.tier and r.file.error is None}, near)
    rules = tuple(rules) if rules is not None else None
    read = tuple(replace(r, facts={kind: _facts(kind, r, profile, cache, defined, bare)
                                   for kind in (KINDS if rules is None else _read(r, rules, bare, profile))})
                 for r in placed)
    return replace(bare, files=read)


def _covered(read: Read, covered: dict[str, str]) -> Read:
    """The file with the tier whose tests cover its part, the first that does."""
    part = read.place.part if read.place is not None else None
    return replace(read, tier=covered.get(part, "")) if part is not None else read


def _tested(file: SourceFile, steps: tuple[str, ...], package: bool, profile: Profile) -> Read:
    where = tested(profile, file.path, file.beside)
    return Read(file, steps, package, True, None, where.tier.name if where.tier is not None else "", where.instance,
                where.own, where.parts, where.is_test, where.is_fake)


def _read(read: Read, rules: tuple[Rule, ...], facts: Facts, profile: Profile) -> tuple[str, ...]:
    """The kinds of fact the rules read of the file: those whose scope holds it read their kinds, their links and their
    spread; a rule of reach reads the kinds and the links of every file on its scope's side (see reach_scopes), and
    the links of its roots; and a rule that a file must reach reads the file of each file of its scope, which it
    says."""
    kinds: list[str] = []
    for rule in rules:
        if in_scope(rule.scope, read, facts, profile):
            kinds += [*rule.facts, *rule.spread, *rule.links,
                      *(("file",) if rule.quantifier in (*FILE_REACH, AT_LEAST) else ())]
        side, roots = reach_scopes(rule)
        if side is not None and in_scope(side, read, facts, profile):
            kinds += [*rule.facts, *rule.links]
        if roots is not None and in_scope(roots, read, facts, profile):
            kinds += rule.links
    return tuple(dict.fromkeys(kinds))


def reach_scopes(rule: Rule) -> tuple[Scope | None, Scope | None]:
    """The files a rule of reach reads besides its scope: for MUST_REACH and MUST_NOT_REACH, every file of its scope's
    side, whose facts
    may match a target or lead to one; for MUST_BE_REACHED, its roots. None where the rule has none."""
    return (Scope(rule.scope.files) if rule.quantifier in FILE_REACH else None), rule.roots


def _facts(kind: str, read: Read, profile: Profile, cache: Placements, defined: Defined,
           facts: Facts) -> tuple[Fact, ...]:
    file, root = read.file, defined.root
    package = read.steps if read.package else read.steps[:-1]
    if file.error is not None:
        unreadable = frozenset({"unreadable"} if file.error.unreadable else ())
        return (Fact("syntax-error", file.error.line, text=file.error.message, traits=unreadable),) \
            if kind == "syntax-error" else ()
    match kind:
        case "syntax-error":
            return ()
        case "file":
            return (Fact("file", 0, traits=_file(file, read, defined), lines=file.lines),)
        case "names-mentioned":
            return (Fact("names-mentioned", 0, names=file.named),)
        case "comment":
            return tuple(Fact("comment", c.line, name=c.marker or None, traits=_DOC if c.doc else frozenset(),
                              text=c.text) for c in file.comments)
        case "class":
            ports = {c.name: c for c in file.classes if c.interface}
            side = root if not read.in_tests or file.beside else facts.tests_root
            return tuple(Fact("class", c.line, (c.name,), c.name, _class(c, read, defined, ports),
                              names=c.named, bases=_lineage((side, *read.steps, c.name), defined.bases))
                         for c in file.classes)
        case "function":
            return tuple(_function(f) for f in file.functions)
        case "callback":
            return tuple(Fact("callback", c.line, (c.function,), c.parameter,
                              frozenset(n for n, on in ((_RECEIVER, c.receiver), (_ANNOTATED, c.annotated)) if on),
                              function=c.function)
                         for c in file.callbacks)
        case "import":
            return tuple(Fact("import", i.line, i.module, traits=_TRAITS[i.relative, i.standard, False]
                              | (_TYPE_ONLY if i.type_only else frozenset()),
                              text=i.written) for i in file.imports)
        case "imported-name":
            return tuple(_imported(file))
        case "use":
            return tuple(Fact("use", u.line, u.name, bound=u.bound) for u in file.uses)
        case "method-call":
            return tuple(Fact("method-call", m.line, name=m.name, traits=_TRAITS[False, False, m.held],
                              arguments=m.passed, literals=m.literals, function=m.function)
                         for m in file.method_calls)
        case "call":
            return tuple(Fact("call", c.line, c.func, c.func[-1],
                              at=_placed(profile, cache, c.func[1:]) if c.func[:1] == (root,) else None,
                              arguments=c.passed, literals=c.literals, function=c.function)
                         for c in file.calls)
        case "construction":
            return tuple(Fact("construction", c.line, c.func, c.func[-1], _built(c.func, defined),
                              at=defined.classes[c.func], arguments=c.passed, literals=c.literals,
                              function=c.function)
                         for c in file.calls if c.func in defined.classes)
        case "function-reference":
            return tuple(_references(file, profile, cache, defined))
        case "import-into-app" if read.in_tests:
            return tuple(Fact("import-into-app", line, target=target, at=_placed(profile, cache, target),
                              traits=_TYPE_ONLY if i.type_only else frozenset())
                         for i in (file.imports if file.beside else tuple(i for i in file.imports if not i.relative))
                         for line, target in targets((i,), package if file.beside else (),
                                                     facts.known | facts.beside, root)
                         if target not in facts.beside)
        case "import-into-app":
            return tuple(Fact("import-into-app", line, name=name, target=target, at=_placed(profile, cache, target),
                              traits=_TYPE_ONLY if i.type_only else frozenset())
                         for i in file.imports for line, target, name in named_targets((i,), package, facts.known, root))
        case "import-to-definition" if read.in_tests:
            return tuple(Fact("import-to-definition", line, target=target, at=_placed(profile, cache, target),
                              traits=_TYPE_ONLY if i.type_only else frozenset())
                         for i in (file.imports if file.beside else tuple(i for i in file.imports if not i.relative))
                         for line, target in _defined(i, package if file.beside else (), facts.known | facts.beside,
                                                      defined)
                         if target not in facts.beside)
        case "import-to-definition":
            return tuple(Fact("import-to-definition", line, name=name, target=target,
                              at=_placed(profile, cache, target), traits=_TYPE_ONLY if i.type_only else frozenset())
                         for i in file.imports
                         for line, target, name in _named_definitions(i, package, facts.known, defined))
        case "import-into-tests":
            return tuple(Fact("import-into-tests", line, target=target)
                         for line, target in _into_tests(read, package, facts)) if read.in_tests else ()
    raise ValueError(f"no kind of fact is named {kind!r}")


def _passed(app: Iterable[tuple[SourceFile, tuple[str, ...], bool]],
            root: str) -> dict[tuple[str, ...], dict[str, tuple[tuple[str, ...], str]]]:
    """The names each package file of the app passes on, by its steps below the root: each name a from-import of the
    app it makes binds (under the name it takes, or another), with the module below the root it takes it from and the
    name it takes there; an import of every name a module makes public passes on nothing this reads."""
    found: dict[tuple[str, ...], dict[str, tuple[tuple[str, ...], str]]] = {}
    for file, steps, package in app:
        if not package or file.error is not None:
            continue
        passed: dict[str, tuple[tuple[str, ...], str]] = {}
        for i in file.imports:
            if i.names is None or i.every:
                continue
            bound = dict(i.aliases)
            for base, name in imported_names(i, steps, root):
                if name is not None:
                    passed.setdefault(bound.get(name, name), (base, name))
        found[steps] = passed
    return found


def _named_definitions(i: Import, package: tuple[str, ...], known: frozenset[tuple[str, ...]],
                       defined: Defined) -> Iterator[tuple[int, tuple[str, ...], str | None]]:
    """What named_targets yields of the import, each name taken from a package file that passes it on followed to
    where it is defined: through each package file that takes it in turn, each once, to the file it is then a file of,
    or to the module that takes it by no import, with the name it has there."""
    for line, target, name in named_targets((i,), package, known, defined.root):
        seen: set[tuple[tuple[str, ...], str]] = set()
        while name is not None and name in defined.passed.get(target, {}) and (target, name) not in seen:
            seen.add((target, name))
            target, name = defined.passed[target][name]
            if target + (name,) in known:
                target, name = target + (name,), None
        yield line, target, name


def _defined(i: Import, package: tuple[str, ...], known: frozenset[tuple[str, ...]],
             defined: Defined) -> Iterator[tuple[int, tuple[str, ...]]]:
    """What _named_definitions yields, without the names."""
    for line, target, _ in _named_definitions(i, package, known, defined):
        yield line, target


def _into_tests(read: Read, package: tuple[str, ...], facts: Facts) -> list[tuple[int, tuple[str, ...]]]:
    """What a test's imports reach of the test code: for a test below the tests root, what they reach below it, its
    relative imports read from its own package; for a test beside the code, what its absolute imports reach below the
    tests root (the fakes, which its tier may import only when it tests a part they stand in for, and any other test
    code, which it may not import from outside its own folder); then, for any test, the tests beside the code they
    reach, read below the app's root, a relative import read from its own package only for a test beside the code."""
    imports = read.file.imports
    beside = read.file.beside
    own = list(targets(tuple(i for i in imports if not i.relative) if beside else imports, () if beside else package,
                       facts.known_tests, facts.tests_root))
    near = imports if beside else tuple(i for i in imports if not i.relative)
    return [*own, *((line, target) for line, target in targets(near, package, facts.beside, facts.root)
                    if target in facts.beside)]


def _references(file: SourceFile, profile: Profile, cache: Placements, defined: Defined) -> Iterator[Fact]:
    """The uses that reach a function the app defines, but the callee of a call on its line, once for each call."""
    calls = Counter((call.line, call.func) for call in file.calls)
    for use in file.uses:
        if use.name[:1] != (defined.root,):
            continue
        for end in range(max(use.bound, 2), len(use.name) + 1):
            module, function = use.name[1:end - 1], use.name[end - 1]
            if function in defined.functions.get(module, ()):
                if calls[(use.line, use.name)] > 0:
                    calls[(use.line, use.name)] -= 1
                else:
                    yield Fact("function-reference", use.line, use.name, target=(*module, function),
                               at=_placed(profile, cache, module))
                break


def _placed(profile: Profile, cache: Placements, path: tuple[str, ...]) -> Place | None:
    """Where a path below the root sits, worked out once a run."""
    found, files = cache
    if path not in found:
        found[path] = place(profile, path, files)
    return found[path]


def _class(cls: Class, read: Read, defined: Defined, ports: dict[str, Class]) -> frozenset[str]:
    exception = (read.steps, cls.name) in defined.exceptions and not read.in_tests
    return frozenset(n for n, on in (("exception", exception), ("record", cls.record),
                                     ("interface", ports.get(cls.name) is cls), ("immutable", cls.immutable),
                                     ("public", cls.public)) if on)


def _built(func: tuple[str, ...], defined: Defined) -> frozenset[str]:
    """Of the traits a class has, those of the class a construction builds, by its dotted path: an exception, a
    record."""
    return frozenset(n for n, on in (("exception", (func[1:-1], func[-1]) in defined.exceptions),
                                     ("record", func in defined.records)) if on)


def _function(function: Function) -> Fact:
    path = (function.owner, function.name) if function.owner else (function.name,)
    public = _PUBLIC if function.public else frozenset()
    signature = {"parameters": tuple((p.name, p.annotation, p.default) for p in function.parameters),
                 "returns": function.returns}
    if not function.owner:
        return Fact("function", function.line, path, function.name, _TOP | public, **signature)
    if not function.forwards or function.sole_call is None:
        return Fact("function", function.line, path, function.name, public, **signature)
    return Fact("function", function.line, path, function.name, _FORWARDS | public, target=function.sole_call.then,
                text=function.forwards, **signature)


def _file(file: SourceFile, read: Read, defined: Defined) -> frozenset[str]:
    code = any(f.real_statements for f in file.functions)
    raising = bool(file.classes) and not read.in_tests and all(
        (read.steps, c.name) in defined.exceptions for c in file.classes) and not any(not f.owner for f in file.functions)
    return frozenset(n for n, on in (("no-statements", not code), ("exceptions-only", raising)) if on)


def _exceptions(files: Iterable[tuple[SourceFile, tuple[str, ...]]], root: str) -> set[tuple[tuple[str, ...], str]]:
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


def _bases(files: Iterable[tuple[SourceFile, tuple[str, ...], str]]) -> dict[tuple[str, ...], tuple[tuple[str, ...], ...]]:
    """The bases of every class of the files, each file with its steps below the root and that root, by the class's
    dotted path: a base an import binds by where it leads, one written as the name of a class of the same file by that
    class's path, any other by the name it is written with, alone; a base that is no name is none."""
    found: dict[tuple[str, ...], tuple[tuple[str, ...], ...]] = {}
    for file, steps, root in files:
        local = {c.name for c in file.classes}
        for cls in file.classes:
            written = cls.base_names or ("",) * len(cls.bases)
            found[(root, *steps, cls.name)] = tuple(
                base if base is not None else (root, *steps, name) if name in local else (name,)
                for base, name in zip(cls.bases, written) if base is not None or name)
    return found


def _lineage(path: tuple[str, ...], bases: dict[tuple[str, ...], tuple[tuple[str, ...], ...]]) -> tuple[tuple[str, ...], ...]:
    """Every class the class at path derives from, however far: its own bases first, then theirs when the project
    defines them, each once, the class itself never."""
    found: list[tuple[str, ...]] = []
    pending = list(bases.get(path, ()))
    while pending:
        base = pending.pop(0)
        if base not in found and base != path:
            found.append(base)
            pending += bases.get(base, ())
    return tuple(found)


def _imported(file: SourceFile) -> Iterator[Fact]:
    for i in file.imports:
        traits = _TRAITS[i.relative, i.standard, False] | (_TYPE_ONLY if i.type_only else frozenset())
        if i.names is None:
            yield Fact("imported-name", i.line, i.module, traits=traits, text=i.written)
        else:
            yield from (Fact("imported-name", i.line, (*i.module, name), name,
                             traits if name in i.withheld else traits | _PUBLIC, text=i.written) for name in i.names)
