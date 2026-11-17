from typer import Context

from app.modules.documents.application.controller import DocumentController

def documents_controller(ctx: Context) -> DocumentController:
    return ctx.obj.documents           # bootstrap/ passes the App as the context object
