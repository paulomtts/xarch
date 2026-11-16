"""The docs of the bundled profiles, as the wired spec module publishes them: every document and folder of
docs/project/, with templates."""
import pytest

from xarch.bootstrap.wiring import build_spec
from xarch.modules.spec.contract import Docs

QUESTIONS = {
    "statement.md": "What problems are we trying to solve? What must the system do?",
    "domain.md": "What exists in this problem domain, and how does it work?",
    "design.md": "What are we proposing to build, and how will the pieces fit together?",
    "architecture.md": "How the system is structured",
    "testing.md": "How the system is tested",
    "requirements.md": "What does it require to exist?",
    "adrs/0000-template.md": "What decisions have we made and why?",
    "artifacts/standards/_template.md": "What is the correct way of doing things?",
    "artifacts/audits/_template.md": "What does inconsistently wrong harness output look like?",
    "artifacts/taxonomy/_template.md": "What are the names for certain recognizable patterns?",
    "artifacts/modules/_template.md": "What is this module's responsibility? How does it behave? What are its invariants?",
    "artifacts/guards/_template.md": "What does this guard refuse, and why?",
}


CONTENT = ["architecture.md", "testing.md"]
"""The docs written in full from the architecture, not left as templates."""
TEMPLATES = [path for path in QUESTIONS if path not in CONTENT]


def docs(profile: str = "cli") -> Docs:
    return build_spec().docs(profile)


def templates(profile: str = "cli") -> dict[str, str]:
    return {"/".join(f.path): f.template for f in docs(profile).files}


def test_the_docs_live_in_docs_project_beside_the_app():
    assert docs().root == ("docs", "project")


def test_every_document_and_folder_has_exactly_one_template_in_order():
    assert list(templates()) == list(QUESTIONS)


@pytest.mark.parametrize("path", list(QUESTIONS))
def test_each_template_starts_with_a_title_and_states_its_question(path):
    text = templates()[path]
    assert text.startswith("# ") and text.endswith("\n")
    assert QUESTIONS[path] in "\n".join(text.splitlines()[:4])


@pytest.mark.parametrize("path", TEMPLATES)
def test_each_template_is_short_with_sections(path):
    text = templates()[path]
    assert text.count("\n## ") >= 2
    assert len(text.splitlines()) <= 45


def test_the_domain_template_has_a_mermaid_placeholder():
    assert "```mermaid" in templates()["domain.md"]


@pytest.mark.parametrize("profile, driver", [("cli", "argument parsing"), ("web", "routing")])
def test_testing_gives_every_part_a_tier_and_names_the_profiles_driver(profile, driver):
    """Every placeholder was filled."""
    text = templates(profile)["testing.md"]
    for part in ["`kernel/`", "`domain/`", "`application/controller.py`", "`adapters/`", "`bootstrap/`",
                 f"`{profile}/`", "`platform/`", "`tests/architecture/`"]:
        assert part in text
    assert f"| rendering | `{profile}/` |" in text
    assert "{{" not in text and "}}" not in text


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_testing_unit_tests_pure_logic(profile):
    text = templates(profile)["testing.md"]
    assert "| unit | `domain/`, `application/logic/`, `adapters/`, `kernel/logic/`, `kernel/` |" in text
    assert "or by calling a pure function from `logic/`" in text.split("## 3. Placement")[1]


def test_testing_makes_the_given_when_then_table_the_standard_for_a_use_case():
    text = templates()["testing.md"]
    files = text.split("## 5. Files")[1].split("\n## ")[0]
    assert "| integration | use case |" in files
    assert "### 5.2 Tables" in files and "### 5.3 Tables in the other tiers" in files
    table = files.split("### 5.2 Tables")[1].split("### 5.3 ")[0]
    for rule in ["`given`", "`when`", "`then`", "`pytest.param(..., id=\"<a sentence stating the outcome>\")`",
                 "`controller(**given)`", "no `if`, `match`, `try`, `for` or `while`", "fire-only", "fresh id",
                 "dict(review=Denied(\"spam\"))", "own test"]:
        assert rule in table, rule
    other = files.split("### 5.3 ")[1]
    assert "inputs" in other and "answer" in other and "no status-code or exit-code column" in other
    guards = text.split("## 9. Guards")[1]
    assert "`scenario-coverage`" in guards
    outside = text.replace(guards, "")
    assert "[[#5.2 Tables]]" in outside and "[[#5.3 Tables in the other tiers]]" in outside and "(section 5.2)" in outside


