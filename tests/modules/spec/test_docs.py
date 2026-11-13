"""Tests for the docs layout the spec module publishes: every document and folder of docs/project/, with templates."""
import pytest

from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.application.services.skeleton import SkeletonService
from xarch.modules.spec.contract import Docs
from tests.fakes.settings import FakeSettings

QUESTIONS = {
    "statement.md": "What problems are we trying to solve? What must the system do?",
    "domain.md": "What exists in this problem domain, and how does it work?",
    "design.md": "What are we proposing to build, and how will the pieces fit together?",
    "architecture.md": "How the system is structured",
    "testing.md": "How is the system tested?",
    "requirements.md": "What does it require to exist?",
    "adrs/0000-template.md": "What decisions have we made and why?",
    "artifacts/standards/_template.md": "What is the correct way of doing things?",
    "artifacts/audits/_template.md": "What does inconsistently wrong harness output look like?",
    "artifacts/taxonomy/_template.md": "What are the names for certain recognizable patterns?",
    "artifacts/modules/_template.md": "What is this module's responsibility? How does it behave? What are its invariants?",
    "artifacts/guards/_template.md": "What does this guard refuse, and why?",
}


CONTENT = ["architecture.md", "testing.md"]                              # written in full, not templates
TEMPLATES = [path for path in QUESTIONS if path not in CONTENT]


def docs(profile: str = "cli") -> Docs:
    return SpecController(SkeletonService(FakeSettings())).docs(profile)


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
    text = templates(profile)["testing.md"]
    for part in ["`kernel/`", "`domain/`", "`application/`", "`contract/`", "`adapters/`", "`bootstrap/`",
                 f"`{profile}/`", "`platform/`", "`tests/architecture/`"]:
        assert part in text
    assert f"| driver | `{profile}/`, `bootstrap/jobs/` | {driver}" in text
    assert "{entry}" not in text and "{driver_proves}" not in text and "{driver_test}" not in text   # every placeholder was filled


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_testing_unit_tests_pure_logic(profile):
    text = templates(profile)["testing.md"]
    assert "| unit | `kernel/` and `kernel/logic/`, `domain/`, `application/logic/` |" in text
    assert "or by calling a\n> pure function from `logic/`" in text.split("## Placement")[1]


def test_testing_puts_scenarios_in_the_use_case_tier_only_with_the_name_rule():
    text = templates()["testing.md"]
    files = text.split("## Files")[1].split("## ")[0]
    assert "| use case | use case, headed by its scenarios |" in files
    assert "Scenarios belong to the use-case tier only" in files
    assert "a scenario's name is its test's name" in files
    assert "Scenario: a document with a title is published" in files
    assert "def test_a_document_with_a_title_is_published" in files
    assert text.count("cenario") == files.count("cenario")           # no other section mentions them


def test_testing_gives_every_tier_a_litmus_test_in_placement():
    text = templates()["testing.md"]
    tiers = [line.split("|")[1].strip() for line in text.split("## Tiers")[1].split("## ")[0].splitlines()
             if line.startswith("| ") and not line.startswith("| Tier")]
    placement = text.split("## Placement")[1].split("## ")[0]
    assert tiers == ["unit", "use case", "conformance", "driver", "bootstrap", "guard"]
    verdicts = {"use case": "it is a use-case test", "bootstrap": "it is the bootstrap test", "guard": "it is a guard"}
    for tier in tiers:
        assert f"> **{tier}.** " in placement
        assert verdicts.get(tier, f"it is a {tier} test") in placement


def test_testing_fakes_stateful_ports_and_mocks_fire_only_ones():
    text = templates()["testing.md"]
    section = text.split("## Fakes and mocks")[1].split("## ")[0]
    assert "| reads back what it wrote | stateful | a fake" in section
    assert "| only fires and never reads | fire-only | a mock" in section
    assert "A mock has nothing to conform." in section
    assert "class DocumentRepo(Protocol):" in section and "class FakeDocumentRepo:" in section
    assert "class DbDocumentRepo:" in section and "DocsRepo" not in text     # the names follow the naming table
    assert "> **Litmus test.** Does the use case ever read back" in section
    assert "If a port does both, split the port" in section


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_testing_shows_one_example_test_per_tier(profile):
    examples = templates(profile)["testing.md"].split("## Examples")[1].split("## ")[0]
    for tier in ["unit", "use case", "conformance", "driver", "bootstrap", "guard"]:
        assert f"# {tier}: tests/" in examples
    assert f"# driver: tests/{profile}/" in examples


