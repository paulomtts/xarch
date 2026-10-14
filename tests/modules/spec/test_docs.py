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
    assert "{entry}" not in text and "{driver_proves}" not in text   # every placeholder was filled


def test_testing_puts_scenarios_in_the_use_case_tier_only_with_the_name_rule():
    text = templates()["testing.md"]
    files = text.split("## Files")[1].split("## ")[0]
    assert "| use case | use case, headed by its scenarios |" in files
    assert "Scenarios belong to the use-case tier only" in files
    assert "a scenario's name is its test's name" in files
    assert "Scenario: a draft with a title is published" in files
    assert "def test_a_draft_with_a_title_is_published" in files
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
    assert "class DocsRepo(Protocol):" in section and "class FakeDocsRepo:" in section


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


def test_only_testing_differs_between_profiles():
    cli, web = templates("cli"), templates("web")
    assert [path for path in cli if cli[path] != web[path]] == ["testing.md"]