def test_testing_names_a_table_test_for_the_use_case_and_a_standalone_test_for_its_outcome():
    text = templates()["testing.md"]
    naming = text.split("### 8.2 How tests are named")[1].split("\n### ")[0]
    assert "`test_publish`" in naming and "`test_is_stale`" in naming
    assert "id" in naming and "never" in naming
    assert "> [!TIP]\n> **Litmus test.** When the test fails" in naming


def test_testing_takes_the_data_of_an_integration_test_from_its_given_column():
    text = templates()["testing.md"]
    data = text.split("## 7. Data")[1].split("\n## ")[0]
    assert "| integration | the `given` column" in data


def test_the_helper_builds_the_fakes_from_their_starting_state_for_both_forms_of_given():
    text = templates()["testing.md"]
    helpers = text.split("### 8.1 Where helpers live")[1].split("\n### ")[0]
    assert "def controller(repo: Iterable[Document] = (), review: Allowed | Denied = Allowed()" in helpers
    assert "FakeDocumentRepo(repo)" in helpers and "FakeContentReview(review)" in helpers
    fake = text.split("## 6. Fakes and mocks")[1].split("\n## ")[0]
    assert "def __init__(self, docs: Iterable[Document] = ()): self.docs = {d.id: d for d in docs}" in fake
    assert "def save(self, doc): self.docs[doc.id] = doc\n" in fake
    assert "def save(self, doc: Document) -> None: ..." in fake


def test_testing_gives_every_tier_a_litmus_test_in_placement():
    text = templates()["testing.md"]
    tiers = [line.split("|")[1].strip() for line in text.split("## 1. Tiers")[1].split("\n## ")[0].splitlines()
             if line.startswith("| ") and not line.startswith("| Tier")]
    placement = text.split("## 3. Placement")[1].split("\n## ")[0]
    assert tiers == ["unit", "integration", "rendering", "guard"]
    verdicts = {"integration": "it is an integration test", "guard": "it is a guard"}
    for tier in tiers:
        assert f"### 3.{tiers.index(tier) + 1} {tier}\n\n> [!TIP]\n> **Litmus test.** " in placement
        assert verdicts.get(tier, f"it is a {tier} test") in placement


def test_testing_fakes_stateful_ports_and_mocks_fire_only_ones():
    """The names follow the naming table."""
    text = templates()["testing.md"]
    section = text.split("## 6. Fakes and mocks")[1].split("\n## ")[0]
    assert "| reads back what it wrote | read (stateful) | at least one returns a value | a fake" in section
    assert "| only fires and never reads | fire-only | every one returns `None` | a mock that names the port" in section
    assert "a mock is not a fake" in section
    assert "class DocumentRepo(Protocol):" in section and "class FakeDocumentRepo:" in section
    assert "class DbDocumentRepo:" in section
    assert "> [!TIP]\n> **Litmus test.** Does the use case ever read back" in section
    assert "A port that is written and then read back is a read port" in section
    assert "two unrelated needs" in section and "`check` does not report it" in section


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_testing_shows_one_example_test_per_tier(profile):
    examples = templates(profile)["testing.md"].split("## 4. Examples")[1].split("\n## ")[0]
    for tier in ["unit", "integration", "rendering", "guard"]:
        assert f"# {tier}: tests/" in examples
    assert f"# rendering: tests/{profile}/" in examples


def test_testing_keeps_the_seed_in_bootstrap_and_in_no_tier():
    text = templates()["testing.md"]
    data = text.split("## 7. Data")[1].split("\n## ")[0]
    assert "`bootstrap/`" in data and "No tier runs a shared seed" in data


def test_only_architecture_and_testing_differ_between_profiles():
    cli, web = templates("cli"), templates("web")
    assert [path for path in cli if cli[path] != web[path]] == ["architecture.md", "testing.md"]


