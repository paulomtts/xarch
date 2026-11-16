"""The checks the rules as data now are, called as each check's unit tests always called it: the rules a profile's keys
expand to, run by the engine over the facts of the files given, read as production reads them (only the kinds of fact
the rules read, see facts_of), so that a rule that declares too little fails here as it would in a check."""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation, Weak
from xarch.modules.rules.application.logic import expansion
from xarch.modules.rules.application.logic.engine import run
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.domain.rule import Rule
from xarch.modules.rules.domain.values import Comment, Profile, SourceFile
from xarch.profile_values.language import CheckedLanguage


def checked(rules: Iterable[Rule], profile: Profile, app: Iterable[SourceFile] = (), tests: Iterable[SourceFile] = (),
            root: str = "", tests_root: str = "", unread: Iterable[SourceFile] = ()) -> list[Violation | Weak]:
    rules = tuple(rules)
    return run(rules, facts_of(app, tests, profile, root, tests_root, rules, unread), profile)


def libraries(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.libraries(profile), profile, files, root=root)


def forbidden(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.forbidden(profile), profile, app, tests)


def package_only(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile,
                 root: str) -> list[Violation | Weak]:
    return checked(expansion.package_only(profile), profile, app, tests, root)


def private_imports(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
                    tests_root: str) -> list[Violation | Weak]:
    return checked(expansion.private_imports(profile), profile, app, tests, root, tests_root)


def built_by(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.built_by(profile), profile, app, root=root)


def rules(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.rules(profile), profile, files, root=root)


def types_only(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile,
               root: str) -> list[Violation | Weak]:
    return checked(expansion.types_only_tiers(profile), profile, app, tests, root)


def types_only_parts(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.types_only_parts(profile), profile, app, root=root)


def tiers(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile, root: str,
          tests_root: str) -> list[Violation | Weak]:
    return checked(expansion.tiers(profile), profile, app, tests, root, tests_root)


def syntax(files: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.syntax(profile), profile, files)


def names(app: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.names(profile), profile, app)


def no_callbacks(app: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.no_callbacks(profile), profile, app)


def no_comments(files: Iterable[SourceFile], language: CheckedLanguage) -> list[Violation | Weak]:
    profile = Profile(parts={}, rules={}, no_comments=True, language=language)
    return checked(expansion.no_comments(profile), profile, files)


def comment_allowed(comment: Comment, language: CheckedLanguage) -> bool:
    """Whether the no-comments rule excuses a comment: the language's tools read it."""
    return not no_comments([SourceFile("x", ("x",), (), comments=(comment,))], language)


def closed_tree(paths: Iterable[tuple[str, ...]], profile: Profile, shown: str) -> list[Violation | Weak]:
    unread = [SourceFile("/".join((shown, *path)), path, ()) for path in paths]
    return checked(expansion.closed_tree(profile), profile, unread=unread)


def holds(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.holds(profile), profile, app, root=root)


def must_import(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.must_import(profile), profile, files, root=root)


def must_import_tiers(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile, root: str,
                      tests_root: str) -> list[Violation | Weak]:
    return checked(expansion.must_import_tiers(profile), profile, app, tests, root, tests_root)


def dead_code(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile,
              has_tests: bool = True) -> list[Violation | Weak]:
    return checked(expansion.dead_code(profile), profile, app, tests if has_tests else [])


def untested(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
             tests_root: str) -> list[Violation | Weak]:
    return checked(expansion.untested(profile), profile, app, tests, root, tests_root)


def pass_through(app: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.pass_through(profile), profile, app)
