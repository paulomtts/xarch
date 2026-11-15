def controller(repo: DocumentRepo, review: ContentReview | None = None, clock: Clock | None = None) -> DocumentController:
    service = DocumentService(repo, review or FakeContentReview(), clock or FakeClock(NOW))   # what the test omits is a fake
    return DocumentController(service)
