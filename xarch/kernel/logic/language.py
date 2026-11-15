"""The language of the app as a check reads it: spec reads it from the language's data file, the rules module checks
the source with it."""
from __future__ import annotations

from dataclasses import dataclass

from xarch.kernel.logic.placement import Marks


@dataclass(frozen=True)
class LanguageView:
    """The language of the app as a check reads it: how a message names it, the ending of a source file's name, the
    file that stands for the folder holding it, the dotted names that mark a class as an interface, and those of what
    imports by a name worked out when the code runs."""
    title: str = ""
    extension: str = ""
    package_file: str = ""
    interface: tuple[tuple[str, ...], ...] = ()
    dynamic: tuple[tuple[str, ...], ...] = ()

    @property
    def marks(self) -> Marks:
        return Marks(self.extension, self.package_file)