def test_testing_keeps_the_seed_in_bootstrap_for_the_bootstrap_tier_only():
    text = templates()["testing.md"]
    data = text.split("## Data")[1].split("## ")[0]
    assert "| bootstrap | the seed |" in data and "`bootstrap/`" in data
    assert "smoke" not in text
    outside = [line for line in text.replace(data, "").splitlines() if "seed" in line]
    assert all("bootstrap" in line for line in outside)               # no other tier mentions it


def test_only_architecture_and_testing_differ_between_profiles():
    cli, web = templates("cli"), templates("web")
    assert [path for path in cli if cli[path] != web[path]] == ["architecture.md", "testing.md"]


@pytest.mark.parametrize("profile, folder, other", [("cli", "cli/", "web/"), ("web", "web/", "cli/")])
def test_architecture_is_the_full_document_for_the_profiles_entry_point(profile, folder, other):
    text = templates(profile)["architecture.md"]
    assert text.count("\n## ") >= 9 and len(text.splitlines()) > 400
    for section in ["## 1. Structure", "## 5. The dependency rules", f"### 9.3 {folder}", "### 9.4 bootstrap/"]:
        assert section in text
    assert f"└── {folder}" in text and f"└── {other}" not in text
    assert f"| `{folder}` | any module's `controller`" in text
    assert "└── project/" in text                                         # docs are published below docs/project
    assert "docs/cli" not in text and "docs/web" not in text


def test_architecture_keeps_its_braces_and_tool_name():
    text = templates()["architecture.md"]
    assert "{entry}" not in text and "{driver_proves}" not in text
    assert 'echo(f"Published {view.title}")' in text                      # code examples are not run through format


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_architecture_assumes_nothing_about_who_uses_the_app(profile):
    assert "single user" not in templates(profile)["architecture.md"]


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_architecture_does_not_ask_for_a_home_for_future_callers(profile):
    assert "home in the tree" not in templates(profile)["architecture.md"]


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_architecture_orders_a_modules_layers_inward_instead_of_allowing_sideways_imports(profile):
    text = templates(profile)["architecture.md"]
    assert "sideways" not in text and "same ring" not in text
    layers = text.split("## 3. The rings inside a module")[1].split("## 4.")[0]
    assert "`domain/` → `contract/` → `application/logic/` → `application/ports/` → `application/services/` → `application/controller.py`" in layers
    assert "`platform/` → `adapters/`" in layers
    assert text.split("## 5. ")[1].startswith("The dependency rules\n\nDependencies point inward:")


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_table_model_lives_in_platform_and_the_repo_translates_it(profile):
    text = templates(profile)["architecture.md"]
    adapters = text.split("### 8.7 adapters/")[1].split("### 8.8")[0]
    platform = text.split("### 9.2 platform/")[1].split("### 9.3")[0]
    assert "class DocumentRow" not in adapters and "document_row.py" not in text
    assert "def _to_domain(self, row: DocumentRow) -> Document:" in adapters and "def _from_domain(self, doc: Document) -> DocumentRow:" in adapters
    assert "_to_row" not in adapters and "_to_document" not in adapters
    assert "and never in `domain/` or in the table model" in adapters
    table = block(platform, "platform/sql/tables/documents.py")
    assert "class DocumentRow(SQLModel, table=True):" in table and '__tablename__ = "documents"' in table
    assert "app.modules" not in table and "Document," not in table           # columns only: it knows no module's types
    assert "knows no module's types" in platform and "table models" in platform


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_ports_may_import_only_the_domain_and_the_kernel(profile):
    rows = templates(profile)["architecture.md"].split("## 5. ")[1].split("\n\n")
    ports = [line for line in "\n".join(rows).splitlines() if line.startswith("| `application/ports/`")]
    assert ports == ["| `application/ports/` | its own module's `domain/`, `kernel/` |"]


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_architecture_says_plainly_that_files_within_one_part_import_each_other_freely(profile):
    text = templates(profile)["architecture.md"].split("## 5. ")[1].split("| Part |")[0]
    assert "Every part may also import its own files" not in text
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
    text = templates(profile)["architecture.md"]
    assert "│   └── logic/                  pure functions that modules share" in text
    assert "│       │   ├── logic/          pure functions over the module's domain objects" in text
    rules = text.split("## 5. ")[1].split("## 6.")[0]
    assert "| `application/logic/` | its own module's `domain/`, `kernel/` |" in rules
    assert "`services/` (the controller only), `logic/`, `domain/`, `ports/` and `contract/`, `kernel/` |" in rules
    assert "| `domain/` | its own module's `domain/`, `kernel/` |" in rules           # the domain does not import logic
    assert "`domain` → `logic` → `ports` → `services`" in text.split("## 7. ")[1].split("## 8.")[0]
    assert "  - [[#8.5 application/logic/]]" in text and "  - [[#8.6 application/ports/]]" in text
    logic = text.split("### 8.5 application/logic/")[1].split("### 8.6 ")[0]
    assert "def is_stale(doc: Document, now: datetime) -> bool:" in block(logic, "modules/documents/application/logic/staleness.py")
    assert "from app.modules.documents.application.logic.staleness import is_stale" in logic
    assert "is_stale(doc, self._clock.now())" in logic
    assert "> **Litmus test.** Is it a pure function over this module's domain objects, not one entity's invariant" in logic
    assert "it belongs in `kernel/logic/`" in logic and "it belongs in that entity in `domain/`" in logic
    kernel = text.split("### 9.1 kernel/")[1].split("### 9.2 ")[0]
    assert "Nothing here has business meaning" not in kernel and "including a business rule two modules need" in kernel
    assert "it goes in `kernel/logic/`" in kernel


