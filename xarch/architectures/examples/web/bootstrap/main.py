from app.bootstrap.app import build_app
from app.bootstrap.settings import Settings

def main() -> None:
    uvicorn.run(build_app(Settings.from_env()).web)
