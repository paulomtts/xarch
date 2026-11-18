"""The errors review raises; each reason is safe to show as it is."""
from __future__ import annotations

from xarch.kernel.errors import DomainError
from xarch.modules.review.domain.published import LeftOut, Reading


class NoSelection(DomainError):
    """No file was chosen: review reads only the files it is given."""

    def __init__(self) -> None:
        super().__init__("no file was chosen")


class AllWithOthers(DomainError):
    """Every file of the app was asked for together with paths or a list, which say less."""

    def __init__(self) -> None:
        super().__init__("every file of the app was asked for with other files")


class InPieces(DomainError):
    """Every file of the app was asked for in pieces: a sweep over pieces is noise."""

    def __init__(self) -> None:
        super().__init__("every file of the app was asked for in pieces")


class OverCap(DomainError):
    """More files would be judged than one run may judge."""

    def __init__(self, chosen: int, cap: int):
        super().__init__(f"{chosen} files would be judged, more than {cap}")
        self.chosen, self.cap = chosen, cap


class NoKey(DomainError):
    """A question would be sent, and the key of the decision model's service is not set; variable is where it is read
    from."""

    def __init__(self, variable: str):
        super().__init__(f"no key: {variable} is not set")
        self.variable = variable


class Unanswered(DomainError):
    """The decision model failed on a question; reason says how, the key in no word of it."""


class NotAccepted(Unanswered):
    """The decision model would not take one request, as that request's own fault (too large, or one it cannot read);
    reason says why, the key in no word of it. Unlike any other failure, it says nothing of the next request, which is
    still sent."""


class Refused(DomainError):
    """The files or the profile cannot be read: a path outside the project, a profile that cannot be used; reason
    says which, as the module that refused says it."""


class NoSuchEval(DomainError):
    """Evals were asked for by ids the profile writes no eval of its own of: those ids, and the ids it does write."""

    def __init__(self, names: tuple[str, ...], known: tuple[str, ...]):
        super().__init__(f"no eval of the profile's own named {', '.join(names)}")
        self.names, self.known = names, known


class NoWhy(DomainError):
    """A file was to be accepted with no reason given: a person accepts a file for a reason, which the record keeps."""

    def __init__(self) -> None:
        super().__init__("no reason was given")


class Unjudged(DomainError):
    """Files were to be accepted that review does not judge: each, with why it is left out."""

    def __init__(self, files: tuple[LeftOut, ...]):
        super().__init__(f"review does not judge {', '.join(item.file for item in files)}")
        self.files = files


class NoAnswerKept(DomainError):
    """Files were to be accepted whose answer is not in the cache: accepting sends nothing, so they must be reviewed
    first."""

    def __init__(self, files: tuple[str, ...]):
        super().__init__(f"no answer is kept for {', '.join(files)}")
        self.files = files


class Undoubted(DomainError):
    """Files were to be accepted that do not read as doubtful: there is nothing to accept; each, as it reads."""

    def __init__(self, readings: tuple[Reading, ...]):
        super().__init__(f"{', '.join(item.file for item in readings)} do not read as doubtful")
        self.readings = readings


class Unrecorded(DomainError):
    """Files were to be taken out of the record of accepted files that it does not name: each, as review shows it."""

    def __init__(self, files: tuple[str, ...]):
        super().__init__(f"the record of accepted files does not name {', '.join(files)}")
        self.files = files
