@pytest.fixture
def client():
    def build(controller: DocumentController):
        cli = Typer()
        cli.add_typer(documents_commands.app, name="documents")
        return partial(CliRunner().invoke, cli, obj=App(cli=cli, documents=controller))   # the command gets the fake controller
    return build
