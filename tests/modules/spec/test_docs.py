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
    "architecture.md": "What is the system structurally?",
    "testing.md": "How is the system tested?",
    "requirements.md": "What does it require to exist?",
    "adrs/0000-template.md": "What decisions have we made and why?",
    "artifacts/standards/_template.md": "What is the correct way of doing things?",
    "artifacts/audits/_template.md": "What does inconsistently wrong harness output look like?",
    "artifacts/taxonomy/_template.md": "What are the names for certain recognizable patterns?",
    "artifacts/modules/_template.md": "What is this module's responsibility? How does it behave? What are its invariants?",
    "artifacts/guards/_template.md": "What does this guard refuse, and why?",
}


TEMPLATES = [path for path in QUESTIONS if path != "testing.md"]       # testing.md is content, not a template


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
    assert QUESTIONS[path] in text.splitlines()[2]


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
    assert f"| driver | `{profile}/` | {driver}" in text
    assert "{" not in text                                            # every placeholder was filled


def test_testing_keeps_the_seed_in_bootstrap_for_the_smoke_tier_only():
    text = templates()["testing.md"]
    data = text.split("## Data")[1].split("## ")[0]
    assert "| smoke | the seed |" in data and "`bootstrap/`" in data
    assert data.count("seed") == text.count("seed")                   # no other tier mentions it


def test_only_testing_differs_between_profiles():
    cli, web = templates("cli"), templates("web")
    assert [path for path in cli if cli[path] != web[path]] == ["testing.md"]
