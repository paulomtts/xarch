from app.modules.documents.contract import PublishDocument, DocumentId, Published, Missing, Rejected
from app.cli.dependencies import documents_controller
# the output helpers: cli/terminal.py
from app.cli.terminal import echo, fail

# bootstrap/ adds this group to the program's Typer
app = Typer()

@app.command()
def publish(ctx: Context, id: UUID) -> None:
    documents = documents_controller(ctx)
    # controller call
    result = documents.publish(PublishDocument(DocumentId(id)))
    # the command branches on the Result
    match result:
        case Published(view): echo(f"Published {view.title}")
        case Missing():       fail("No such document", code=1)
        case Rejected(why):   fail(why, code=2)
