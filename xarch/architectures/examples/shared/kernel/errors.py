# the base of every module's errors; it names no module's thing
class DomainError(Exception):
    # a message safe to show the caller
    reason: str
class NotFound(DomainError): ...
