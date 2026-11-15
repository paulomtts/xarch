from app.modules.documents.application.controller import DocumentController

def documents_controller(request: Request) -> DocumentController:
    return request.app.state.documents       # bootstrap/ sets it when it builds the app
