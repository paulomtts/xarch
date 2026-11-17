"""Which files review never sends: those a path the profile writes under `review.never` matches, the profile's own
examples among them. A path is matched
step by step against a file's path below the app, and against the path below the app of the file it links to when it
is a link: a step as written, `*` for any text inside one step, and a step
that is `**` for any number of folders, none included; a path that matches a folder holds back every file below it. An
example is matched by its path below the app, as the profile writes it."""
from __future__ import annotations

import re
from dataclasses import replace

from xarch.modules.review.domain.published import CLEAN, FEWEST_EXAMPLES, FLAGGED, NEVER, PLACEMENT, HeldExample, LeftOut
from xarch.modules.review.domain.values import CodeFile, EvalText, Found

ANY_FOLDERS = "**"
"""A step of a path that stands for any number of folders, none included."""


def _step(pattern: str, step: str) -> bool:
    return re.fullmatch("[^/]*".join(re.escape(piece) for piece in pattern.split("*")), step) is not None


def _starts(pattern: tuple[str, ...], path: tuple[str, ...]) -> bool:
    """Whether the pattern matches the path or a folder above it."""
    if not pattern:
        return True
    if pattern[0] == ANY_FOLDERS:
        return any(_starts(pattern[1:], path[skipped:]) for skipped in range(len(path) + 1))
    return bool(path) and _step(pattern[0], path[0]) and _starts(pattern[1:], path[1:])


def _below_app(file: str) -> tuple[str, ...]:
    """The steps below the app of a file of the app, shown from the folder holding the app."""
    return tuple(file.split("/")[1:])


def _first(paths: list[tuple[str, ...]], never: tuple[str, ...]) -> str:
    """The first path of never that matches one of the paths, each as its steps below the app, "" for none."""
    return next((pattern for pattern in never if any(_starts(tuple(pattern.split("/")), path) for path in paths)), "")


def _held_by(file: CodeFile, never: tuple[str, ...]) -> str:
    """The first path of never that matches the file, or the file it links to, "" for none."""
    return _first([_below_app(shown) for shown in (file.file, file.target) if shown], never)


def held_by(path: str, never: tuple[str, ...]) -> str:
    """The first path of never that matches an example of the profile's own, by its path below the app as the profile
    writes it, "" for none."""
    return _first([tuple(path.split("/"))], never)


def kept_examples(asked: EvalText, never: tuple[str, ...]) -> EvalText:
    """The eval with only the examples no path of never matches: those it is held to, and held as."""
    return replace(asked, flagged_examples=tuple(item for item in asked.flagged_examples if not held_by(item[0], never)),
                   clean_examples=tuple(item for item in asked.clean_examples if not held_by(item[0], never)))


def kept_files(examples: tuple[CodeFile, ...], never: tuple[str, ...]) -> tuple[CodeFile, ...]:
    """The examples of placement no path of never matches, in order."""
    return tuple(example for example in examples if not held_by(example.file, never))


def examples_held(asked: EvalText, never: tuple[str, ...]) -> tuple[HeldExample, ...]:
    """Each example of the eval a path of never matches, flagged ones first, with the path that matched."""
    return tuple(HeldExample(asked.asked, kind, path, pattern)
                 for kind, files in ((FLAGGED, asked.flagged_examples), (CLEAN, asked.clean_examples))
                 for path, _ in files if (pattern := held_by(path, never)))


def files_held(kind: str, examples: tuple[CodeFile, ...], never: tuple[str, ...]) -> tuple[HeldExample, ...]:
    """Each example of placement of the kind, lying in a part, that a path of never matches, with the path that
    matched."""
    return tuple(HeldExample(PLACEMENT, kind, example.file, pattern) for example in examples
                 if example.part and (pattern := held_by(example.file, never)))


def too_few(asked: EvalText) -> str:
    """The kind of example (flagged, then clean) of which the eval holds fewer than FEWEST_EXAMPLES, "" for none."""
    return next((kind for kind, files in ((FLAGGED, asked.flagged_examples), (CLEAN, asked.clean_examples))
                 if len(files) < FEWEST_EXAMPLES), "")


def held_back(found: Found, never: tuple[str, ...]) -> Found:
    """The files found, with each file read that a path of never matches moved to those left out, after the others,
    with the path that matched; its text goes nowhere."""
    kept = tuple(file for file in found.read if not _held_by(file, never))
    held = tuple(LeftOut(file.file, NEVER, len(file.text), pattern) for file in found.read
                 if (pattern := _held_by(file, never)))
    return Found(kept, found.unread + held)


def unmatched(found: Found, never: tuple[str, ...]) -> tuple[str, ...]:
    """The paths of never that match no file read, nor the file any links to, in never's order."""
    return tuple(pattern for pattern in never if not any(_held_by(file, (pattern,)) for file in found.read))
