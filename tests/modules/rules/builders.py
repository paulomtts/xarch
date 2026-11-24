"""Builders for the rules module's unit tests: a hand-made profile shaped like the bundled web profile, and source
files written as the parser would hand them over, each argument defaulted so a test names only what it cares about.

PROFILE's app is the package `app`, its tests the package `tests`; its repeating folder is modules/<module>/, holding
domain/, contract/, application/{controller.py, services/, logic/, ports/} and adapters/, beside kernel/, platform/,
web/ (the entry) and bootstrap/. Its tiers are unit (kernel, domain, logic, adapters; held to `uses.never`),
integration (controller, services, ports, contract), rendering (web; the controller as a type only) and guard (by
its folder, architecture/).
"""
from __future__ import annotations

import sys
from dataclasses import replace
from importlib import resources
from pathlib import Path

import yaml

from xarch.kernel.logic.names import is_private_name, outside_steps
from xarch.kernel.placement import EVERYTHING
from xarch.kernel.source import Import
from xarch.modules.rules.domain.parsed import Class, SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.profile_values.language import LINE, CheckedLanguage, CommentForm, InterfaceMark, RecordMark, Writing
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import CaseTable, Fakes, Fixture, Framework, ScenarioCoverage, StandIns
from xarch.profile_values.tiers import CheckedTier


def marks_of(file: dict) -> tuple[InterfaceMark, ...]:
    """The interface marks a language's data file writes, as its loader reads them: a base split at the file's member,
    a keyword whole."""
    return tuple(InterfaceMark(outside_steps(mark["base"], file["member"])) if "base" in mark
                 else InterfaceMark(keyword=mark["keyword"]) for mark in file.get("interface", ()))


def forms_of(file: dict) -> tuple[CommentForm, ...]:
    """The comment forms a language's data file writes, as its loader reads them: a line form's marker alone, a block
    form's or a doc form's opening and closing."""
    return tuple(CommentForm(kind, value) if kind == LINE else CommentForm(kind, *value)
                 for form in file.get("comments", ()) for kind, value in form.items())


def records_of(file: dict) -> tuple[RecordMark, ...]:
    """The marks of an immutable record a language's data file writes, as its loader reads them: a base, a decorator
    or a type split at the file's member, a decorator's keywords in the order written, a fields word whole."""
    return tuple(_record_mark(mark, file["member"]) for mark in file.get("immutable", ()))


def _record_mark(mark: dict, member: str) -> RecordMark:
    if "base" in mark:
        return RecordMark(base=outside_steps(mark["base"], member))
    if "decorator" in mark:
        return RecordMark(decorator=outside_steps(mark["decorator"], member),
                          keywords=tuple(mark.get("keywords", {}).items()))
    if "type" in mark:
        return RecordMark(type=outside_steps(mark["type"], member))
    return RecordMark(fields=mark["fields"])


PYTHON_FILE = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                             .read_text(encoding="utf-8"))
PYTHON = CheckedLanguage(title="Python", extensions=(".py",), package_files=("__init__.py",),
                         interface=marks_of(PYTHON_FILE),
                         dynamic=(("importlib", "import_module"), ("importlib", "__import__"), ("builtins", "__import__")),
                         private="_", special=PYTHON_FILE["special"], call="__call__",
                         nothing=tuple(PYTHON_FILE["nothing"]), comments=forms_of(PYTHON_FILE),
                         directives=("type: ignore", "noqa", "pragma:"), shebang="#!",
                         encoding=r"coding[:=][ \t]*[-\w.]+", branching=("if", "match", "try", "for", "while"),
                         immutable=(RecordMark(base=("typing", "NamedTuple")),
                                    RecordMark(decorator=("dataclasses", "dataclass"), keywords=(("frozen", "True"),))),
                         branching_expressions=("if",), names=PYTHON_FILE["name"], package=PYTHON_FILE["package"],
                         member=PYTHON_FILE["member"], writing=Writing(**PYTHON_FILE["writing"]),
                         standard_modules=frozenset(sys.stdlib_module_names))
"""Python as its data file says it, for the checks that read the tokens of its code; the patterns of a name and of a
package, and the member that joins them, read from it; its standard modules the interpreter's, as spec hands them;
how it writes a row of a table, read from it."""
BRACE_FILE = yaml.safe_load((Path(__file__).resolve().parents[2] / "fakes" / "languages" / "brace.yaml")
                            .read_text(encoding="utf-8"))
