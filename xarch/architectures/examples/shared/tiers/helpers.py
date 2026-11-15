def controller(repo: Iterable[Document] = (), review: Allowed | Denied = Allowed(), now: datetime = NOW) -> DocumentController:
    service = DocumentService(FakeDocumentRepo(repo), FakeContentReview(review), FakeClock(now))   # each argument is a fake's start state
    return DocumentController(service)