@pytest.mark.parametrize("profile, folder, other", [("cli", "cli/", "web/"), ("web", "web/", "cli/")])
def test_architecture_is_the_full_document_for_the_profiles_entry_point(profile, folder, other):
    """Docs are published below docs/project."""
    text = templates(profile)["architecture.md"]
    assert text.count("\n## ") >= 9 and len(text.splitlines()) > 400
    for section in ["## 1. Structure", "## 5. The dependency rules", f"### 9.3 {folder}", "### 9.4 bootstrap/"]:
        assert section in text
    assert f"── {folder}" in text and f"── {other}" not in text
    assert f"| `{folder}` | any module's `application/controller.py` and `contract/`" in text
    assert "└── project/" in text
    assert "docs/cli" not in text and "docs/web" not in text


def test_architecture_keeps_its_braces_and_tool_name():
    """Code examples keep their braces."""
    text = templates()["architecture.md"]
    assert "{{" not in text and "}}" not in text
    assert 'echo(f"Published {view.title}")' in text


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_architecture_orders_a_modules_layers_inward(profile):
    text = templates(profile)["architecture.md"]
    layers = text.split("## 3. The rings inside a module")[1].split("## 4.")[0]
    chain = ["domain/", "contract/", "application/logic/", "application/ports/", "application/services/",
             "application/controller.py"]
    assert " → ".join(f"`{step}`" for step in chain) in layers
    assert "`platform/` → `adapters/`" in layers
    assert text.split("## 5. ")[1].startswith("The dependency rules\n\nDependencies point inward:")


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_table_model_lives_in_platform_and_the_repo_translates_it(profile):
    """Columns only: it knows no module's types."""
    text = templates(profile)["architecture.md"]
    adapters = text.split("### 8.7 adapters/")[1].split("### 8.8")[0]
    platform = text.split("### 9.2 platform/")[1].split("### 9.3")[0]
    assert "def _to_domain(self, row: DocumentRow) -> Document:" in adapters
    assert "def _from_domain(self, doc: Document) -> DocumentRow:" in adapters
    assert "and never in `domain/` or in the table model" in adapters
    table = block(platform, "platform/sql/tables/documents.py")
    assert "class DocumentRow(SQLModel, table=True):" in table and '__tablename__ = "documents"' in table
    assert "app.modules" not in table and "Document," not in table
    assert "knows no module's types" in platform and "table models" in platform


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_ports_may_import_only_the_domain_and_the_kernel(profile):
    rows = templates(profile)["architecture.md"].split("## 5. ")[1].split("\n\n")
    ports = [line for line in "\n".join(rows).splitlines() if line.startswith("| `application/ports/`")]
    assert ports == ["| `application/ports/` | its own module's `domain/`, `kernel/`, `kernel/logic/` |"]


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_architecture_says_plainly_that_files_within_one_part_import_each_other_freely(profile):
    text = templates(profile)["architecture.md"].split("## 5. ")[1].split("| Part |")[0]
    assert "Files within one part may import each other freely" in text
    assert "not checked" in text


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_architecture_defines_build_moderation_beside_build_documents(profile):
    wiring = templates(profile)["architecture.md"].split("# bootstrap/wiring.py")[1].split("# bootstrap/app.py")[0]
    assert "def build_documents(" in wiring
    assert "def build_moderation(session: Session) -> ModerationController:" in wiring
    assert wiring.index("def build_documents(") < wiring.index("def build_moderation(")


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_architecture_has_a_naming_table_where_an_adapter_ends_with_its_ports_name(profile):
    text = templates(profile)["architecture.md"]
    assert "  - [[#8.8 Naming]]" in text
    naming = text.split("### 8.8 Naming")[1].split("## 9.")[0]
    for kind in ["command", "DTO", "Result variant", "Result union", "entity", "id", "domain error", "service",
                 "controller", "pure rule", "port", "adapter", "table model", "test fake"]:
        assert f"| {kind} |" in naming
    assert "| adapter | `adapters/` | `<System><PortName>`" in naming
    assert "`DbDocumentRepo`" in naming and "`ModerationContentReview`" in naming
    assert "always ends with the name of the port it fills" in naming


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_architecture_gives_pure_logic_a_place_in_the_module_and_in_the_kernel(profile):
    """The domain does not import logic."""
    text = templates(profile)["architecture.md"]
    assert "    └── logic/                  pure functions that modules share" in text
    assert "│       │   ├── logic/          pure functions over the module's domain objects" in text
    rules = text.split("## 5. ")[1].split("## 6.")[0]
    assert "| `application/logic/` | its own module's `domain/`, `kernel/`, `kernel/logic/` |" in rules
    assert ("| `application/controller.py` | its own module's `application/services/`, `application/logic/`, `domain/`, "
            "`application/ports/` and `contract/`, `kernel/`, `kernel/logic/` |") in rules
    assert "| `domain/` | `kernel/`, `kernel/logic/` |" in rules
    assert "| `kernel/logic/` | `kernel/` |" in rules
    assert "`domain` → `logic` → `ports` → `services`" in text.split("## 7. ")[1].split("## 8.")[0]
    assert "  - [[#8.5 application/logic/]]" in text and "  - [[#8.6 application/ports/]]" in text
    logic = text.split("### 8.5 application/logic/")[1].split("### 8.6 ")[0]
    assert "def is_stale(doc: Document, now: datetime) -> bool:" in block(logic, "modules/documents/application/logic/staleness.py")
    assert "from app.modules.documents.application.logic.staleness import is_stale" in logic
    assert "is_stale(doc, self._clock.now())" in logic
    assert "> **Litmus test.** Is it a pure function over this module's domain objects, not one entity's invariant" in logic
    assert "it belongs in `kernel/logic/`" in logic and "it belongs in that entity in `domain/`" in logic
    kernel = text.split("### 9.1 kernel/")[1].split("### 9.2 ")[0]
    assert "including a business rule two modules need" in kernel
    assert "it goes in `kernel/logic/`" in kernel