BRACE = CheckedLanguage(title=BRACE_FILE["title"], extensions=tuple(BRACE_FILE["extensions"]),
                        package_files=tuple(BRACE_FILE["package_files"]), interface=marks_of(BRACE_FILE),
                        immutable=records_of(BRACE_FILE),
                        dynamic=(("node:module", "createRequire"),), nothing=tuple(BRACE_FILE["nothing"]),
                        comments=forms_of(BRACE_FILE), directives=tuple(BRACE_FILE["directives"]),
                        names=BRACE_FILE["name"], package=BRACE_FILE["package"], member=BRACE_FILE["member"],
                        standard_modules=frozenset(BRACE_FILE["standard"]["modules"]))
"""The TypeScript-like test-only language as a check reads it, its endings, package files, patterns, member, interface
marks, marks of an immutable record, annotations of no value, comment forms, directives and standard modules read from
its data file."""
PERCENT_FILE = yaml.safe_load((Path(__file__).resolve().parents[2] / "fakes" / "languages" / "percent.yaml")
                              .read_text(encoding="utf-8"))
PERCENT = CheckedLanguage(title=PERCENT_FILE["title"], extensions=tuple(PERCENT_FILE["extensions"]),
                          interface=marks_of(PERCENT_FILE), comments=forms_of(PERCENT_FILE),
                          special=PERCENT_FILE["special"], unannotated=PERCENT_FILE["unannotated"],
                          names=PERCENT_FILE["name"], package=PERCENT_FILE["package"], member=PERCENT_FILE["member"])
"""The ObjectScript-like test-only language as a check reads it: its interface marks, its comment forms (two line
markers among them), the pattern of a special name and its word on a method with no annotation read from its data
file."""
APP, TESTS = "app", "tests"
MODULES = Repeat("module", ("modules",))
EACH_PARTS = {"domain": ("domain",), "contract": ("contract",), "controller": ("application", "controller.py"),
              "services": ("application", "services"), "logic": ("application", "logic"),
              "ports": ("application", "ports"), "adapters": ("adapters",)}
PARTS = {"kernel": ("kernel",), **{name: ("modules", "*", *sub) for name, sub in EACH_PARTS.items()},
         "platform": ("platform",), "web": ("web",), "bootstrap": ("bootstrap",)}


def own(*parts: str) -> tuple[Target, ...]:
    return tuple(Target(p, "own") for p in parts)


RULES = {
    "kernel": (),
    "domain": (Target("kernel"),),
    "contract": (Target("domain", "own", ("values",)), Target("kernel")),
    "controller": (*own("services", "logic", "domain", "ports", "contract"), Target("kernel")),
    "services": (*own("logic", "domain", "ports", "contract"), Target("kernel")),
    "logic": (*own("domain"), Target("kernel")),
    "ports": (*own("domain"), Target("kernel")),
    "adapters": (*own("ports", "domain"), Target("kernel"), Target("platform"), Target("contract", "any")),
    "platform": (Target("kernel"),),
    "web": (Target("controller", "any"), Target("contract", "any"), Target("kernel")),
    "bootstrap": (Target(EVERYTHING),),
}
FOLDERS = ((), ("bootstrap",), ("kernel",), ("kernel", "logic"), ("modules",), ("modules", "*"),
           *(("modules", "*", *sub) for sub in [("contract",), ("domain",), ("application",),
                                                  ("application", "services"), ("application", "logic"),
                                                  ("application", "ports"), ("adapters",)]),
           ("platform",), ("web",), ("web", "routes"))
UNIT = CheckedTier("unit", (Target("kernel"), *own("domain", "logic", "adapters")), ("modules", "docs", "domain"),
                apply_never=True)
INTEGRATION = CheckedTier("integration", own("controller", "services", "ports", "contract"),
                       ("modules", "docs", "application"))
RENDERING = CheckedTier("rendering", (Target("web"),), ("web",), imports_types_only=("controller",))
GUARD = CheckedTier("guard", (), ("architecture",))
NOW = ("datetime", "datetime", "now")
MOCK = ("unittest", "mock", "Mock")
AUTOSPEC = ("unittest", "mock", "create_autospec")
TABLE = CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id", ("argnames", "argvalues"))
PROFILE = Profile(
    parts=PARTS, rules=RULES, folders=FOLDERS, tiers=(UNIT, INTEGRATION, RENDERING, GUARD),
    imports_libraries={"platform": ("sqlmodel",), "adapters": ("sqlmodel",), "web": ("fastapi",),
                       "bootstrap": ("sqlmodel", "fastapi")},
    fakes=Fakes(("fakes",), ("ports",), "Fake"), repeats=(MODULES,), package_only=("contract",),
    scenarios=ScenarioCoverage("contract", "integration", "Result", ("given", "when", "then"), TABLE, "test_{name:snake}.py"),
    no_comments=True,
    stand_ins=StandIns((MOCK, ("unittest", "mock", "MagicMock")), (AUTOSPEC,), ("spec", "spec_set"),
                       (Fixture("mocker", ("Mock", "MagicMock"), ("create_autospec",)),), 0),
    framework=Framework(("test_*.py", "*_test.py"), "test_*"),
    uses_never={"domain": (NOW, ("builtins", "open"), ("socket",))}, language=PYTHON, default_tests="tests")


