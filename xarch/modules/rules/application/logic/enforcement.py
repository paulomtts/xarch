"""The findings of the enforcement section, besides the violations: what the check could not see or was told to
pass over, read from the same parsed files.

    skipped    a use, in a test file, of a name the profile's `tests.skips` lists, or one below it: a marker such as
               `pytest.mark.skip`, `pytest.mark.skipif(...)` (a name of its own, so listed on its own) or a call such
               as `pytest.skip(...)`, read through imports like any use (see the Use value); one per use
    dynamic    a use, in a file read, of what Python imports by a computed or string name with:
               `importlib.import_module`, `importlib.__import__` and the builtin `__import__`; the import rules
               cannot see what those import
    drift      an init file (`files` in the profile) that is missing, or pinned and not what `init` would write now

strict_findings lists what `--strict` fails on: every finding but the guards that the bundled profile in force, or
the one a custom profile is compared with, also leaves off; with no profile to compare with, every guard left off.
"""
from __future__ import annotations

from collections.abc import Iterable, Sequence

from xarch.modules.rules.domain.values import At, Drift, Enforcement, Finding, InitFile, Profile, SourceFile

DYNAMIC = (("importlib", "import_module"), ("importlib", "__import__"), ("builtins", "__import__"))
"""The callables of Python itself that import by a name computed at run time."""
MISSING, CHANGED = "missing", "changed"


def skipped(tests: Iterable[SourceFile], profile: Profile) -> list[At]:
    skips = profile.framework.skips if profile.framework is not None else ()
    return [At(file.name, use.line) for file in tests for use in file.uses
            if any(use.name[:len(skip)] == skip for skip in skips)]


def dynamic(files: Iterable[SourceFile]) -> list[At]:
    return [At(file.name, use.line) for file in files for use in file.uses if use.name in DYNAMIC]


def drift(files: Sequence[InitFile], found: Sequence[str | None]) -> list[Drift]:
    """found holds the text of each file as it stands, None where there is none."""
    states = [(file, MISSING if text is None else CHANGED if file.pinned and text != file.text else None)
              for file, text in zip(files, found)]
    return [Drift("/".join(file.path), state) for file, state in states if state is not None]


def strict_findings(enforcement: Enforcement) -> tuple[Finding, ...]:
    origin = enforcement.origin
    found = [Finding("guards_off", g) for g in origin.guards_off if g not in origin.baseline_off]
    found += [Finding("looser", f"{item.key}: {item.sentence}") for item in origin.looser]
    found += [Finding("ungoverned", file) for file in enforcement.ungoverned]
    found += [Finding("init_files", f"{item.file} is {item.state}") for item in enforcement.init_files]
    found += [Finding("skipped", f"{at.file}:{at.line}") for at in enforcement.skipped]
    found += [Finding("dynamic", f"{at.file}:{at.line}") for at in enforcement.dynamic]
    found += [Finding("weak", f"{weak.file}:{weak.line}: {weak.message}") for weak in enforcement.weak]
    return tuple(found)
