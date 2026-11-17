from app.kernel.errors import DomainError, NotFound

class DocumentNotFound(NotFound):      reason = "The document does not exist."
class DocumentIncomplete(DomainError): reason = "The document needs a title."
class ContentRejected(DomainError):
    # the review's reason, passed on
    def __init__(self, why: str): self.reason = why
