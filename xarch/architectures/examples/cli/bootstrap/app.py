from app.cli.commands import documents as documents_commands
from app.modules.documents.adapters.moderation_content_review import ModerationContentReview
from app.modules.documents.application.controller import DocumentController
from app.platform.clock import SystemClock
from app.platform.sql import Session, create_engine
# reads the environment: bootstrap/settings.py
from app.bootstrap.settings import Settings
from app.bootstrap.wiring import build_documents, build_moderation

# what main holds on to
@dataclass
class App:
    cli: Typer
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
    cli = Typer()
    cli.add_typer(documents_commands.app, name="documents")
    return App(cli=cli, documents=documents)
