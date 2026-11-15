"""The facts of a run, read once from the parsed files: where each file sits (placement, worked out once per file), and
what it says, by kind, each fact as a rule reads it (see Fact):

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

and the facts derived from them over the whole app:

    build     a call of a class the app defines at the top level of a file, read through the import that binds the
              callee: path the callee, at where the class's file sits
    reference a use that reaches a function the app defines at the top level of a file (the first prefix, from the
              one its import bound, whose last name the file binds to a function alone): target that function below
              the root, at where its file sits
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator

from xarch.modules.rules.application.logic.imports import dotted, named_targets, targets
from xarch.modules.rules.application.logic.places import place
from xarch.modules.rules.application.logic.tier_of import tested
from xarch.modules.rules.domain.rule import Defined, Fact, Facts, Read
from xarch.modules.rules.domain.values import Profile, SourceFile


def facts_of(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
             tests_root: str = "") -> Facts:
    """The facts of the app's files, below the root package root, and of the test files, below the package
    tests_root."""
    marks = profile.language.marks
    app, tests = [(f, *dotted(f.path, marks)) for f in app], [(f, *dotted(f.path, marks)) for f in tests]
    known = frozenset(steps for _, steps, _ in app)
    known_tests = frozenset(steps for _, steps, _ in tests)
    defined = Defined(root, {(root, *steps, c.name): place(profile, steps) for f, steps, _ in app for c in f.classes},
                      {steps: frozenset(f.module_functions) for f, steps, _ in app})
    read = [_app(file, steps, package, profile, defined, known) for file, steps, package in app]
    read += [_test(file, steps, package, profile, defined, tests_root, known, known_tests)
             for file, steps, package in tests]
    return Facts(tuple(read), root, tests_root, known, known_tests,
                 frozenset(r.steps for r in read if r.test and r.is_test))


def _app(file: SourceFile, steps: tuple[str, ...], package: bool, profile: Profile, defined: Defined,
         known: frozenset[tuple[str, ...]]) -> Read:
    edges = tuple(Fact("edge", line, name=name, target=target, at=place(profile, target))
                  for line, target, name in named_targets(file.imports, steps if package else steps[:-1], known,
                                                          defined.root))
    return Read(file, steps, package, False, place(profile, steps), facts=_said(file, profile, defined) | {"edge": edges})


def _test(file: SourceFile, steps: tuple[str, ...], package: bool, profile: Profile, defined: Defined,
          tests_root: str, known: frozenset[tuple[str, ...]], known_tests: frozenset[tuple[str, ...]]) -> Read:
    where = tested(profile, file.path)
    absolute = tuple(i for i in file.imports if not i.relative)
    edges = tuple(Fact("edge", line, target=target, at=place(profile, target))
                  for line, target in targets(absolute, (), known, defined.root))
    own = tuple(Fact("suite_edge", line, target=target)
                for line, target in targets(file.imports, steps if package else steps[:-1], known_tests, tests_root))
    return Read(file, steps, package, True, None, where.tier.name if where.tier is not None else "", where.instance,
                where.own, where.parts, where.is_test, where.is_fake,
                _said(file, profile, defined) | {"edge": edges, "suite_edge": own})


def _said(file: SourceFile, profile: Profile, defined: Defined) -> dict[str, tuple[Fact, ...]]:
    root = defined.root
    return {"file": (Fact("file", 0),),
            "import": tuple(Fact("import", i.line, i.module, traits=_traits(i.relative, i.standard), text=i.written)
                            for i in file.imports),
            "imported": tuple(_imported(file)),
            "use": tuple(Fact("use", u.line, u.name, bound=u.bound) for u in file.uses),
            "method": tuple(Fact("method", m.line, name=m.name, traits=_traits(held=m.held)) for m in file.method_calls),
            "call": tuple(Fact("call", c.line, c.func, at=place(profile, c.func[1:]) if c.func[:1] == (root,) else None)
                          for c in file.calls),
            "build": tuple(Fact("build", c.line, c.func, at=defined.classes[c.func]) for c in file.calls
                           if c.func in defined.classes),
            "reference": tuple(_references(file, profile, defined))}


def _references(file: SourceFile, profile: Profile, defined: Defined) -> Iterator[Fact]:
    for use in file.uses:
        if use.name[:1] != (defined.root,):
            continue
        for end in range(max(use.bound, 2), len(use.name) + 1):
            module, function = use.name[1:end - 1], use.name[end - 1]
            if function in defined.functions.get(module, ()):
                yield Fact("reference", use.line, use.name, target=(*module, function), at=place(profile, module))
                break


def _imported(file: SourceFile) -> Iterator[Fact]:
    for i in file.imports:
        traits = _traits(i.relative, i.standard)
        if i.names is None:
            yield Fact("imported", i.line, i.module, traits=traits, text=i.written)
        else:
            yield from (Fact("imported", i.line, (*i.module, name), name, traits, text=i.written) for name in i.names)


def _traits(relative: bool = False, standard: bool = False, held: bool = False) -> frozenset[str]:
    return frozenset(name for name, on in (("relative", relative), ("standard", standard), ("held", held)) if on)
