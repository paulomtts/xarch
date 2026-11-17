def controller(repo: Iterable[Document] = (), review: Allowed | Denied = Allowed(), now: datetime = NOW) -> DocumentController:
    # each argument is a fake's start state
    service = DocumentService(FakeDocumentRepo(repo), FakeContentReview(review), FakeClock(now))
    return DocumentController(service)