def test_architecture_defines_every_name_its_examples_use():
    text = templates()["architecture.md"]
    for definition in ["class CreateDocument:", "class Created:", "CreateResult = ", "class ContentRejected(",
                       "class DocumentIncomplete(", "def new(cls, title: str)", "class Allowed", "class Denied"]:
        assert definition in text, definition
    assert "from app.modules.moderation.contract import ReviewText, ReviewResult, Clean, Flagged" in text


def test_architecture_names_the_reviews_outcomes_apart_from_the_create_results_variant():
    text = templates()["architecture.md"]
    assert "-> Allowed | Denied:" in text
    assert "case Denied(why): raise ContentRejected(why)" in text         # the review's outcome becomes a domain error
    assert "Allowed | Denied | Rejected" not in text and "case Rejected(" not in text.split("### 8.4 ")[1].split("### 8.5 ")[0]
    assert "return Rejected(e.reason)" in text                            # the controller's Result variant stays


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_testing_tells_the_same_story_as_architecture(profile):
    text = templates(profile)["testing.md"]
    examples = text.split("## Examples")[1].split("## ")[0]
    assert "One module, `documents`, with a use case `publish`" in examples
    for name in ["Draft", "Refused", "Publish(", "a_draft", "`docs`", "tests/modules/docs/", "test_docs_repo"]:
        assert name not in text, name
    for name in ["PublishDocument", "Rejected", "FakeDocumentRepo", "DbDocumentRepo", "DocumentIncomplete", "Published"]:
        assert name in examples, name
    scenarios = text.split("## Files")[1].split("## ")[0]
    for variant in ["is published", "is missing", "is rejected"]:       # one scenario per variant of the publish Result
        assert f"Scenario: a document" in scenarios and variant in scenarios
        assert f"def test_a_document" in scenarios


def test_testing_drives_each_profiles_entry_point_its_own_way():
    cli = templates("cli")["testing.md"].split("# driver:")[1].split("# bootstrap:")[0]
    web = templates("web")["testing.md"].split("# driver:")[1].split("# bootstrap:")[0]
    assert "runner" in cli and "exit_code == 0" in cli and "Published Hello" in cli and '["documents", "publish"' in cli
    assert "client" in web and "status_code == 200" in web and "Hello" in web
    assert "runner" not in web and "exit_code" not in web


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_controller_builds_the_dto_and_the_service_returns_the_entity(profile):
    text = templates(profile)["architecture.md"]
    controller = text.split("### 8.3 ")[1].split("### 8.4 ")[0]
    service = text.split("### 8.4 ")[1].split("### 8.5 ")[0]
    assert "return Published(self._view(doc))" in controller and "return Created(self._view(doc))" in controller
    assert "def _view(self, doc: Document) -> DocumentView:" in controller
    assert "entities into DTOs" in controller
    assert "def publish(self, id: DocumentId) -> Document:" in service and "def create(self, title: str) -> Document:" in service
    assert "to_view" not in text and "DocumentView" not in service
    assert "without building the `Result` or the DTO" in service
    assert "which the controller builds from the entity (section 8.3)" in text


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
    assert "from app.modules.documents.contract.commands import" in init and "from app.modules.documents.contract.results import" in init and "class " not in init
    assert "imports from `contract`, never from its files" in contract


