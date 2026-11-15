"""The checks the rules as data now are, called as each check's unit tests always called it: the rules a profile's keys
expand to, run by the engine over the facts of the files given."""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.logic.language import LanguageView
from xarch.kernel.violations import Violation, Weak
from xarch.modules.rules.application.logic import expansion, filters
from xarch.modules.rules.application.logic.engine import run
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.domain.rule import Fact, Found, Read
from xarch.modules.rules.domain.values import Comment, Profile, SourceFile


def libraries(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return run(expansion.libraries(profile), facts_of(files, [], profile, root), profile)


def forbidden(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return run(expansion.forbidden(profile), facts_of(app, tests, profile, ""), profile)


def package_only(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile,
                 root: str) -> list[Violation | Weak]:
    return run(expansion.package_only(profile), facts_of(app, tests, profile, root), profile)


def private_imports(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
                    tests_root: str) -> list[Violation | Weak]:
    return run(expansion.private_imports(profile), facts_of(app, tests, profile, root, tests_root), profile)


def built_by(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return run(expansion.built_by(profile), facts_of(app, [], profile, root), profile)


def rules(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return run(expansion.rules(profile), facts_of(files, [], profile, root), profile)


def types_only(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile,
               root: str) -> list[Violation | Weak]:
    return run(expansion.types_only_tiers(profile), facts_of(app, tests, profile, root), profile)


def types_only_parts(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return run(expansion.types_only_parts(profile), facts_of(app, [], profile, root), profile)


def tiers(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile, root: str,
          tests_root: str) -> list[Violation | Weak]:
    return run(expansion.tiers(profile), facts_of(app, tests, profile, root, tests_root), profile)


def syntax(files: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return run(expansion.syntax(profile), facts_of(files, [], profile, ""), profile)


def names(app: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return run(expansion.names(profile), facts_of(app, [], profile, ""), profile)


def no_callbacks(app: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return run(expansion.no_callbacks(profile), facts_of(app, [], profile, ""), profile)


def no_comments(files: Iterable[SourceFile], language: LanguageView) -> list[Violation | Weak]:
    profile = Profile(parts={}, rules={}, no_comments=True, language=language)
    return run(expansion.no_comments(profile), facts_of(files, [], profile, ""), profile)


def comment_allowed(comment: Comment, language: LanguageView) -> bool:
    """Whether the no-comments rule excuses a comment: the language's tools read it."""
    profile = Profile(parts={}, rules={}, no_comments=True, language=language)
    (rule,) = expansion.no_comments(profile)
    found = Found(rule, Read(SourceFile("x", ("x",), ()), ("x",), False, False), Fact("comment", comment.line,
                                                                                       text=comment.text))
    return filters.holds("read-by-a-tool", found, facts_of([], [], profile, ""), profile)


def closed_tree(paths: Iterable[tuple[str, ...]], profile: Profile, shown: str) -> list[Violation | Weak]:
    unread = [SourceFile("/".join((shown, *path)), path, ()) for path in paths]
    return run(expansion.closed_tree(profile), facts_of([], [], profile, "", unread=unread), profile)


def holds(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return run(expansion.holds(profile), facts_of(app, [], profile, root), profile)


def must_import(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return run(expansion.must_import(profile), facts_of(files, [], profile, root), profile)


def must_import_tiers(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile, root: str,
                      tests_root: str) -> list[Violation | Weak]:
    return run(expansion.must_import_tiers(profile), facts_of(app, tests, profile, root, tests_root), profile)


def dead_code(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile,
              has_tests: bool = True) -> list[Violation | Weak]:
    return run(expansion.dead_code(profile), facts_of(app, tests if has_tests else [], profile, ""), profile)


def untested(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
             tests_root: str) -> list[Violation | Weak]:
    return run(expansion.untested(profile), facts_of(app, tests, profile, root, tests_root), profile)
