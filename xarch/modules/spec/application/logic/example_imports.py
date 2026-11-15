"""The example check: every import of an example must be one its part may make by the architecture's rules.

An example is one file of an example project of the docs, so it is checked as if it lived at its `path`: the
importer's part is the part its path lies in, and each import of the app's own code is resolved to a part the same
way, through the parts' path patterns (the repeating folder captures the instance, the deepest pattern wins, a path no
part claims is structure). The import is allowed when a target in the importer's `may_import` reaches it: everything,
or the same part, in the importer's instance (a bare name), in any instance (@any) or outside the repeating folder,
and below its /<path> if it names one. Structure is reached only by everything. Imports outside the app's root
package (the standard library, third parties) are not the architecture's business and are ignored.

Every source file of the language below the example projects is checked, so a file that lies in no part is reported,
except the test code below tests/: no rule of the architecture governs it (a test may import whatever it tests), so it
is only parsed and must be valid.
"""
from __future__ import annotations

import ast
from collections.abc import Iterator, Mapping

from xarch.kernel.logic.placement import reaches
from xarch.modules.spec.domain.values import Architecture

ROOT_PACKAGE = "app"
"""The examples' app, as the docs name it: they import `app.<path>`."""
TESTS = "tests"
"""The folder of an example project that holds test code, which no rule governs, so that it is only parsed."""


def example_problems(architecture: Architecture, texts: Mapping[str, str]) -> list[str]:
    """Every import of an example its part may not make, and every example that lies in no part; texts holds
    each example's file, by its path."""
    problems: list[str] = []
    for example in architecture.examples.values():
        if example.file.endswith(architecture.language.extension):
            problems += _problems(architecture, "example", example.path, texts[example.name], example.path[0] != TESTS)
    return problems


def _problems(architecture: Architecture, name: str, path: tuple[str, ...], text: str,
              in_part: bool) -> list[str]:
    """The example's problems; in_part: it must lie in a part, as an example of the app's own code does.

    Test code: no rule governs what it imports.
    """
    shown = f"{name} ({'/'.join(path)})"
    source = architecture.place_of(path)
    if source.part is None and in_part:
        return [f"{shown}: lies in no part of the architecture"]
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        return [f"{shown}: is not valid {architecture.language.title}: {e.msg} (line {e.lineno})"]
    if source.part is None:
        return []
    rule = architecture.targets_of(source.part)
    found: list[str] = []
    for target, steps, name in _targets(tree, path[:-1], architecture):
        if not any(reaches(allowed, source, architecture.place_of(steps), name) for allowed in rule):
            problem = (f"{shown}: imports {'.'.join((ROOT_PACKAGE, *target))} which {source.part} may not import "
                       f"(parts.{source.part}.may_import)")
            if problem not in found:
                found.append(problem)
    return found


def _targets(tree: ast.AST, package: tuple[str, ...],
             architecture: Architecture) -> Iterator[tuple[tuple[str, ...], tuple[str, ...], str | None]]:
    """(as shown, as checked, the name imported from it): the path below the root package of everything the code
    imports from it.

    `from m import n` may import a module n, so n is checked as part of the path when m is no part, or a part's own
    folder; it is shown only when m is no part. The name is n when it is not checked as part of the path, else None:
    what is imported is the whole of the path.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                steps = tuple(alias.name.split("."))
                if steps[0] == ROOT_PACKAGE:
                    yield steps[1:], steps[1:], None
        elif isinstance(node, ast.ImportFrom):
            module = tuple(node.module.split(".")) if node.module else ()
            if node.level:
                keep = len(package) - (node.level - 1)
                if keep < 0:
                    continue
                base = package[:keep] + module
            elif module[:1] == (ROOT_PACKAGE,):
                base = module[1:]
            else:
                continue
            place = architecture.place_of(base)
            for alias in node.names:
                steps = base if alias.name == "*" or place.sub else base + (alias.name,)
                yield (base if place.part is not None else steps), steps, alias.name if steps == base else None


def shipped_problems(architecture: Architecture, texts: Mapping[str, str], bundled: bool) -> list[str]:
    """The example problems a profile may not have when its docs are written: every one, for a bundled profile, which
    ships with xarch; none for a custom one, whose examples `profile check` reports instead."""
    return example_problems(architecture, texts) if bundled else []