def block(text: str, header: str) -> str:
    """The code of one example file: from its path comment to the next path comment or the end of its fence."""
    body = text.split(f"# {header}")[-1]              # the last one: an earlier mention may only excerpt the file
    cut = [i for i in (body.find("\n# modules/"), body.find("\n# bootstrap/"), body.find("\n# cli/"),
                       body.find("\n# web/"), body.find("\n# kernel/"), body.find("\n# platform/"), body.find("\n```"))
           if i != -1]
    return body[:min(cut)]


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_every_example_file_shows_the_imports_between_the_projects_own_files(profile):
    text = templates(profile)["architecture.md"]
    expected = {
        "modules/documents/domain/errors.py": ["from app.kernel.errors import DomainError, NotFound"],
        "modules/documents/domain/document.py": ["from app.kernel.identifiers import new_id", "from app.modules.documents.domain.errors import", "from app.modules.documents.domain.values import DocumentId"],
        "modules/documents/application/controller.py": ["from app.modules.documents.contract import", "from app.modules.documents.domain.errors import", "from app.modules.documents.application.services.document_service import DocumentService"],
        "modules/documents/application/services/document_service.py": ["from app.modules.documents.application.ports.document_repo import DocumentRepo", "from app.modules.documents.domain.document import Document", "from app.kernel.time import Clock"],
        "modules/documents/application/ports/document_repo.py": ["from app.modules.documents.domain.document import Document", "from app.modules.documents.domain.values import DocumentId"],
        "modules/documents/adapters/db_document_repo.py": ["from app.platform.sql.tables.documents import DocumentRow", "from app.platform.sql import Session", "from app.modules.documents.domain.document import Document"],
        "bootstrap/wiring.py": ["from app.modules.documents.adapters.db_document_repo import DbDocumentRepo", "from app.platform.sql import Session"],
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



@pytest.mark.parametrize("profile", ["cli", "web"])
def test_no_registering_happens_inside_the_entry_point(profile):
    text = templates(profile)["architecture.md"]
    assert "register_controllers" not in text and "def register(" not in text


def test_web_routes_are_plain_functions_and_bootstrap_owns_the_app():
    text = templates("web")["architecture.md"]
    routes = block(text, "web/routes/documents.py")
    assert "router = APIRouter()" in routes and '@router.post("/documents/{id}/publish")' in routes
    assert "def publish(id: UUID, documents: DocumentController = Depends(documents_controller)):" in routes
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
    assert "def publish(ctx: Context, id: UUID):" in commands and "documents = documents_controller(ctx)" in commands
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
    text = templates(profile)["architecture.md"]
    bootstrap = text.split("### 9.4 bootstrap/")[1]
    migration = block(bootstrap, "bootstrap/migrations/0001_create_documents.py")
    assert "from app.platform.sql.tables.documents import DocumentRow" in migration
    assert "def upgrade(engine: Engine) -> None:" in migration
    assert "SQLModel.metadata.create_all(engine, tables=[DocumentRow.__table__])" in migration
    assert "CREATE TABLE" not in text and "exec_driver_sql" not in text          # SQLModel builds the table, not hand-written SQL
    assert "builds the table from the table model" in bootstrap and "a new migration file, never an edit of an old one" in bootstrap
    assert "adapters" not in migration and "names one of the row classes" not in text
    assert "(section 9.4 shows one)" in text.split("### 8.7 adapters/")[1].split("### 8.8")[0]
    assert "models · migrations" not in text and "repos · table models" not in text and "adapters/ · repos\"]" in text


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_table_model_is_named_by_its_place_in_the_naming_table_and_the_tree(profile):
    text = templates(profile)["architecture.md"]
    assert "| table model | `platform/sql/tables/` | thing and `Row` | `DocumentRow` |" in text
    assert "sql engine, sessions and table models" in text
    assert "so two modules may map the same tables" not in text and "Each table is defined once, in `platform/`" in text


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_architecture_says_where_callers_other_than_the_entry_point_live(profile):
    text = templates(profile)["architecture.md"]
    section = text.split("## 10. Callers other than the entry point")[1]
    assert "`bootstrap/jobs/<job>.py`" in section and "driver test" in section
    assert "- [[#10. Callers other than the entry point]]" in text
    assert "section 10 says where each lives" in text
    assert "UnitOfWork" not in text and "Actor" not in text         # transactions and the caller are the implementation's business
