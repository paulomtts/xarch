from app.modules.documents.application.controller import DocumentController
from app.modules.documents.contract import PublishDocument, DocumentId, Published, Missing, Rejected
from app.web.dependencies import documents_controller
from app.web.i18n import t
from app.web.ui import render

router = APIRouter()                         # bootstrap/ includes this router in the program's FastAPI

@router.post("/documents/{id}/publish")
def publish(id: UUID, documents: DocumentController = Depends(documents_controller)):
    result = documents.publish(PublishDocument(DocumentId(id)))                 # controller call
    match result:                                # the route branches on the Result
        case Published(view): return render("documents/published", view=view)
        case Missing():       raise HTTPException(404, t("documents.missing"))
        case Rejected(why):   raise HTTPException(422, why)