PLUGINS = Repeat("plugin", ("plugins",))
PLUGIN_PARTS = {"hooks": ("plugins", "*", "hooks"), "manifest": ("plugins", "*", "manifest.py")}
PLUGIN = CheckedTier("plugin", own("hooks", "manifest"), None)
TWO = replace(
    PROFILE, parts={**PARTS, **PLUGIN_PARTS},
    rules={**RULES, "hooks": (*own("manifest"), Target("domain", "any"), Target("kernel")),
           "manifest": (Target("kernel"),), "domain": (Target("kernel"), Target("hooks", "any"))},
    folders=(*FOLDERS, ("plugins",), ("plugins", "*"), ("plugins", "*", "hooks")),
    tiers=(UNIT, PLUGIN, INTEGRATION, RENDERING, GUARD), repeats=(MODULES, PLUGINS))
"""PROFILE with a second repeating folder, plugins/<plugin>/, holding hooks/ and manifest.py: a plugin's hooks may
import its own manifest, any module's domain and the kernel; a module's domain may import any plugin's hooks."""


def profile(**changes) -> Profile:
    """PROFILE with the given fields changed."""
    return replace(PROFILE, **changes)


def steps(path: str) -> tuple[str, ...]:
    return tuple(path.split("/"))


def dotted(name: str) -> tuple[str, ...]:
    return tuple(name.split("."))


def imp(line: int, module: str, *names: str, up: int | None = None, language: CheckedLanguage = PYTHON,
        withheld: tuple[str, ...] = ()) -> Import:
    """`import module` with no names, `from module import names` with some; up, for a relative import, how many
    folders above the importing file's own it climbs. It is marked standard, and written, as the reader marks it when
    handed the standard modules of language (Python unless given): absolute and its first step one of them; the
    module with one dot more than up before it. It withholds, as that reader would, each name that starts as a
    private name of language does, and the names withheld lists besides."""
    steps = dotted(module) if module else ()
    relative = up is not None
    hidden = frozenset(withheld) | frozenset(name for name in names if is_private_name(name, language.private))
    return Import(line, steps, names or None, relative, up or 0,
                  not relative and bool(steps) and steps[0] in language.standard_modules,
                  "." * ((up or 0) + 1) + module if relative else module, withheld=hidden)


def _public(name: str, given: bool, language: CheckedLanguage) -> bool:
    return given and not is_private_name(name, language.private)


def _record(cls: Class, file: SourceFile, language: CheckedLanguage) -> bool:
    return cls.record or (language.title == PYTHON.title and all(language.is_special(m.name) for m in cls.methods)
                          and any(cls.name in f.returns_named for f in file.functions if not f.owner))


def read_as(file: SourceFile, language: CheckedLanguage) -> SourceFile:
    """The file with each class, function and constant whose name starts as a private name of language does made not
    public, as its reader would say, one given as not public staying so; and, under Python, each class its reader would
    call a record made one (every method special by language's pattern, and a function of the file's top level naming
    it in its return annotation), one given as a record staying so. Under another language a class is a record only as
    given."""
    return replace(file, classes=tuple(replace(c, public=_public(c.name, c.public, language),
                                               record=_record(c, file, language)) for c in file.classes),
                   functions=tuple(replace(f, public=_public(f.name, f.public, language)) for f in file.functions),
                   constants=tuple(replace(c, public=_public(c.name, c.public, language)) for c in file.constants))


def source(path: str, *imports: Import, root: str = APP, language: CheckedLanguage = PYTHON, **fields) -> SourceFile:
    """A file at path below root, shown as root/path, with its imports and any other field of a SourceFile, each of its
    definitions public or not as the reader of language would say (Python unless given; see read_as)."""
    return read_as(SourceFile(f"{root}/{path}", steps(path), imports, **fields), language)


def in_tests(path: str, *imports: Import, **fields) -> SourceFile:
    """A file at path below the tests root."""
    return source(path, *imports, root=TESTS, **fields)


def aliased(line: int, written: str, module: str, *names: str) -> Import:
    """An import written by an alias the project maps, such as `@app/domain/order`, that the reader resolved to module
    from the top: absolute, as the reader hands it over, with the module as the source writes it."""
    return Import(line, dotted(module), names or None, written=written)


def unresolved(line: int, written: str, *names: str) -> Import:
    """An import naming a place of the app the reader found no file or folder for, as the Python reader hands over a
    relative one it cannot follow: no module, relative, climbing none, marked unresolved, as written."""
    return Import(line, (), names or None, True, 0, written=written, unresolved=True)
