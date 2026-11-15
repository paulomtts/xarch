from app.modules.documents.adapters.moderation_content_review import ModerationContentReview
from app.modules.documents.application.controller import DocumentController
from app.platform.clock import SystemClock
from app.platform.sql import Session, create_engine
from app.web.routes import documents as documents_routes
from app.bootstrap.settings import Settings    # bootstrap/settings.py: reads the environment
from app.bootstrap.wiring import build_documents, build_moderation

@dataclass
class App:                              # what main holds on to
    web: FastAPI
    documents: DocumentController

def build_app(settings: Settings) -> App:
    engine = create_engine(settings.database_url)    # from platform/sql
    session = Session(engine)
    clock = SystemClock()                            # from platform/, used as the kernel's Clock
    moderation = build_moderation(session)
    documents = build_documents(session, clock, review=ModerationContentReview(moderation))   # an adapter wraps the provider's controller
    web = FastAPI()                                  # the program's own app object
    web.include_router(documents_routes.router)
    web.state.documents = documents                  # what web/dependencies.py reads
    return App(web=web, documents=documents)
