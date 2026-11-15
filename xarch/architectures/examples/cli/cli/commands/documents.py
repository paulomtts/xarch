from app.modules.documents.contract import PublishDocument, DocumentId, Published, Missing, Rejected
from app.cli.dependencies import documents_controller
from app.cli.terminal import echo, fail          # cli/terminal.py: the output helpers

app = Typer()                              # bootstrap/ adds this group to the program's Typer

@app.command()
def publish(ctx: Context, id: UUID):
    documents = documents_controller(ctx)
    result = documents.publish(PublishDocument(DocumentId(id)))                 # controller call
    match result:                                # the command branches on the Result
        case Published(view): echo(f"Published {view.title}")
        case Missing():       fail("No such document", code=1)
        case Rejected(why):   fail(why, code=2)
