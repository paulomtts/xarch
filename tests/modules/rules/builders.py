"""Builders for the rules module's unit tests: a hand-made profile shaped like the bundled web profile, and source
files written as the parser would hand them over, each argument defaulted so a test names only what it cares about.

PROFILE's app is the package `app`, its tests the package `tests`; its `each` folder is modules/<module>/, holding
domain/, contract/, application/{controller.py, services/, logic/, ports/} and adapters/, beside kernel/, platform/,
web/ (the entry) and bootstrap/. Its tiers are unit (kernel, domain, logic, adapters; held to `forbidden`),
integration (controller, services, ports, contract), rendering (web; the controller as a type only) and guard (by
its example folder, architecture/).
"""
from __future__ import annotations

from dataclasses import replace

from xarch.kernel.logic.placement import EVERYTHING, Target
from xarch.modules.rules.domain.values import (
    Fakes,
    Framework,
    Import,
    Profile,
    Scenarios,
    SourceFile,
    StandIns,
    TableForm,
    TestTier,
)

APP, TESTS = "app", "tests"
EACH_PARTS = {"domain": ("domain",), "contract": ("contract",), "controller": ("application", "controller.py"),
              "services": ("application", "services"), "logic": ("application", "logic"),
              "ports": ("application", "ports"), "adapters": ("adapters",)}
PARTS = {"kernel": ("kernel",), **{name: ("modules", "*", *sub) for name, sub in EACH_PARTS.items()},
         "platform": ("platform",), "web": ("web",), "bootstrap": ("bootstrap",)}


def own(*parts: str) -> tuple[Target, ...]:
    return tuple(Target(p, "own") for p in parts)


RULES = {
    "kernel": (Target("kernel"),),
    "domain": (*own("domain"), Target("kernel")),
    "contract": (*own("contract"), Target("domain", "own", ("values",)), Target("kernel")),
    "controller": (*own("controller", "services", "logic", "domain", "ports", "contract"), Target("kernel")),
    "services": (*own("services", "logic", "domain", "ports", "contract"), Target("kernel")),
    "logic": (*own("logic", "domain"), Target("kernel")),
    "ports": (*own("ports", "domain"), Target("kernel")),
    "adapters": (*own("adapters", "ports", "domain"), Target("kernel"), Target("platform"), Target("contract", "any")),
    "platform": (Target("platform"), Target("kernel")),
    "web": (Target("web"), Target("controller", "any"), Target("contract", "any"), Target("kernel")),
    "bootstrap": (Target(EVERYTHING),),
}
FOLDERS = ((), ("bootstrap",), ("kernel",), ("kernel", "logic"), ("modules",), ("modules", "*"),
           *(("modules", "*", *sub) for sub in [("contract",), ("domain",), ("application",),
                                                  ("application", "services"), ("application", "logic"),
                                                  ("application", "ports"), ("adapters",)]),
           ("platform",), ("web",), ("web", "routes"))
UNIT = TestTier("unit", (Target("kernel"), *own("domain", "logic", "adapters")), ("modules", "docs", "domain"),
                forbidden=True)
INTEGRATION = TestTier("integration", own("controller", "services", "ports", "contract"),
                       ("modules", "docs", "application"))
RENDERING = TestTier("rendering", (Target("web"),), ("web",), types_only=("controller",))
GUARD = TestTier("guard", (), ("architecture",))
NOW = ("datetime", "datetime", "now")
MOCK = ("unittest", "mock", "Mock")
AUTOSPEC = ("unittest", "mock", "create_autospec")
TABLE = TableForm(("pytest", "mark", "parametrize"), ("pytest", "param"), "id", ("argnames", "argvalues"))
PROFILE = Profile(
    parts=PARTS, rules=RULES, folders=FOLDERS, tiers=(UNIT, INTEGRATION, RENDERING, GUARD),
    libraries={"platform": ("sqlmodel",), "adapters": ("sqlmodel",), "web": ("fastapi",),
               "bootstrap": ("sqlmodel", "fastapi")},
    fakes=Fakes(("fakes",), ("ports",), "Fake"), each_root=("modules",), package_only=("contract",),
    scenarios=Scenarios("contract", "integration", "Result", ("given", "when", "then"), TABLE, "test_{name}.py"),
    no_comments=True, stand_ins=StandIns((MOCK, ("unittest", "mock", "MagicMock")), (AUTOSPEC,), ("spec", "spec_set")),
    framework=Framework(("test_*.py", "*_test.py"), "test_*"),
    forbidden={"domain": (NOW, ("builtins", "open"), ("socket",))}, singular="module")


def profile(**changes) -> Profile:
    """PROFILE with the given fields changed."""
    return replace(PROFILE, **changes)


def steps(path: str) -> tuple[str, ...]:
    return tuple(path.split("/"))


def dotted(name: str) -> tuple[str, ...]:
    return tuple(name.split("."))


def imp(line: int, module: str, *names: str, level: int = 0) -> Import:
    """`import module` with no names, `from module import names` with some; level counts a relative import's dots."""
    return Import(line, dotted(module) if module else (), level, names or None)


def source(path: str, *imports: Import, root: str = APP, **fields) -> SourceFile:
    """A file at path below root, shown as root/path, with its imports and any other field of a SourceFile."""
    return SourceFile(f"{root}/{path}", steps(path), imports, **fields)


def in_tests(path: str, *imports: Import, **fields) -> SourceFile:
    """A file at path below the tests root."""
    return source(path, *imports, root=TESTS, **fields)

