from app.bootstrap.app import build_app
from app.bootstrap.settings import Settings

def main() -> None:
    app = build_app(Settings.from_env())
    app.cli(obj=app)                   # the App is the context object that cli/dependencies.py reads
