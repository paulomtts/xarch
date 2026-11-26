from __future__ import annotations

from pathlib import Path

from xarch.kernel.errors import DomainError
from xarch.kernel.source import Unparsable


class RootMissing(DomainError):
    def __init__(self, root: Path):
        super().__init__(f"{root} is not a directory")
        self.root = root


class OutsideProject(DomainError):
    """A path that lies outside the project: not below the folder holding the app folder."""

    def __init__(self, path: Path, project: Path):
        super().__init__(f"{path.as_posix()} lies outside the project: it is not below {project.as_posix()}")


class Unreadable(DomainError):
    """A source text that does not parse, and where and why, as the reader says it."""

    def __init__(self, found: Unparsable):
        super().__init__(f"line {found.line}: {found.message}")
        self.found = found


class ProfileUnusable(DomainError):
    """The profile in force cannot be read for what the check needs of it; reason says why, as the spec module put
    it."""


class RuleRefused(DomainError):
    """A rule that names a word that does not exist, or one that does not apply to what its slot reads: its id, and
    every problem, each as `<slot>: <what>, <what to write>`."""

    def __init__(self, rule: str, problems: tuple[str, ...]):
        super().__init__(f"{rule}: {'; '.join(problems)}")
        self.rule, self.problems = rule, problems


class ChecksRefused(ProfileUnusable):
    """The checks a profile writes itself cannot be run: every problem of every check, each named by its address in
    the profile."""

    def __init__(self, problems: tuple[str, ...]):
        super().__init__("; ".join(problems))
        self.problems = problems


class Unloaded(DomainError):
    """The profile at location does not load: every problem the loader found, each in words."""

    def __init__(self, location: str, problems: tuple[str, ...]):
        super().__init__("; ".join(problems))
        self.location, self.problems = location, problems


class NoProfile(DomainError):
    """No profile is given, and none is configured for the project: the profiles it knows, to choose one from."""

    def __init__(self, known: tuple[str, ...]):
        super().__init__(f"no profile is chosen: the profiles found are {', '.join(known)}")
        self.known = known


class UnknownRule(DomainError):
    """A rule asked for by name that is neither one of check's nor a check of the profile's own (own, by id)."""

    def __init__(self, rule: str, own: tuple[str, ...]):
        mine = f", or a check of the profile's own: {', '.join(own)}" if own else ""
        super().__init__(f"{rule} is no rule of check: name a rule id `xarch check` reports{mine}")
        self.rule = rule


class StrictAgainst(DomainError):
    """`check --strict` asked with --against: strict fails on how the profile stands to its baseline, which --against
    does not change, so the two are never run together."""

    def __init__(self) -> None:
        super().__init__("--against shows a comparison and --strict fails on one: run `check --strict` without "
                         "--against, and it judges the profile against its baseline")
