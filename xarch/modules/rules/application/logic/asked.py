"""The evals the profile writes itself, as rules reads them: what one question of an eval is asked of is each fact of
the kind it reads, in the files of its scope, that passes the filters it keeps, found as a check finds the facts it
reads. An eval is made into a rule that lists each such fact and is never run as a check: a filter that is not a word
of the vocabulary, or does not apply to the kind read, is a problem at the eval's address, as for a check. An example
file holding no fact the eval reads is a problem too: the question would never be asked of it."""
from __future__ import annotations

from dataclasses import replace

from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.application.logic.own_checks import placed
from xarch.modules.rules.domain.errors import RuleRefused
from xarch.modules.rules.domain.rule import EXISTING, MAY_NOT, Fact, Facts, Read, Rule
from xarch.modules.rules.domain.values import Asked, Profile, SourceFile
from xarch.profile_values.checks import LIST, Saying

_READ = "ask the eval's question of it"
"""What the rule that lists the facts an eval reads says of each: it is never shown, since no check runs it."""


def asking(name: str, asked: Asked) -> Rule:
    """The rule that lists each fact the eval reads; raises RuleRefused when a word does not exist or apply."""
    return Rule(name, asked.within, (asked.reads,), MAY_NOT, EXISTING, (Saying("{file}", _READ),), keep=asked.keep,
                mode=LIST, key=f"evals.{name}")


def made(name: str, asked: Asked) -> tuple[Rule | None, list[str]]:
    """The rule of the eval, or None and each problem at its address."""
    try:
        return asking(name, asked), []
    except RuleRefused as refused:
        return None, [f"evals.{name}.{problem}" for problem in refused.problems]


def named(fact: Fact) -> str:
    """How a fact an eval reads is named: Class.method for a method, its name for any other, "" for a file whole."""
    return ".".join(fact.path) if len(fact.path) > 1 else fact.name or ""


def unread(name: str, side: str, files: tuple[tuple[str, str], ...], kept: list[tuple[Read, Fact]],
           reads: str) -> list[str]:
    """A problem for each example file of a side in which the eval reads nothing, at its address."""
    holding = {"/".join(read.file.path) for read, _ in kept}
    return [f"evals.{name}.examples.{side}.{path}: holds no {reads} the eval reads (in its scope, passing keep): give "
            "it one" for path, _ in files if path not in holding]


def project(files: list[tuple[str, SourceFile]], profile: Profile, app: str, rules: tuple[Rule, ...]) -> Facts:
    """The facts of a small project of files, each by its path below the app (tests/<path> for a test) as parsed, the
    app being the package app names: what a check or an eval of the profile's own is held to its examples on."""
    tests = profile.default_tests
    read = [(placed(path, app, tests), parsed) for path, parsed in files]
    app_files = [replace(parsed, name="/".join(shown), path=steps) for (shown, steps, test), parsed in read if not test]
    test_files = [replace(parsed, name="/".join(shown), path=steps) for (shown, steps, test), parsed in read if test]
    return facts_of(app_files, test_files, profile, app, tests, rules)
