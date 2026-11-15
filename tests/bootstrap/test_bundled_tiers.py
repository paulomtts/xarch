"""The tiers of the bundled profiles and of a custom one, loaded and written out through the wiring."""
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_architectures, load_architecture
from xarch.modules.spec.contract import Subject
from xarch.modules.spec.domain.errors import InvalidTemplate


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_every_part_of_a_bundled_architecture_is_tested_or_says_why_not(profile):
    """Rendering tests the entry point."""
    architecture = load_architecture(profile)
    tested = {subject.part for tier in architecture.tiers for subject in tier.subject}
    untested = {name for name, part in architecture.parts.items() if part.untested}
    assert tested | untested == set(architecture.parts) and not tested & untested
    assert untested == {"platform", "bootstrap"}
    assert [tier.name for tier in architecture.tiers] == ["unit", "integration", "rendering",
                                                          "guard"]
    assert architecture.tiers[2].subject[0] == Subject(profile)
    assert all(tier.litmus and tier.example for tier in architecture.tiers)


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_bundled_tier_examples_pass_the_example_check(profile):
    assert build_architectures().check_examples(profile) == ()


CUSTOM = """\
xarch: 2
name: layered
testing: pytest
parts:
  api:
    path: "src/<module>/api"
    role: handlers
    may_import: [store]
    tier: driver
  store:
    path: "src/<module>/store"
    role: database access
    tier: unit
  shared: {path: shared, role: helpers, untested: reached through the parts that use it}
tiers:
  unit:
    proves: a query
    litmus: |
      Does it query?
      If yes, it is a unit test.
    docs:
      may_touch: an in-memory database
      data: built in the test
      example: tests/store/test_store.py
  driver:
    proves: routing
    litmus: Does it route?
    docs:
      may_touch: a fake store
      data: none
      example: tests/api/test_api.py
docs:
  entry: api
  pages:
    architecture.md: {from: layered.md}
    testing.md: {from: layered-testing.md}
  examples: [examples]
  example_notes: {tests/api/test_api.py: one per route}
"""


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_a_custom_architecture_with_its_own_tiers_gets_its_own_testing_md(tmp_path):
    write(tmp_path / "layered.md", "# Layered\n")
    write(tmp_path / "layered-testing.md", "# Testing of {{entry}}\n\n{{tiers}}\n\n{{untested}}\n\n{{tier_litmus:3}}\n\n"
                                          "Run it: `<command>`\n\n{{tier_data}}\n\n{{tier_examples}}\n")
    write(tmp_path / "examples" / "tests/store/test_store.py", "def test_a_query(): ...\n")
    write(tmp_path / "examples" / "tests/api/test_api.py", "def test_a_route(): ...\n")
    docs = build_architectures().docs(write(tmp_path / "layered.yaml", CUSTOM))
    texts = {"/".join(f.path): f.template for f in docs.files}
    assert texts["testing.md"] == (
        "# Testing of src/*/api\n\n"
        "| Tier | Subject | Proves | May touch |\n|---|---|---|---|\n"
        "| unit | `store/` | a query | an in-memory database |\n"
        "| driver | `api/` | routing | a fake store |\n\n"
        "`shared/` gets no tier of its own: reached through the parts that use it.\n\n"
        "### 3.1 unit\n\n> [!TIP]\n> **Litmus test.** Does it query? If yes, it is a unit test.\n\n"
        "### 3.2 driver\n\n> [!TIP]\n> **Litmus test.** Does it route?\n\n"
        "Run it: `<command>`\n\n"
        "| Tier | Where its data comes from |\n|---|---|\n| unit | built in the test |\n| driver | none |\n\n"
        "```python\n# unit: tests/store/test_store.py\ndef test_a_query(): ...\n\n"
        "# driver: tests/api/test_api.py (one per route)\ndef test_a_route(): ...\n```\n")
    assert [f.path for f in docs.files] == [("architecture.md",), ("testing.md",)]


def test_a_custom_testing_template_with_a_bad_placeholder_fails_naming_it(tmp_path):
    write(tmp_path / "layered.md", "# Layered\n")
    write(tmp_path / "layered-testing.md", "{{tier_files}}\n{{tier}}\n")
    write(tmp_path / "examples" / "tests/store/test_store.py", "")
    write(tmp_path / "examples" / "tests/api/test_api.py", "")
    with pytest.raises(InvalidTemplate) as caught:
        build_architectures().docs(write(tmp_path / "layered.yaml", CUSTOM))
    assert caught.value.problems[0] == (
        "layered-testing.md: {{tier_files}}: tier 'unit' has no `one_file_per`, tier 'unit' has no `cases_from`, "
        "tier 'driver' has no `one_file_per`, tier 'driver' has no `cases_from`")
    assert caught.value.problems[1].startswith("layered-testing.md: unknown placeholder {{tier}}: use {{tree}}")
