@pytest.fixture
def client():
    def build(controller: DocumentController) -> TestClient:
        app = FastAPI()
        app.include_router(router)
        # the route gets the fake controller
        app.dependency_overrides[documents_controller] = lambda: controller
        return TestClient(app)
    return build
