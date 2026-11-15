@pytest.fixture
def client():
    def build(controller: DocumentController) -> TestClient:
        app = FastAPI()
        app.include_router(router)
        app.dependency_overrides[documents_controller] = lambda: controller          # the route gets the fake controller
        return TestClient(app)
    return build
