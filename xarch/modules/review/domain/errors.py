"""The errors review raises; each reason is safe to show as it is."""
from __future__ import annotations

from xarch.kernel.errors import DomainError


class NoSelection(DomainError):
    """No file was chosen: review reads only the files it is given."""

    def __init__(self) -> None:
        super().__init__("no file was chosen")


class AllWithOthers(DomainError):
    """Every file of the app was asked for together with paths or a list, which say less."""

    def __init__(self) -> None:
        super().__init__("every file of the app was asked for with other files")


class OverCap(DomainError):
    """More files would be judged than one run may judge."""

    def __init__(self, chosen: int, cap: int):
        super().__init__(f"{chosen} files would be judged, more than {cap}")
        self.chosen, self.cap = chosen, cap


class Unsendable(DomainError):
    """A question would be sent, and review has nothing to send it with."""

    def __init__(self) -> None:
        super().__init__("review has no decision model to send its questions to")


class Refused(DomainError):
    """The files or the profile cannot be read: a path outside the project, a profile that cannot be used; reason
    says which, as the module that refused says it."""
