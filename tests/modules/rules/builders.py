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

from xarch.kernel.logic.names import outside_steps
from xarch.kernel.placement import EVERYTHING
from xarch.kernel.source import Import
from xarch.modules.rules.domain.parsed import SourceFile
from xarch.modules.rules.domain.profile import Profile
from xarch.profile_values.language import CheckedLanguage, InterfaceMark, RecordMark
from xarch.profile_values.placement import Repeat, Target
from xarch.profile_values.testing import CaseTable, Fakes, Fixture, Framework, ScenarioCoverage, StandIns
from xarch.profile_values.tiers import CheckedTier


def marks_of(file: dict) -> tuple[InterfaceMark, ...]:
    """The interface marks a language's data file writes, as its loader reads them: a base split at the file's member,
    a keyword whole."""
    return tuple(InterfaceMark(outside_steps(mark["base"], file["member"])) if "base" in mark
                 else InterfaceMark(keyword=mark["keyword"]) for mark in file.get("interface", ()))


PYTHON_FILE = yaml.safe_load(resources.files("xarch").joinpath("architectures", "presets", "language", "python.yaml")
                             .read_text(encoding="utf-8"))
PYTHON = CheckedLanguage(title="Python", extension=".py", package_file="__init__.py",
                         interface=marks_of(PYTHON_FILE),
                         dynamic=(("importlib", "import_module"), ("importlib", "__import__"), ("builtins", "__import__")),
                         private="_", special=PYTHON_FILE["special"], call="__call__",
                         nothing=tuple(PYTHON_FILE["nothing"]), comment="#", directives=("type: ignore", "noqa", "pragma:"), shebang="#!",
                         encoding=r"coding[:=][ \t]*[-\w.]+", branching=("if", "match", "try", "for", "while"),
                         immutable=(RecordMark(("typing", "NamedTuple")),
                                    RecordMark(("dataclasses", "dataclass"), (("frozen", "True"),))),
                         branching_expressions=("if",), names=PYTHON_FILE["name"], package=PYTHON_FILE["package"],
                         member=PYTHON_FILE["member"], standard_modules=frozenset(sys.stdlib_module_names))
"""Python as its data file says it, for the checks that read the tokens of its code; the patterns of a name and of a
package, and the member that joins them, read from it; its standard modules the interpreter's, as spec hands them."""
BRACE_FILE = yaml.safe_load((Path(__file__).resolve().parents[2] / "fakes" / "languages" / "brace.yaml")
                            .read_text(encoding="utf-8"))
BRACE = CheckedLanguage(title=BRACE_FILE["title"], extension=BRACE_FILE["extension"],
                        package_file=BRACE_FILE["package_file"], interface=marks_of(BRACE_FILE),
                        dynamic=(("node:module", "createRequire"),), nothing=tuple(BRACE_FILE["nothing"]),
                        names=BRACE_FILE["name"], package=BRACE_FILE["package"], member=BRACE_FILE["member"],
                        standard_modules=frozenset(BRACE_FILE["standard"]["modules"]))
"""The TypeScript-like test-only language as a check reads it, its patterns, member, interface marks, annotations of
no value and standard modules read from its data file."""
PERCENT_FILE = yaml.safe_load((Path(__file__).resolve().parents[2] / "fakes" / "languages" / "percent.yaml")
                              .read_text(encoding="utf-8"))
PERCENT = CheckedLanguage(title=PERCENT_FILE["title"], extension=PERCENT_FILE["extension"],
                          package_file=PERCENT_FILE["package_file"], interface=marks_of(PERCENT_FILE),
                          special=PERCENT_FILE["special"], unannotated=PERCENT_FILE["unannotated"],
                          names=PERCENT_FILE["name"], package=PERCENT_FILE["package"], member=PERCENT_FILE["member"])
"""The ObjectScript-like test-only language as a check reads it: its interface marks, the pattern of a special name and
its word on a method with no annotation read from its data file."""
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
RENDERING = CheckedTier("rendering", (Target("web"),), ("web",), types_only=("controller",))
GUARD = CheckedTier("guard", (), ("architecture",))
NOW = ("datetime", "datetime", "now")
MOCK = ("unittest", "mock", "Mock")
AUTOSPEC = ("unittest", "mock", "create_autospec")
TABLE = CaseTable(("pytest", "mark", "parametrize"), ("pytest", "param"), "id", ("argnames", "argvalues"))
PROFILE = Profile(
    parts=PARTS, rules=RULES, folders=FOLDERS, tiers=(UNIT, INTEGRATION, RENDERING, GUARD),
    libraries={"platform": ("sqlmodel",), "adapters": ("sqlmodel",), "web": ("fastapi",),
               "bootstrap": ("sqlmodel", "fastapi")},
    fakes=Fakes(("fakes",), ("ports",), "Fake"), repeats=(MODULES,), package_only=("contract",),
    scenarios=ScenarioCoverage("contract", "integration", "Result", ("given", "when", "then"), TABLE, "test_{name}.py"),
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


def imp(line: int, module: str, *names: str, up: int | None = None, language: CheckedLanguage = PYTHON) -> Import:
    """`import module` with no names, `from module import names` with some; up, for a relative import, how many
    folders above the importing file's own it climbs. It is marked standard, and written, as the reader marks it when
    handed the standard modules of language (Python unless given): absolute and its first step one of them; the
    module with one dot more than up before it."""
    steps = dotted(module) if module else ()
    relative = up is not None
    return Import(line, steps, names or None, relative, up or 0,
                  not relative and bool(steps) and steps[0] in language.standard_modules,
                  "." * ((up or 0) + 1) + module if relative else module)


def source(path: str, *imports: Import, root: str = APP, **fields) -> SourceFile:
    """A file at path below root, shown as root/path, with its imports and any other field of a SourceFile."""
    return SourceFile(f"{root}/{path}", steps(path), imports, **fields)


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
