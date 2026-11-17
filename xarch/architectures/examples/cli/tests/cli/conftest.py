@pytest.fixture
def client():
    def build(controller: DocumentController):
        cli = Typer()
        cli.add_typer(documents_commands.app, name="documents")
        # the command gets the fake controller
        return partial(CliRunner().invoke, cli, obj=App(cli=cli, documents=controller))
    return build
