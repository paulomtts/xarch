"""What the keys of a profile mean as rules as data: each check's keys expand to the rules the engine runs, in the
order the check reads them, each saying what the check has always said. The keys of the profile stay as they are;
this is what they mean, in the words a profile writes its own checks in (`xarch profile explain <key> --rule` prints
them so).
"""
from __future__ import annotations

from dataclasses import replace

from xarch.kernel.logic.conditions import condition
from xarch.kernel.placement import EVERYTHING
from xarch.modules.rules.application.logic.tier_of import NO_TIER, NO_TIER_FIX
from xarch.modules.rules.domain.profile import Profile
from xarch.modules.rules.domain.rule import EXISTING, LIST, MAY_NOT, MAY_ONLY, MUST_BE_REACHED, MUST_REACH, Match, Rule
from xarch.profile_values.checks import ALL, APP, STRUCTURE, TESTS, Condition, Saying, Scope

NEVER_USE_FIX = "do what needs {hit} outside {scope_part}/, and hand {scope_part}/ the result"
_of = condition


def _all(*texts: str) -> tuple[Condition, ...]:
    return tuple(_of(text) for text in texts)


def _libraries(profile: Profile) -> tuple[Rule, ...]:
    """A part imports only the outside packages its `imports.libraries` lists; the standard library and the app's own package
    are always allowed, and a relative import is the app's own, but a module of the standard library the profile
    reserves is an outside package; one finding per package and line. No rule when no part lists libraries, and none
    for a part whose list is everything."""
    if profile.imports_libraries is None:
        return ()
    reserved = ("{where} may not import {package}, which the profile reserves: {reserved_reason} (reserved.{package}; "
                "{key})")
    outside = "{where} may not import the outside package {package} ({key})"
    owners = "move the code that needs {package} to {library_owners}, which may import it (parts.{first_library_owner}" \
             ".imports.libraries)"
    once = ("line", "package")
    sayings = (Saying(reserved, owners, _all("reserved", "listed-by-another-part"), once),
               Saying(reserved, "list {package} in the libraries of the part it is reserved for, and keep the code "
                                "that needs it there", _all("reserved"), once),
               Saying(outside, owners, _all("listed-by-another-part"), once),
               Saying(outside, "use the standard library or a package listed in {key}, since {package} is listed for "
                               "no part", once=once))
    return tuple(Rule("libraries", Scope(APP, part), ("import",), MAY_ONLY, (Match("package", words=allowed),),
                      sayings, keep=keep, exempt=exempt, key=f"parts.{part}.imports.libraries")
                 for part in profile.parts if EVERYTHING not in (allowed := profile.imports_libraries.get(part, ()))
                 for keep, exempt in ((_all("not relative", "not reserved"), _all("app-package", "standard")),
                                      (_all("not relative", "reserved"), _all("app-package"))))


