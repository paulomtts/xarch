"""Builders for the rules module's unit tests: a hand-made profile shaped like the bundled web profile, and source
files written as the parser would hand them over, each argument defaulted so a test names only what it cares about.

PROFILE's app is the package `app`, its tests the package `tests`; its repeating folder is modules/<module>/, holding
domain/, contract/, application/{controller.py, services/, logic/, ports/} and adapters/, beside kernel/, platform/,
web/ (the entry) and bootstrap/. Its tiers are unit (kernel, domain, logic, adapters; held to `forbidden`),
integration (controller, services, ports, contract), rendering (web; the controller as a type only) and guard (by
its folder, architecture/).
"""
from __future__ import annotations

import sys
from dataclasses import replace

from xarch.kernel.logic.language import LanguageView
from xarch.kernel.logic.placement import EVERYTHING, Repeat, Target
from xarch.kernel.logic.source import Import
from xarch.kernel.logic.testing import CaseTable, Fakes, Fixture, Framework, ScenarioCoverage, StandIns, TierView
from xarch.modules.rules.domain.values import Profile, SourceFile

PYTHON = LanguageView("Python", ".py", "__init__.py", (("typing", "Protocol"), ("typing_extensions", "Protocol")),
                      (("importlib", "import_module"), ("importlib", "__import__"), ("builtins", "__import__")),
                      "_", "__", "__call__", "None", "#", ("type: ignore", "noqa", "pragma:"), "#!",
                      r"coding[:=][ \t]*[-\w.]+", ("if", "match", "try", "for", "while"))
"""Python as its data file says it, for the checks that read the tokens of its code."""
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
UNIT = TierView("unit", (Target("kernel"), *own("domain", "logic", "adapters")), ("modules", "docs", "domain"),
                forbidden=True)
INTEGRATION = TierView("integration", own("controller", "services", "ports", "contract"),
                       ("modules", "docs", "application"))
RENDERING = TierView("rendering", (Target("web"),), ("web",), types_only=("controller",))
GUARD = TierView("guard", (), ("architecture",))
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
                       (Fixture("mocker", ("Mock", "MagicMock"), ("create_autospec",)),)),
    framework=Framework(("test_*.py", "*_test.py"), "test_*"),
    forbidden={"domain": (NOW, ("builtins", "open"), ("socket",))}, language=PYTHON)


PLUGINS = Repeat("plugin", ("plugins",))
PLUGIN_PARTS = {"hooks": ("plugins", "*", "hooks"), "manifest": ("plugins", "*", "manifest.py")}
PLUGIN = TierView("plugin", own("hooks", "manifest"), None)
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


def imp(line: int, module: str, *names: str, up: int | None = None) -> Import:
    """`import module` with no names, `from module import names` with some; up, for a relative import, how many
    folders above the importing file's own it climbs. It is marked standard, and written, as the Python reader marks
    it: absolute and a module of the standard library; the module with one dot more than up before it."""
    steps = dotted(module) if module else ()
    relative = up is not None
    return Import(line, steps, names or None, relative, up or 0,
                  not relative and bool(steps) and steps[0] in sys.stdlib_module_names,
                  "." * ((up or 0) + 1) + module if relative else module)


def source(path: str, *imports: Import, root: str = APP, **fields) -> SourceFile:
    """A file at path below root, shown as root/path, with its imports and any other field of a SourceFile."""
    return SourceFile(f"{root}/{path}", steps(path), imports, **fields)


def in_tests(path: str, *imports: Import, **fields) -> SourceFile:
    """A file at path below the tests root."""
    return source(path, *imports, root=TESTS, **fields)

