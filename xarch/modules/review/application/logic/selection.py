"""Which files review judges: the paths it is given, and of the files found there those it reads, each other one left
out with why."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.review.domain.errors import AllWithOthers, InPieces, NoSelection, OverCap
from xarch.modules.review.domain.published import (
    BY_ALL,
    BY_LIST,
    BY_PATHS,
    MAX_FILES,
    MAX_PIECED,
    MIN_CHARS,
    SMALL,
    UNPARSABLE,
    LeftOut,
)
from xarch.modules.review.domain.values import CodeFile, Found


def chosen(paths: tuple[Path, ...], listed: tuple[Path, ...], every: bool, app: Path,
           pieces: bool = False) -> tuple[Path, ...]:
    """The paths to read: those given and those listed, in that order, or the app folder for every file of the app;
    raises NoSelection when none is given, AllWithOthers when every file is asked for with others, InPieces when
    every file is asked for in pieces (about a third of the pieces of good files read low: a sweep is noise)."""
    if every and (paths or listed):
        raise AllWithOthers()
    if every and pieces:
        raise InPieces()
    if every:
        return (app,)
    if not paths and not listed:
        raise NoSelection()
    return paths + listed


def ways(paths: tuple[Path, ...], listed: tuple[Path, ...], every: bool) -> tuple[str, ...]:
    """How the files were chosen, each way once, in the order of BY_PATHS, BY_LIST and BY_ALL."""
    return tuple(way for way, used in ((BY_PATHS, bool(paths)), (BY_LIST, bool(listed)), (BY_ALL, every)) if used)


def _why_unjudged(file: CodeFile) -> str:
    """Why a file read is not judged, "" when it is: it does not parse, or it is too small."""
    return UNPARSABLE if file.error is not None else SMALL if len(file.text) < MIN_CHARS else ""


def judged(found: Found) -> tuple[CodeFile, ...]:
    """The files read that are judged, in order."""
    return tuple(file for file in found.read if not _why_unjudged(file))


def left_out(found: Found) -> tuple[LeftOut, ...]:
    """The files found that are not judged, each with why and its size: those not read, then those read that are not
    judged, each in order."""
    return found.unread + tuple(LeftOut(file.file, why, len(file.text)) for file in found.read
                                if (why := _why_unjudged(file)))


def within_cap(files: tuple[CodeFile, ...], given: int | None, pieces: bool) -> tuple[CodeFile, ...]:
    """The files, when they are no more than one run judges (given, else MAX_PIECED for a run that ranks pieces, else
    MAX_FILES); raises OverCap otherwise."""
    cap = given if given is not None else MAX_PIECED if pieces else MAX_FILES
    if len(files) > cap:
        raise OverCap(len(files), cap)
    return files