def _never_use(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part with a `uses.never` list neither imports what it names, nor uses a name it lists, nor calls a
    method it lists on anything but what its object holds; a test of a tier that applies the lists
    (`uses.apply_never`) is held to the list of each part it mirrors. One finding per line and name."""
    if not profile.uses_never:
        return ()
    facts = ("imported-name", "use", "method-call")
    keep, exempt = _all("not relative", "not on-own-object"), _all("reported-at-import")
    fakes = (_of(f"not below {'/'.join(profile.fakes.folder)}"),) if profile.fakes is not None else ()
    found = [Rule("never-use", Scope(APP, part), facts, MAY_NOT, (Match("path", names=names),),
                  (Saying("{where} may not {verb} {hit} ({key})", NEVER_USE_FIX, once=("line", "hit")),),
                  keep=keep, exempt=exempt, key=f"parts.{part}.uses.never")
             for part, names in profile.uses_never.items()]
    found += [Rule("never-use", Scope(TESTS, part, tier.name, fakes), facts, MAY_NOT, (Match("path", names=names),),
                   (Saying("a test of {scope_part}/ ({tier} tier) may not {verb} {hit} ({key})", NEVER_USE_FIX,
                           once=("line", "hit")),),
                   keep=keep, exempt=exempt, key=f"parts.{part}.uses.never; tiers.{tier.name}.uses.apply_never")
              for tier in profile.tiers if tier.apply_never for part, names in profile.uses_never.items()]
    return tuple(found)


def _package_only(profile: Profile) -> tuple[Rule, ...]:
    """A part the guard names is imported as a package, never by one of its files, from anywhere outside its own
    folder (its own instance, for a part in a repeating folder), the tests included."""
    if not profile.package_only:
        return ()
    return (Rule("package-only", Scope(ALL), ("import-into-app",), MAY_NOT,
                 (Match("part", words=profile.package_only),),
                 (Saying("{target_part} is imported only as a package, never by its files ({target}) (package-only)",
                         "import from {target_package}"),),
                 keep=_all("target-placed", "target-inside-part"), exempt=_all("target-in-own-part"),
                 key="parts.<part>.package_only"),)


def _private_imports(profile: Profile) -> tuple[Rule, ...]:
    """No file of the app or the tests imports a name private in the language from the app's or the tests' own
    package, or relatively; one finding per name."""
    if not profile.private_imports:
        return ()
    return (Rule("private-imports", Scope(ALL), ("imported-name",), MAY_NOT, EXISTING,
                 (Saying("imports the private name {name} from {written} (private-imports)",
                         "make {name} public where it is defined, or move it to a file both may import"),),
                 keep=_all("takes-a-name", "own-code", "not public", "not special"), key="guards.private-imports"),)


def _built_by(profile: Profile) -> tuple[Rule, ...]:
    """Only the parts the classes of a part's `holds` list in `built_by` build a class it defines at the top level of a
    file and holds to classes: one rule for the parts that list no narrower kind beside classes, and one of its own for
    each part that does, which a class held to that kind does not break; the tests are not read."""
    plain = tuple(part for part in profile.holds_built_by if not _narrower(profile, part))
    said = (Saying("{where} builds {name}, a class of {target_part}, which only {built_by} may build "
                   "(parts.{target_part_name}.holds.classes.built_by)",
                   "take {name} as a parameter of the constructor, and build it in {built_by}"),)
    groups = [(plain, ())] if plain else []
    groups += [((part,), _narrower(profile, part)) for part in profile.holds_built_by if _narrower(profile, part)]
    return tuple(Rule("built-by", Scope(APP), ("construction",), MAY_NOT, (Match("part", words=parts),), said,
                      exempt=_all("target-allows-under built_by", *exempt), key="parts.<part>.holds.classes.built_by")
                 for parts, exempt in groups)


_NARROWER = (("exceptions", "exception"), ("records", "record"))
"""The kinds narrower than classes, narrowest first, each with the filter of the class that fits it."""


def _narrower(profile: Profile, part: str) -> tuple[str, ...]:
    """The filters of the kinds narrower than classes that the part's `holds` lists, narrowest first: a class that
    fits one is held to that kind's settings, never to those of classes."""
    kinds = profile.holds.get(part, ())
    return tuple(trait for kind, trait in _NARROWER if kind in kinds)


def _rules(profile: Profile) -> tuple[Rule, ...]:
    """Every import between places the profile governs is allowed by the rules of the importing file's part: a part
    may import itself and its `imports.may`, where a target with a name pattern allows only the names it matches;
    the structure may import nothing the profile governs."""
    narrowed = Saying("{where} may import only {allowed_names} from {target_part}, {disallowed_name} ({target_name})",
                      "import from {target_part} only names that match {allowed_names} ({key}), or move what "
                      "needs the rest to a part that may import it", _all("names-restricted"))
    plain = "{where} may not import {target_part} ({target})"
    found = [Rule("may-import", Scope(APP, part), ("import-into-app",), MAY_ONLY, (Match("permitted"),),
                  (narrowed, Saying(plain, "import only {importable_parts} in {where} ({key}), or {move_fix}")),
                  keep=_all("target-placed"), key=f"parts.{part}.imports.may") for part in profile.parts]
    return (*found, Rule("may-import", Scope(APP, STRUCTURE), ("import-into-app",), MAY_ONLY, (Match("permitted"),),
                         (Saying(plain, "drop the import of {target_part}, or {move_fix}"),), keep=_all("target-placed")))


def _types_only_tiers(profile: Profile) -> tuple[Rule, ...]:
    """A test of a tier that names parts in `imports.types_only` never calls what it imports from them, and never references
    one of their functions; a call is not said again as a reference."""
    return tuple(_types_only(Scope(TESTS, tier=tier.name), f"a {tier.name} test", f"tiers.{tier.name}.imports.types_only",
                             Match("part", words=tier.imports_types_only), "{tier_type_only_fix}")
                 for tier in profile.tiers if tier.imports_types_only)


def _types_only_parts(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part whose `imports.may` marks entries types_only is held to the same rule on what those entries
    reach: their part, instance scope and path, a name pattern aside, which narrows only what may be imported."""
    return tuple(_types_only(Scope(APP, part), "{where}", f"parts.{part}.imports.may.types_only",
                             Match("place", places=tuple(replace(target, names="") for target in targets)),
                             "{type_only_fix}")
                 for part, targets in profile.imports_types_only.items())


def _types_only(scope: Scope, who: str, key: str, match: Match, fix: str) -> Rule:
    said = f"{who} uses {{target_part}} only as a type: it may not "
    return Rule("types-only", scope, ("call", "function-reference"), MAY_NOT, (match,),
                (Saying(said + "call {path} ({key})", fix, _all("of-kind call")),
                 Saying(said + "reference {target}, a function ({key})", fix)),
                keep=_all("target-placed"), key=key)


def _tiers(profile: Profile) -> tuple[Rule, ...]:
    """A test file lies in a tier; a file of a tier imports, of the app, what the part its folder mirrors may (or its
    tier's subject, for one placed by its tier's folder); and of the test code, the fakes only when its tier tests a
    part they stand in for, never another test file (once per line), and anything else only from its own folder. The
    rule of what a tier's file imports of the app is keyed by each tier's imports.also too, for a tier that sets
    it."""
    if not profile.tiers:
        return ()
    folder = "/".join(profile.fakes.folder) if profile.fakes is not None else ""
    not_fake = (_of(f"not below {folder}"),) if folder else ()
    mirrored = Saying("a test of {mirrored_parts} ({tier} tier) may not import {target_part} ({target}): it imports "
                      "only what {mirrored_parts} may ({mirrored_may_import})",
                      "import here only what {mirrored_parts} may; test {target_part} from the folder that mirrors it",
                      _all("mirrors-a-part"))
    by_folder = Saying("a {tier} test may not import {target_part} ({target})",
                       "import here only what the subject of the {tier} tier may; test {target_part} from the folder "
                       "that mirrors it")
    fakes = (Saying("a {tier} test may not import the fakes ({target}): only a tier that tests {faked_parts} may",
                    "drop the import of {target}, or move the test to a tier that tests {faked_parts}",
                    _all(f"target-below {folder}")),) if folder else ()
    test = Saying("a test may not import another test file ({target}): what tests share lives in test code that is no "
                  "test file",
                  "move what {target} holds that this test needs into test code of its folder that is no test file, "
                  "and import it from there", _all("target-test"), ("line", "target"))
    elsewhere = Saying("a test may import test code only from its own folder {own_folder}/ ({target})",
                       "move what {target} holds into {own_folder}/, or drop the import")
    also = "".join(f"; tiers.{tier.name}.imports.also" for tier in profile.tiers if tier.imports_also)
    return (Rule("tiers", Scope(TESTS, where=(_of("not tiered"), _of("test"), *not_fake)), ("file",), MAY_NOT,
                 EXISTING, (Saying(NO_TIER, NO_TIER_FIX),), key="tiers"),
            Rule("tiers", Scope(TESTS, where=_all("tiered")), ("import-into-app",), MAY_ONLY, (Match("permitted"),),
                 (mirrored, by_folder), keep=_all("target-placed"), key=f"tiers{also}"),
            Rule("tiers", Scope(TESTS, where=_all("tiered")), ("import-into-tests",), MAY_ONLY, (Match("permitted"),),
                 (*fakes, test, elsewhere), key="tiers"))


def _syntax(profile: Profile) -> tuple[Rule, ...]:
    """A file that does not parse is a violation, at the line its error is on, and no other rule reads it; so is one
    that cannot be read as text at all, which says why."""
    return (Rule("syntax", Scope(ALL), ("syntax-error",), MAY_NOT, EXISTING,
                 (Saying("{text}, so no check reads it", "save the file as UTF-8 text that xarch may read",
                         _all("unreadable")),
                  Saying("not valid {language}: {text}", "correct the syntax so that the file can be read"))),)


def _names(profile: Profile) -> tuple[Rule, ...]:
    """Every public definition a part holds to a kind whose `names` it gives matches one of its patterns, `*` standing
    for any text: a class held to classes (not one a narrower kind listed beside them holds), a top-level function, a
    record held to records (not an exception, when exceptions are listed) and an exception."""
    return tuple(_named(profile, part, kind, patterns) for part, kinds in profile.holds_names.items()
                 for kind in _KINDS if (patterns := kinds.get(kind)))


_KINDS = ("classes", "functions", "records", "exceptions")
"""The kinds a part's `holds` lists, in the order they are read."""
_NAMED = {"classes": ("class", (), "class"), "functions": ("function", ("top-level",), "function"),
          "records": ("class", ("record",), "record"), "exceptions": ("class", ("exception",), "exception")}
"""What the names of each kind read: the kind of fact, the filters that keep the definitions of the kind, and what
the finding calls one."""


def _named(profile: Profile, part: str, kind: str, patterns: tuple[str, ...]) -> Rule:
    fact, kept, called = _NAMED[kind]
    if kind == "classes":
        exempt = _narrower(profile, part)
    else:
        exempt = ("exception",) if kind == "records" and "exceptions" in profile.holds.get(part, ()) else ()
    return Rule("names", Scope(APP, part), (fact,), MAY_ONLY, (Match("name", words=patterns),),
                (Saying(f"{{name}} does not match {{targets}}, as every {called} of {{where}} must ({{key}})",
                        f"rename {{name}} to match {{targets}}, or move it to the part whose kind of {fact} it is"),),
                keep=_all(*kept, "public"), exempt=_all(*exempt), key=f"parts.{part}.holds.{kind}.names")


def _no_callbacks(profile: Profile) -> tuple[Rule, ...]:
    """Code of a part the guard no-callbacks lists calls none of its own parameters annotated as callables; the first
    parameter of a method, the object it is called on, is no callback."""
    return tuple(Rule("no-callbacks", Scope(APP, part), ("callback",), MAY_NOT, EXISTING,
                      (Saying("{function} calls its parameter {name}: {where} takes no callback ({key})",
                              "have the caller call {name} first and pass {function} the answer as a value"),),
                      keep=_all("annotated-callable"), exempt=_all("receiver"), key="guards.no-callbacks")
                 for part in profile.no_callbacks)


def _no_comments(profile: Profile) -> tuple[Rule, ...]:
    """No comment, in the app or its tests, but doc comments and those the language's tools read: its directives, a
    shebang on line 1, an encoding declaration on line 1 or 2."""
    if not profile.no_comments:
        return ()
    return (Rule("no-comments", Scope(ALL), ("comment",), MAY_NOT, EXISTING,
                 (Saying("a comment (no-comments)", "say it in a docstring or a name, and delete the comment"),),
                 exempt=_all("directive", "doc"), key="guards.no-comments"),)


def _closed_tree(profile: Profile) -> tuple[Rule, ...]:
    """Every source file of the app lies in a part, or is a package file of a folder of the layout."""
    if not profile.closed_tree:
        return ()
    return (Rule("closed-tree", Scope(APP, where=_all("not placed")), ("file",), MAY_NOT, EXISTING,
                 (Saying("lies in no part and no folder of the layout (closed-tree)",
                         "move {file} into the part that fits it (run xarch where {file}), or add its folder to the "
                         "layout"),), key="guards.closed-tree"),)


def _holds(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part that lists `holds` defines at the top level only the kinds it lists, listed without failing:
    no public function when it does not list functions; no class (a private one too) when it does not list classes,
    but one a narrower kind it lists fits, an exception or a record, each said as the narrowest kind it fits. In a
    language whose reader does not supply whether a function is at the top level, no part is held to its functions. A
    package file only gathers what its package holds and is not read."""
    found = []
    for part, kinds in profile.holds.items():
        key, held, within = f"parts.{part}.holds", _listed(kinds), Scope(APP, part, where=_all("not package-file"))
        if "functions" not in kinds and _top_level(profile):
            found.append(Rule("holds", within, ("function",), MAY_NOT, EXISTING,
                              (Saying(f"{{name}} is a function at the top level, but {{where}} holds {held} ({{key}})",
                                      "make {name} a method of the class whose rule it is, or move it to "
                                      "{parts_holding_functions}"),),
                              keep=_all("top-level", "public"), mode=LIST, key=key))
        if "classes" not in kinds:
            fix = "move {name} to {parts_holding_classes}, or make what it does functions"
            sayings = tuple(Saying(f"{{name}} is {called}, but {{where}} holds {held} ({{key}})", fix, _all(trait))
                            for kind, trait, called in _UNLISTED if kind not in kinds)
            found.append(Rule("holds", within, ("class",), MAY_NOT, EXISTING,
                              (*sayings, Saying(f"{{name}} is a class, but {{where}} holds {held} ({{key}})", fix)),
                              exempt=_all(*(trait for kind, trait in _NARROWER if kind in kinds)), mode=LIST, key=key))
    return tuple(found)


_UNLISTED = (("exceptions", "exception", "an exception"), ("records", "record", "a record"))
"""How the class a part's `holds` does not allow is said when it is of a narrower kind the part does not list,
narrowest first."""


def _listed(kinds: tuple[str, ...]) -> str:
    """The kinds a part's `holds` lists, joined as the docs join names."""
    return kinds[0] if len(kinds) == 1 else f"{', '.join(kinds[:-1])} and {kinds[-1]}"


def _top_level(profile: Profile) -> bool:
    """Whether the language's reader says which functions are at the top level: a data file that does not grade the
    facts it supplies is read as supplying it."""
    supplies = profile.language.supplies
    return supplies is None or any(supply.fact == "function.top_level" for supply in supplies)


def _immutable(profile: Profile) -> tuple[Rule, ...]:
    """Every class a file of a part defines at the top level and holds to a kind whose `immutable` it sets is an
    immutable record, as the language's data file says one is made, listed without failing: for classes, every class
    but an exception and one a narrower kind listed beside them holds; for records, every record but an exception,
    when exceptions are listed. A package file only gathers what its package holds and is not read."""
    found = []
    for part, kinds in profile.holds_immutable.items():
        within = Scope(APP, part, where=_all("not package-file"))
        fix = ("make {name} an immutable record (the {language} data file's `immutable` says how), or move it to "
               "{parts_holding_classes}")
        if "classes" in kinds:
            exempt = ("exception", *(trait for trait in _narrower(profile, part) if trait != "exception"), "immutable")
            found.append(Rule("immutable", within, ("class",), MAY_NOT, EXISTING,
                              (Saying("{name} is a class that is no immutable record, but every class of {where} is "
                                      "one ({key})", fix),),
                              exempt=_all(*exempt), mode=LIST, key=f"parts.{part}.holds.classes.immutable"))
        if "records" in kinds:
            exempt = ("exception",) if "exceptions" in profile.holds.get(part, ()) else ()
            found.append(Rule("immutable", within, ("class",), MAY_NOT, EXISTING,
                              (Saying("{name} is a record that is not immutable, but every record of {where} is one "
                                      "({key})", fix),),
                              keep=_all("record"), exempt=_all(*exempt, "immutable"), mode=LIST,
                              key=f"parts.{part}.holds.records.immutable"))
    return tuple(found)


def _must_import(profile: Profile) -> tuple[Rule, ...]:
    """Each file of a part that lists `imports.must` imports one of the targets or an outside package, itself or
    through the files of its own part and instance it imports, however far; a package file and a file with no real
    statement are not said."""
    return tuple(Rule("must-import", Scope(APP, part), ("import", "import-into-app"), MUST_REACH,
                      (Match("place", places=wanted), Match("outside")),
                      (Saying("{where} imports nothing from {targets} and no outside package, though each of its "
                              "files must ({key})",
                              "import what it works with from {targets}, or an outside package, or move its code to a "
                              "part that need not"),),
                      exempt=_all("package-file", "no-statements"), key=f"parts.{part}.imports.must",
                      links=("import-into-app",), via=_all("target-in-own-part"))
                 for part, wanted in profile.imports_must.items())


def _must_import_tiers(profile: Profile) -> tuple[Rule, ...]:
    """Each test file of a tier that lists `imports.must` reaches one of the parts, in any instance, by an import into
    the app or through test code it imports that is no test file, however far; one with no real statement is not
    said."""
    return tuple(Rule("must-import", Scope(TESTS, tier=tier.name, where=_all("test")), ("import-into-app",),
                      MUST_REACH, (Match("part", words=tier.imports_must),),
                      (Saying("a test of the {tier} tier imports nothing from {targets}, directly or through test code it imports "
                              "({key})",
                              "drive what it proves through {targets}, or move it to the tier of the part it calls "
                              "directly"),),
                      keep=_all("target-placed"), exempt=_all("no-statements"), key=f"tiers.{tier.name}.imports.must",
                      links=("import-into-tests",), via=_all("not target-test"))
                 for tier in profile.tiers if tier.imports_must)


def _dead_code(profile: Profile) -> tuple[Rule, ...]:
    """A port that no other file of the app names, by any name it reads, but a package file and a part that may
    import everything; and a fake that no test outside the fakes' folder names, nor a fake named so, however far."""
    if not profile.dead_code or profile.fakes is None:
        return ()
    folder, prefix = "/".join(profile.fakes.folder), profile.fakes.prefix
    ports = [Rule("dead-code", Scope(APP, part), ("class",), MUST_BE_REACHED, EXISTING,
                  (Saying("{name} is a port that nothing else in the app names (dead-code)",
                          "delete {name} and its fake, or add the code that uses it"),),
                  keep=_all("interface"), links=("names-mentioned",),
                  roots=Scope(APP, where=_all("not package-file", "not may-import-everything")), elsewhere=True,
                  key="guards.dead-code")
             for part in profile.fakes.stand_in_for]
    fakes = Rule("dead-code", Scope(TESTS, where=_all(f"below {folder}")), ("class",), MUST_BE_REACHED, EXISTING,
                 (Saying("{name} is a fake that no test names (dead-code)",
                         "delete {name}, or write the test that uses it"),),
                 keep=_all(f"named {prefix}*"), exempt=_all(f"named {prefix}") if prefix else (), links=("names-mentioned",),
                 roots=Scope(TESTS, where=_all(f"not below {folder}")), spread=("class",), key="guards.dead-code")
    return (*ports, fakes)


def _untested(profile: Profile) -> tuple[Rule, ...]:
    """A file of a part a tier tests that no test code of that tier reaches, by an import, or through files of parts
    of that same tier, however far; listed. A package file, a file with no real statement and a file of exceptions
    only are not."""
    if not profile.dead_code or not profile.untested:
        return ()
    return (Rule("dead-code", Scope(APP, where=_all("tiered")), ("file",), MUST_BE_REACHED, EXISTING,
                 (Saying("a file of {where} that no {tier} test reaches (guards.dead-code.untested)",
                         "write its {tier} test in {tests_folder}/, or delete what nothing uses"),),
                 exempt=_all("package-file", "exceptions-only", "no-statements"), mode=LIST, links=("import-into-app",),
                 via=_all("target-in-own-tier"), roots=Scope(TESTS, where=_all("tiered")),
                 spread=("import-into-app",), key="guards.dead-code.untested"),)


def _tests_only(profile: Profile) -> tuple[Rule, ...]:
    """A public class or top-level function a file of the app defines that no other file of the app names, by its last
    step, a package file aside, which only gathers what its package holds: only the tests, or nothing, use it;
    listed."""
    if not profile.dead_code or not profile.tests_only:
        return ()
    said = (Saying("{name} is public, but no other file of the app names it: only the tests, or nothing, use it "
                   "(guards.dead-code.tests_only)",
                   "delete {name} and what tests it alone, or make it private when its own file uses it, or use it "
                   "where the app needs it"),)
    return tuple(Rule("dead-code", Scope(APP), (kind,), MUST_BE_REACHED, EXISTING, said, keep=_all("public", *kept),
                      mode=LIST, links=("names-mentioned",), roots=Scope(APP, where=_all("not package-file")),
                      elsewhere=True, key="guards.dead-code.tests_only")
                 for kind, kept in (("class", ("not exception",)), ("function", ("top-level",))))


def _pass_through(profile: Profile) -> tuple[Rule, ...]:
    """A method of a listed part that only forwards to one call, listed without failing."""
    keep = "it stays listed and fails only `check --strict`"
    return tuple(Rule("pass-through", Scope(APP, part), ("function",), MAY_NOT, EXISTING,
                      (Saying("{qualified_name} only passes its arguments on to {forwarded} and returns its .{returned}",
                              f"have the caller use {{forwarded}}(...).{{returned}}, or keep it as a deliberate plain "
                              f"forward: {keep}", _all("returns-an-attribute")),
                       Saying("{qualified_name} only passes its arguments on to {forwarded}",
                              f"have the caller use {{forwarded}}, or keep it as a deliberate plain forward: {keep}")),
                      keep=_all("forwards"), mode=LIST, key="guards.pass-through")
                 for part in profile.pass_through)


KEYS = ("parts.imports.may", "parts.imports.libraries", "parts.uses.never", "tiers.uses.apply_never", "tiers",
        "tiers.imports.also", "tiers.imports.types_only",
        "parts.package_only", "parts.imports.may.types_only", "guards.no-callbacks", "parts.holds.classes.names",
        "parts.holds.functions.names", "parts.holds.records.names", "parts.holds.exceptions.names",
        "parts.holds.classes.built_by", "guards.private-imports", "guards.no-comments", "guards.closed-tree",
        "parts.holds", "parts.holds.classes.immutable", "parts.holds.records.immutable",
        "parts.imports.must", "tiers.imports.must", "guards.dead-code", "guards.dead-code.untested",
        "guards.dead-code.tests_only", "guards.pass-through")
"""The keys the rules of the book are keyed by, each with any part or tier left out (see explained.general), in the
order of the book: a key the engine expands to rules when a profile sets it."""


def book(profile: Profile) -> dict[str, tuple[Rule, ...]]:
    """Every check the engine runs, by the name of its group, each the rules its keys expand to."""
    return {"syntax": _syntax(profile), "may-import": _rules(profile), "libraries": _libraries(profile),
            "never-use": _never_use(profile), "tiers": _tiers(profile), "types-only tiers": _types_only_tiers(profile),
            "package-only": _package_only(profile), "types-only parts": _types_only_parts(profile),
            "no-callbacks": _no_callbacks(profile), "names": _names(profile), "built-by": _built_by(profile),
            "private-imports": _private_imports(profile), "no-comments": _no_comments(profile),
            "closed-tree": _closed_tree(profile), "holds": _holds(profile), "immutable": _immutable(profile),
            "must-import": _must_import(profile),
            "must-import tiers": _must_import_tiers(profile), "dead-code": _dead_code(profile),
            "untested": _untested(profile), "tests-only": _tests_only(profile), "pass-through": _pass_through(profile)}
