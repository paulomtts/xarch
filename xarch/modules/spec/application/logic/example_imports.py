"""The example check: every import of a Python example must be one its part may make by the architecture's rules.

An example is one file of the docs' example project, so it is checked as if it lived at its `path`: the importer's
part is the part its path lies in, and each import of the app's own code is resolved to a part the same way, through
the parts' path patterns (`*` captures the module, the deepest pattern wins, a path no part claims is structure).
The import is allowed when a target in the importer's row of `rules` reaches it: `*`, or the same part, in the
importer's module (@own), in any module (@any) or outside the modules (a bare part), and below its /<path> if it
names one. Structure is reached only by `*`. Imports outside the app's root package (the standard library, third
parties) are not the architecture's business and are ignored.

A tier's example test is checked the same way when its path lies in a part. One that lies in no part, such as one
under tests/, is test code, which no rule of the architecture governs (a test may import whatever it tests), so it
is only parsed: it must be valid Python.
"""
from __future__ import annotations

import ast
from collections.abc import Iterator, Mapping

from xarch.kernel.logic.placement import reaches
from xarch.modules.spec.domain.values import Architecture

ROOT_PACKAGE = "app"
"""The examples' app, as the docs name it: they import `app.<path>`."""
PYTHON = ".py"


def example_problems(architecture: Architecture, texts: Mapping[str, str],
                     tier_texts: Mapping[str, str] | None = None) -> list[str]:
    """Every import of a Python example its part may not make, and every example that lies in no part; texts holds
    each example's file, by name, and tier_texts each tier's example test, by tier name (a tier missing from it is
    not checked)."""
    problems: list[str] = []
    for example in architecture.examples.values():
        if example.file.endswith(PYTHON):
            problems += _problems(architecture, f"example {example.name}", example.path, texts[example.name], True)
    for tier in architecture.tiers:
        if tier.example is not None and tier.example.file.endswith(PYTHON) and tier.name in (tier_texts or {}):
            problems += _problems(architecture, f"tier {tier.name}'s example", tier.example.path,
                                  (tier_texts or {})[tier.name], False)
        for helper in tier.helpers:
            if helper.file.endswith(PYTHON) and helper.file in (tier_texts or {}):
                problems += _problems(architecture, f"tier {tier.name}'s helper", helper.path,
                                      (tier_texts or {})[helper.file], False)
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
        return [f"{shown}: is not valid Python: {e.msg} (line {e.lineno})"]
    if source.part is None:
        return []
    rule = architecture.rules.get(source.part, ())
    found: list[str] = []
    for target, steps in _targets(tree, path[:-1], architecture):
        if not any(reaches(allowed, source, architecture.place_of(steps)) for allowed in rule):
            problem = (f"{shown}: imports {'.'.join((ROOT_PACKAGE, *target))} which {source.part} may not import "
                       f"(rules.{source.part})")
            if problem not in found:
                found.append(problem)
    return found


def _targets(tree: ast.AST, package: tuple[str, ...],
             architecture: Architecture) -> Iterator[tuple[tuple[str, ...], tuple[str, ...]]]:
    """(as shown, as checked): the path below the root package of everything the code imports from it.

    `from m import n` may import a module n, so n is checked as part of the path when m is no part, or a part's own
    folder; it is shown only when m is no part.
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                steps = tuple(alias.name.split("."))
                if steps[0] == ROOT_PACKAGE:
                    yield steps[1:], steps[1:]
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
                yield (base if place.part is not None else steps), steps
