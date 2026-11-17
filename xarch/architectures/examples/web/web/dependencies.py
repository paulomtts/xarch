from fastapi import Request

from app.modules.documents.application.controller import DocumentController

def documents_controller(request: Request) -> DocumentController:
    # bootstrap/ sets it when it builds the app
    return request.app.state.documents
