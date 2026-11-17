from app.modules.documents.contract.views import DocumentView

# the variants of the publish Result
@dataclass(frozen=True)
class Published: view: DocumentView
@dataclass(frozen=True)
class Missing: ...
# shared with the create Result
@dataclass(frozen=True)
class Rejected: reason: str

PublishResult = Published | Missing | Rejected

# the variants of the create Result
@dataclass(frozen=True)
class Created: view: DocumentView

CreateResult = Created | Rejected