def test_architecture_defines_every_name_its_examples_use():
    text = templates()["architecture.md"]
    for definition in ["class CreateDocument:", "class Created:", "CreateResult = ", "class ContentRejected(",
                       "class DocumentIncomplete(", "def new(cls, title: str)", "class Allowed", "class Denied"]:
        assert definition in text, definition
    assert "from app.modules.moderation.contract import ReviewText, ReviewResult, Clean, Flagged" in text


def test_architecture_names_the_reviews_outcomes_apart_from_the_create_results_variant():
    """The review's outcome becomes a domain error. The controller's Result variant stays."""
    text = templates()["architecture.md"]
    assert "-> Allowed | Denied:" in text
    assert "case Denied(why): raise ContentRejected(why)" in text
    assert "return Rejected(e.reason)" in text


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_testing_tells_the_same_story_as_architecture(profile):
    """One row per variant of the publish Result."""
    text = templates(profile)["testing.md"]
    examples = text.split("## 4. Examples")[1].split("\n## ")[0]
    assert "One module, `documents`, with a use case `publish`" in examples
    for name in ["PublishDocument", "Rejected", "Missing", "Published", "DbDocumentRepo", "DocumentIncomplete",
                 "is_stale"]:
        assert name in examples, name
    table = examples.split("# integration:")[1].split("# rendering:")[0]
    for variant in ["is published", "is missing", "is rejected"]:
        assert 'id="a document' in table and variant in table
    assert "def test_publish(given, when, then):" in table and "pytest.param(" in table


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_rendering_example_is_a_table_of_the_result_and_what_is_shown_with_no_code(profile):
    examples = templates(profile)["testing.md"].split("## 4. Examples")[1].split("\n## ")[0]
    rendering = examples.split("# rendering:")[1].split("# guard:")[0]
    assert '@pytest.mark.parametrize("result, shown", [' in rendering
    assert "def test_publish(client, result, shown):" in rendering
    assert rendering.count("pytest.param(") == 3 and rendering.count('id="a ') == 3
    for word in ["status", "exit", "404", "422", "code"]:
        assert word not in rendering, word
    assert "given" not in rendering and "when" not in rendering


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_unit_example_is_a_table_of_a_rules_inputs_and_its_answer(profile):
    examples = templates(profile)["testing.md"].split("## 4. Examples")[1].split("\n## ")[0]
    unit = examples.split("# unit:")[1].split("# integration:")[0]
    assert '@pytest.mark.parametrize("published_at, now, stale", [' in unit
    assert "def test_is_stale(published_at, now, stale):" in unit and unit.count("pytest.param(") == 3
    assert "given" not in unit and "then" not in unit


