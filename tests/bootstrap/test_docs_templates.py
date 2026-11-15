"""Docs templates filled through the wiring: the bundled ones generate the checked-in docs, and a custom architecture
brings its own."""
from importlib import resources
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_architectures, build_spec, load_architecture
from xarch.modules.spec.domain.errors import InvalidTemplate

DOCS = Path(__file__).resolve().parents[2] / "docs"


PROFILES = ["cli", "web"]
CHECKED_IN = [(profile, path.relative_to(DOCS / profile).as_posix()) for profile in PROFILES
              for path in sorted((DOCS / profile).rglob("*.md"))]
"""Every doc checked in under docs/<profile>/, the golden copy of what `init` writes into docs/project/."""


def generated(profile: str) -> dict[str, str]:
    return {"/".join(f.path): f.template for f in build_spec().docs(profile).files}


@pytest.mark.parametrize("profile", PROFILES)
def test_init_writes_exactly_the_docs_checked_in_for_the_profile(profile):
    assert sorted(generated(profile)) == sorted(path for p, path in CHECKED_IN if p == profile)


@pytest.mark.parametrize("profile, doc", [pytest.param(p, d, id=f"{p}/{d}") for p, d in CHECKED_IN])
def test_the_bundled_architecture_and_templates_generate_each_checked_in_doc_byte_for_byte(profile, doc):
    assert generated(profile)[doc] == (DOCS / profile / doc).read_text(encoding="utf-8")


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_the_bundled_template_holds_no_hand_typed_structure(profile):
    template = resources.files("xarch").joinpath("architectures", f"{profile}.md").read_text(encoding="utf-8")
    for placeholder in ["{{tree}}", "{{rules_table}}", "{{layers:application}}", "{{layers:edge}}", "{{placement}}",
                        "{{naming}}"]:
        assert template.count(placeholder) == 1, placeholder
    for part in load_architecture(profile).parts:
        assert template.count(f"{{{{litmus:{part}}}}}") == 1, part
    assert "**Litmus test.** Does it" not in template and "├──" not in template.split("tests/")[0]


def test_the_bundled_testing_template_is_shared_and_holds_no_hand_typed_tiers():
    """The commands that run the tiers are left as `<command>`: they are the project's own."""
    for profile in ("cli", "web"):
        docs = {"/".join(doc.path): doc.source for doc in load_architecture(profile).docs}
        assert docs["testing.md"] == "testing.md"
    template = resources.files("xarch").joinpath("architectures", "testing.md").read_text(encoding="utf-8")
    for placeholder in ["{{tiers}}", "{{untested}}", "{{tier_litmus:3}}", "{{tier_index:3}}", "{{tier_examples}}",
                        "{{tier_helpers}}", "{{tier_files}}", "{{tier_data}}"]:
        assert template.count(placeholder) == 1, placeholder
    assert "| unit |" not in template and "> **unit.**" not in template and "# unit:" not in template
    assert "- unit, integration, rendering, guard: `<command>`" in template


def write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


ARCHITECTURE = """\
xarch: 2
name: layered
parts:
  api:   {path: "src/<module>/api", role: handlers, litmus: "Does it parse?", may_import: [store]}
  store: {path: "src/<module>/store", role: database access, litmus: "Does it query?"}
docs:
  entry: api
  pages:
    architecture.md: {from: layered.md, note: this file}
"""


def test_a_custom_architecture_brings_its_own_template(tmp_path):
    """It names no testing template, so it gets no testing.md."""
    write(tmp_path / "notes.md", "# Notes\n")
    write(tmp_path / "layered.md", "# Layered\n\nsrc/\n{{tree}}\n\n{{rules_table}}\n\n{{litmus:api}}\n")
    docs = build_architectures().docs(write(tmp_path / "layered.yaml", ARCHITECTURE + "    notes.md: {from: notes.md}\n"))
    texts = {"/".join(f.path): f.template for f in docs.files}
    assert texts["architecture.md"] == (
        "# Layered\n\nsrc/\n"
        "└── src/\n    └── <module>/\n        ├── api/     handlers\n        └── store/   database access\n\n"
        "| Part | May import |\n|---|---|\n| `api/` | its own module's `store/` |\n| `store/` | nothing |\n\n"
        "> [!TIP]\n> **Litmus test.** Does it parse?\n")
    assert list(texts) == ["architecture.md", "notes.md"] and texts["notes.md"] == "# Notes\n"


def test_a_template_with_a_bad_placeholder_fails_naming_the_template(tmp_path):
    write(tmp_path / "layered.md", "{{litmus:repo}} {{tables}}\n")
    with pytest.raises(InvalidTemplate) as caught:
        build_architectures().docs(write(tmp_path / "layered.yaml", ARCHITECTURE))
    assert caught.value.problems[0] == "layered.md: {{litmus:repo}}: the architecture defines no part 'repo'"
    assert caught.value.problems[1].startswith("layered.md: unknown placeholder {{tables}}: use {{tree}}")


def test_an_architecture_that_declares_no_docs_gets_none(tmp_path):
    path = write(tmp_path / "layered.yaml", ARCHITECTURE.split("docs:")[0])
    assert build_architectures().docs(path).files == ()
