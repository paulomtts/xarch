"""The example check: every import of an example must be one its part may make by the architecture's rules.

An example is one file of an example project of the docs, so it is checked as if it lived at its `path`: the
importer's part is the part its path lies in, and each import of the app's own code is resolved to a part the same
way, through the parts' path patterns (the repeating folder captures the instance, the deepest pattern wins, a path no
part claims is structure). The import is allowed when a target in the importer's `imports.may` reaches it: everything,
or the same part, in the importer's instance (a bare name), in any instance (@any) or outside the repeating folder,
and below its /<path> if it names one. Structure is reached only by everything. Imports outside the app's root
package (the standard library, third parties) are not the architecture's business and are ignored. The example
project's app is the one the docs' example project names (EXAMPLE_APP), and its test code lies in the default tests
folder.

The examples are read by the reader of the app's language, as data: what each imports, or where and why it does not
parse. Every source file of the language below the example projects is checked, so a file that lies in no part is
reported, except the test code below the tests folder: no rule of the architecture governs it (a test may import
whatever it tests), so it is only read and must be valid.
"""
from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping

from xarch.kernel.logic.examples import is_test_example
from xarch.kernel.logic.placement import reaches, stem
from xarch.kernel.logic.source import imported_names
from xarch.kernel.source import Import, Unparsable
from xarch.modules.spec.domain.published import DEFAULT_TESTS, EXAMPLE_APP
from xarch.modules.spec.domain.values import Architecture, Example

Read = tuple[Import, ...] | Unparsable
"""An example as the reader read it: its imports in order, or where and why it does not parse."""


def checked_examples(architecture: Architecture) -> tuple[Example, ...]:
    """The examples the check reads: those whose file is a source file of the app's language, of any of its endings."""
    marks = architecture.language.checked.marks
    return tuple(example for example in architecture.examples.values()
                 if stem(example.file.rsplit("/", 1)[-1], marks) is not None)


def example_problems(architecture: Architecture, reads: Mapping[str, Read]) -> list[str]:
    """Every import of an example its part may not make, and every example that lies in no part or does not parse;
    reads holds each checked example as read, by its name."""
    problems: list[str] = []
    for example in checked_examples(architecture):
        problems += _problems(architecture, example.path, reads[example.name],
                              not is_test_example(example.path, DEFAULT_TESTS))
    return problems


def _problems(architecture: Architecture, path: tuple[str, ...], read: Read, in_part: bool) -> list[str]:
    """The example's problems; in_part: it must lie in a part, as an example of the app's own code does.

    Test code: no rule governs what it imports.
    """
    shown = f"example ({'/'.join(path)})"
    source = architecture.place_of(path)
    if source.part is None and in_part:
        return [f"{shown}: lies in no part of the architecture"]
    if isinstance(read, Unparsable):
        return [f"{shown}: is not valid {architecture.language.checked.title}: {read.message} (line {read.line})"]
    if source.part is None:
        return []
    rule = architecture.targets_of(source.part)
    found: list[str] = []
    for target, steps, name in _targets(read, path[:-1], architecture):
        if not any(reaches(allowed, source, architecture.place_of(steps), name) for allowed in rule):
            problem = (f"{shown}: imports {'.'.join((EXAMPLE_APP, *target))} which {source.part} may not import "
                       f"(parts.{source.part}.imports.may)")
            if problem not in found:
                found.append(problem)
    return found


def _targets(imports: Iterable[Import], folder: tuple[str, ...],
             architecture: Architecture) -> Iterator[tuple[tuple[str, ...], tuple[str, ...], str | None]]:
    """(as shown, as checked, the name imported from it): the path below the root package of everything the code
    imports from it, folder being the example's own folder.

    Importing names from m may import a module of that name, so a name is checked as part of the path when m is no
    part, or a part's own folder; it is shown only when m is no part. The name is the one imported when it is not
    checked as part of the path, else None: what is imported is the whole of the path.
    """
    for imp in imports:
        for base, name in imported_names(imp, folder, EXAMPLE_APP):
            if name is None:
                yield base, base, None
                continue
            place = architecture.place_of(base)
            steps = base if imp.every or place.sub else base + (name,)
            yield (base if place.part is not None else steps), steps, name if steps == base else None


def shipped_problems(architecture: Architecture, reads: Mapping[str, Read], bundled: bool) -> list[str]:
    """The example problems a profile may not have when its docs are written: every one, for a bundled profile, which
    ships with xarch; none for a custom one, whose examples `profile check` reports instead."""
    return example_problems(architecture, reads) if bundled else []
