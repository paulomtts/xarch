"""The checks the rules as data now are, called as each check's unit tests always called it: the rules a profile's keys
expand to, run by the engine over the facts of the files given, read as production reads them (only the kinds of fact
the rules read, see facts_of), so that a rule that declares too little fails here as it would in a check."""
from __future__ import annotations

from collections.abc import Iterable

from xarch.kernel.violations import Violation
from xarch.modules.rules.application.logic import expansion, known
from xarch.modules.rules.application.logic.engine import run
from xarch.modules.rules.application.logic.facts import facts_of
from xarch.modules.rules.domain.outcomes import Accepting
from xarch.modules.rules.domain.parsed import Comment, SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.published import Weak
from xarch.modules.rules.domain.rule import Rule
from xarch.profile_values.language import CheckedLanguage


def checked(rules: Iterable[Rule], profile: Profile, app: Iterable[SourceFile] = (), tests: Iterable[SourceFile] = (),
            root: str = "", tests_root: str = "", unread: Iterable[SourceFile] = ()) -> list[Violation | Weak]:
    rules = tuple(rules)
    return run(rules, facts_of(app, tests, profile, root, tests_root, rules, unread), profile)


def libraries(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["libraries"], profile, files, root=root)


def forbidden(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["never-use"], profile, app, tests)


def package_only(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile,
                 root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["package-only"], profile, app, tests, root)


def private_imports(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
                    tests_root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["private-imports"], profile, app, tests, root, tests_root)


def built_by(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["built-by"], profile, app, root=root)


def rules(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["rules"], profile, files, root=root)


def types_only(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile,
               root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["types-only tiers"], profile, app, tests, root)


def types_only_parts(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["types-only parts"], profile, app, root=root)


def tiers(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile, root: str,
          tests_root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["tiers"], profile, app, tests, root, tests_root)


def syntax(files: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["syntax"], profile, files)


def names(app: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["names"], profile, app)


def no_callbacks(app: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["no-callbacks"], profile, app)


def no_comments(files: Iterable[SourceFile], language: CheckedLanguage) -> list[Violation | Weak]:
    profile = Profile(parts={}, rules={}, no_comments=True, language=language)
    return checked(expansion.book(profile)["no-comments"], profile, files)


def comment_allowed(comment: Comment, language: CheckedLanguage) -> bool:
    """Whether the no-comments rule excuses a comment: the language's tools read it."""
    return not no_comments([SourceFile("x", ("x",), (), comments=(comment,))], language)


def closed_tree(paths: Iterable[tuple[str, ...]], profile: Profile, shown: str) -> list[Violation | Weak]:
    unread = [SourceFile("/".join((shown, *path)), path, ()) for path in paths]
    return checked(expansion.book(profile)["closed-tree"], profile, unread=unread)


def holds(app: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked((*expansion.book(profile)["holds"], *expansion.book(profile)["immutable"]), profile, app, root=root)


def must_import(files: Iterable[SourceFile], profile: Profile, root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["must-import"], profile, files, root=root)


def must_import_tiers(tests: Iterable[SourceFile], app: Iterable[SourceFile], profile: Profile, root: str,
                      tests_root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["must-import tiers"], profile, app, tests, root, tests_root)


def dead_code(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile,
              has_tests: bool = True) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["dead-code"], profile, app, tests if has_tests else [])


def only_by_tests(app: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["tests-only"], profile, app)


def accepting(app: Iterable[SourceFile], profile: Profile, root: str,
              tests: Iterable[SourceFile] = ()) -> Accepting:
    """What the tests-only check lists of the app, the names the profile accepts as only the tests' taken out and the
    entries that no longer hold added, as the check of an app and its tests holds them, on the same facts."""
    rules = expansion.book(profile)["tests-only"]
    facts = facts_of(app, tests, profile, root, "tests", rules, ())
    return known.accepting(run(rules, facts, profile), facts, profile)


def untested(app: Iterable[SourceFile], tests: Iterable[SourceFile], profile: Profile, root: str,
             tests_root: str) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["untested"], profile, app, tests, root, tests_root)


def pass_through(app: Iterable[SourceFile], profile: Profile) -> list[Violation | Weak]:
    return checked(expansion.book(profile)["pass-through"], profile, app)