def test_testing_drives_each_profiles_entry_point_its_own_way():
    cli = templates("cli")["testing.md"].split("# rendering:")[1].split("# guard:")[0]
    web = templates("web")["testing.md"].split("# rendering:")[1].split("# guard:")[0]
    assert "CliRunner" in templates("cli")["testing.md"] and "Published Hello" in cli and '["documents", "publish"' in cli
    assert "client" in web and "Hello" in web
    assert "CliRunner" not in templates("web")["testing.md"]


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_service_builds_the_dto_and_the_controller_maps_failures(profile):
    text = templates(profile)["architecture.md"]
    controller = text.split("### 8.3 ")[1].split("### 8.4 ")[0]
    service = text.split("### 8.4 ")[1].split("### 8.5 ")[0]
    assert "return Published(view)" in controller and "return Created(view)" in controller
    assert "return Missing()" in controller and "return Rejected(e.reason)" in controller
    assert "_view" not in controller and "DocumentView" not in controller
    assert "def publish(self, id: DocumentId) -> DocumentView:" in service
    assert "def create(self, title: str) -> DocumentView:" in service
    assert "def _view(self, doc: Document) -> DocumentView:" in service
    assert "turn each exception a service raises into the `Result` variant that says it" in controller
    assert "assemble what the use case hands out on success" in service
    assert "which the service builds from the entity (section 8.4)" in text


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_contract_example_is_split_into_files_like_a_real_contract(profile):
    text = templates(profile)["architecture.md"]
    contract = text.split("### 8.1 ")[1].split("### 8.2 ")[0]
    for path in ["commands.py", "views.py", "results.py", "__init__.py"]:
        assert f"# modules/documents/contract/{path}" in contract
    commands = contract.split("contract/commands.py")[1].split("# modules/")[0]
    assert "class PublishDocument:" in commands and "class CreateDocument:" in commands
    assert "class DocumentView:" in contract.split("contract/views.py")[1].split("# modules/")[0]
    results = contract.split("contract/results.py")[1].split("# modules/")[0]
    assert "from app.modules.documents.contract.views import DocumentView" in results and "CreateResult = " in results
    init = contract.split("contract/__init__.py")[1].split("```")[0]
    assert "from app.modules.documents.contract.commands import" in init
    assert "from app.modules.documents.contract.results import" in init and "class " not in init
    assert "imports from `contract`, never from its files" in contract


def block(text: str, header: str) -> str:
    """The code of one example file: from its path comment to the next path comment or the end of its fence.

    The last one: an earlier mention may only excerpt the file.
    """
    body = text.split(f"# {header}")[-1]
    cut = [i for i in (body.find("\n# modules/"), body.find("\n# bootstrap/"), body.find("\n# cli/"),
                       body.find("\n# web/"), body.find("\n# kernel/"), body.find("\n# platform/"), body.find("\n```"))
           if i != -1]
    return body[:min(cut)]


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_every_example_file_shows_the_imports_between_the_projects_own_files(profile):
    text = templates(profile)["architecture.md"]
    expected = {
        "modules/documents/domain/errors.py": ["from app.kernel.errors import DomainError, NotFound"],
        "modules/documents/domain/document.py": [
            "from app.kernel.identifiers import new_id", "from app.modules.documents.domain.errors import",
            "from app.modules.documents.domain.values import DocumentId"],
        "modules/documents/application/controller.py": [
            "from app.modules.documents.contract import", "from app.modules.documents.domain.errors import",
            "from app.modules.documents.application.services.document_service import DocumentService"],
        "modules/documents/application/services/document_service.py": [
            "from app.modules.documents.application.ports.document_repo import DocumentRepo",
            "from app.modules.documents.domain.document import Document", "from app.kernel.time import Clock"],
        "modules/documents/application/ports/document_repo.py": [
            "from app.modules.documents.domain.document import Document",
            "from app.modules.documents.domain.values import DocumentId"],
        "modules/documents/adapters/db_document_repo.py": [
            "from app.platform.sql.tables.documents import DocumentRow", "from app.platform.sql import Session",
            "from app.modules.documents.domain.document import Document"],
        "bootstrap/wiring.py": [
            "from app.modules.documents.adapters.db_document_repo import DbDocumentRepo",
            "from app.platform.sql import Session"],
    }
    for header, imports in expected.items():
        code = block(text, header)
        for line in imports:
            assert line in code, (header, line)


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_examples_say_which_imports_they_show(profile):
    text = templates(profile)["architecture.md"]
    assert "Every import starts at `app.`" in text
    assert "standard library and third-party packages are left out" in text


