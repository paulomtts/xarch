from app.cli.commands import documents as documents_commands
from app.modules.documents.adapters.moderation_content_review import ModerationContentReview
from app.modules.documents.application.controller import DocumentController
from app.platform.clock import SystemClock
from app.platform.sql import Session, create_engine
from app.bootstrap.settings import Settings    # bootstrap/settings.py: reads the environment
from app.bootstrap.wiring import build_documents, build_moderation

@dataclass
class App:                              # what main and the bootstrap test hold on to
    cli: Typer
    documents: DocumentController

def build_app(settings: Settings) -> App:
    engine = create_engine(settings.database_url)    # from platform/sql
    session = Session(engine)
    clock = SystemClock()                            # from platform/, used as the kernel's Clock
    moderation = build_moderation(session)
    documents = build_documents(session, clock, review=ModerationContentReview(moderation))   # an adapter wraps the provider's controller
    cli = Typer()                                    # the program's own app object
    cli.add_typer(documents_commands.app, name="documents")
    return App(cli=cli, documents=documents)
