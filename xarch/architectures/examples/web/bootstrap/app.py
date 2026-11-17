from app.modules.documents.adapters.moderation_content_review import ModerationContentReview
from app.modules.documents.application.controller import DocumentController
from app.platform.clock import SystemClock
from app.platform.sql import Session, create_engine
from app.web.routes import documents as documents_routes
# reads the environment: bootstrap/settings.py
from app.bootstrap.settings import Settings
from app.bootstrap.wiring import build_documents, build_moderation

# what main holds on to
@dataclass
class App:
    web: FastAPI
    documents: DocumentController

def build_app(settings: Settings) -> App:
    # from platform/sql
    engine = create_engine(settings.database_url)
    session = Session(engine)
    # from platform/, used as the kernel's Clock
    clock = SystemClock()
    moderation = build_moderation(session)
    # an adapter wraps the provider's controller
    documents = build_documents(session, clock, review=ModerationContentReview(moderation))
    # the program's own app object
    web = FastAPI()
    web.include_router(documents_routes.router)
    # what web/dependencies.py reads
    web.state.documents = documents
    return App(web=web, documents=documents)