def test_web_routes_are_plain_functions_and_bootstrap_owns_the_app():
    text = templates("web")["architecture.md"]
    routes = block(text, "web/routes/documents.py")
    assert "router = APIRouter()" in routes and '@router.post("/documents/{id}/publish")' in routes
    assert "def publish(id: UUID, documents: DocumentController = Depends(documents_controller)) -> Response:" in routes
    assert "from app.web.dependencies import documents_controller" in routes
    assert "from app.web.i18n import t" in routes and "from app.web.ui import render" in routes
    assert "request.app.state.documents" in block(text, "web/dependencies.py")
    app = block(text, "bootstrap/app.py")
    assert "web = FastAPI()" in app and "web.include_router(documents_routes.router)" in app
    assert "web.state.documents = documents" in app and "def build_app(settings: Settings) -> App:" in app
    assert "engine = create_engine(settings.database_url)" in app and "return App(web=web," in app
    assert "uvicorn.run(build_app(Settings.from_env()).web)" in text


def test_cli_commands_are_plain_functions_and_bootstrap_owns_the_app():
    text = templates("cli")["architecture.md"]
    commands = block(text, "cli/commands/documents.py")
    assert "app = Typer()" in commands and "@app.command()" in commands
    assert "def publish(ctx: Context, id: UUID) -> None:" in commands and "documents = documents_controller(ctx)" in commands
    assert "from app.cli.dependencies import documents_controller" in commands and "from app.cli.terminal import echo, fail" in commands
    assert "ctx.obj.documents" in block(text, "cli/dependencies.py")
    app = block(text, "bootstrap/app.py")
    assert "cli = Typer()" in app and 'cli.add_typer(documents_commands.app, name="documents")' in app
    assert "def build_app(settings: Settings) -> App:" in app and "return App(cli=cli," in app
    assert "app.cli(obj=app)" in text


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_entry_point_never_imports_the_bootstrap(profile):
    text = templates(profile)["architecture.md"]
    folder = "cli" if profile == "cli" else "web"
    for header in [f"{folder}/dependencies.py", f"{folder}/{'commands' if profile == 'cli' else 'routes'}/documents.py"]:
        code = block(text, header)
        assert "from app.bootstrap" not in code


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_no_example_uses_a_relative_import(profile):
    import re
    text = templates(profile)["architecture.md"]
    assert re.findall(r"^\s*from \.+\S* import|^\s*from \. import", text, re.M) == []


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_schema_is_shown_as_a_migration_and_the_row_is_the_modules_view_of_it(profile):
    """SQLModel builds the table, not hand-written SQL."""
    text = templates(profile)["architecture.md"]
    bootstrap = text.split("### 9.4 bootstrap/")[1]
    migration = block(bootstrap, "bootstrap/migrations/0001_create_documents.py")
    assert "from app.platform.sql.tables.documents import DocumentRow" in migration
    assert "def upgrade(engine: Engine) -> None:" in migration
    assert "SQLModel.metadata.create_all(engine, tables=[DocumentRow.__table__])" in migration
    assert "builds the table from the table model" in bootstrap and "a new migration file, never an edit of an old one" in bootstrap
    assert "adapters" not in migration
    assert "(section 9.4 shows one)" in text.split("### 8.7 adapters/")[1].split("### 8.8")[0]
    assert "adapters/ · repos\"]" in text


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_table_model_is_named_by_its_place_in_the_naming_table_and_the_tree(profile):
    text = templates(profile)["architecture.md"]
    assert "| table model | `platform/sql/tables/` | thing and `Row` | `DocumentRow` |" in text
    assert "sql engine, sessions and table models" in text
    assert "Each table is defined once, in `platform/`" in text


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_architecture_says_where_callers_other_than_the_entry_point_live(profile):
    """Transactions and the caller are the implementation's business."""
    text = templates(profile)["architecture.md"]
    section = text.split("## 10. Callers other than the entry point")[1]
    assert "`bootstrap/jobs/<job>.py`" in section and "handed a fake one" in section
    assert "- [[#10. Callers other than the entry point]]" in text
    assert "section 10 says where each lives" in text
