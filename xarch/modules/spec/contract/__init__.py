"""What the spec module publishes: the skeleton of a profile as flat lists of entries, and which profile is in force."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Entry:
    path: tuple[str, ...]      # e.g. ("application", "controller.py")
    is_dir: bool
    leaf: bool                 # a file, or a directory that holds nothing in the spec


@dataclass(frozen=True)
class Skeleton:
    top_level: tuple[Entry, ...]   # below the app root
    module: tuple[Entry, ...]      # below modules/<module>/
    entry_point: str               # the top-level folder that drives the modules, e.g. "cli" or "web"


@dataclass(frozen=True)
class DocFile:
    path: tuple[str, ...]          # below the docs root, e.g. ("adrs", "0000-template.md")
    template: str                  # the text a new file starts with: content for testing.md, a template elsewhere


@dataclass(frozen=True)
class Docs:
    """The project docs of a profile; folders exist because the template files inside them do."""
    root: tuple[str, ...]          # below the folder holding the app, e.g. ("docs", "project")
    files: tuple[DocFile, ...]


@dataclass(frozen=True)
class SelectProfile:
    app: Path                      # the app folder; its project's pyproject.toml may configure the profile
    override: str | None = None    # an explicit choice, e.g. from --profile


@dataclass(frozen=True)
class ProfileSelected:
    name: str


@dataclass(frozen=True)
class ProfileRefused:
    reason: str                    # safe to show the user as-is


ProfileResult = ProfileSelected | ProfileRefused
