"""`xarch profile new` through the real app: a bundled profile is copied into the project with every file it points
to, so that the copy loads and passes `xarch profile check` untouched; nothing is overwritten."""
import pytest
import yaml
from typer.testing import CliRunner

from tests.bootstrap.project import bundled_profiles
from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_spec, load_architecture

runner = CliRunner()
BUNDLED = bundled_profiles()


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "cli"\n')


@pytest.mark.parametrize("bundled", BUNDLED)
def test_the_copy_of_each_bundled_profile_loads_and_passes_the_profile_check_untouched(tmp_path, bundled):
    result = runner.invoke(app, ["profile", "new", "mine", "--from", bundled])
    assert result.exit_code == 0, result.output
    copy = tmp_path / "architecture" / "mine" / "mine.yaml"
    architecture = load_architecture(copy)
    assert (architecture.name, architecture.based_on) == ("mine", bundled)
    assert load_architecture(bundled).parts.keys() == architecture.parts.keys()
    checked = runner.invoke(app, ["profile", "check", str(copy)])
    assert checked.exit_code == 0, checked.output
    assert f"no looser than {bundled}" in checked.output
    assert runner.invoke(app, ["profile", "check", "--format", "json", str(copy)]).exit_code == 0


@pytest.mark.parametrize("bundled", BUNDLED)
def test_the_copy_holds_every_file_the_bundled_profile_points_to(tmp_path, bundled):
    runner.invoke(app, ["profile", "new", "mine", "--from", bundled])
    written = {p.relative_to(tmp_path / "architecture" / "mine").as_posix()
               for p in (tmp_path / "architecture" / "mine").rglob("*") if p.is_file()}
    pointed = build_spec().docs(bundled)
    assert {"mine.yaml"} < written and len(written) > len(pointed.files)
    document = yaml.safe_load((tmp_path / "architecture" / "mine" / "mine.yaml").read_text())
    pages = document["docs"]["pages"].values()
    sources = [page["from"] if isinstance(page, dict) else page for page in pages if not isinstance(page, dict) or "from" in page]
    assert all((tmp_path / "architecture" / "mine" / source).is_file() for source in sources)


def test_the_output_says_where_it_went_what_line_to_add_and_what_to_do_next(tmp_path):
    result = runner.invoke(app, ["profile", "new", "mine", "--from", "web"])
    assert result.exit_code == 0, result.output
    assert "architecture/mine/" in result.output and "mine.yaml" in result.output
    assert 'profile = "architecture/mine/mine.yaml"' in result.output and "[tool.xarch]" in result.output
    steps = result.output.split("next:")[1]
    assert steps.index("edit") < steps.index("xarch profile explain") < steps.index("xarch profile check")


def test_pyproject_is_never_written_so_the_profile_in_force_does_not_change(tmp_path):
    runner.invoke(app, ["profile", "new", "mine", "--from", "web"])
    assert (tmp_path / "pyproject.toml").read_text() == '[tool.xarch]\nprofile = "cli"\n'


def test_the_folder_is_chosen_with_out_and_recorded_relative_to_the_project(tmp_path):
    result = runner.invoke(app, ["profile", "new", "mine", "--from", "cli", "--out", "rules/mine"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "rules" / "mine" / "mine.yaml").is_file()
    assert 'profile = "rules/mine/mine.yaml"' in result.output


def test_a_second_copy_over_the_first_writes_nothing_and_says_which_files_exist(tmp_path):
    runner.invoke(app, ["profile", "new", "mine", "--from", "cli"])
    folder = tmp_path / "architecture" / "mine"
    (folder / "mine.yaml").write_text("edited\n")
    again = runner.invoke(app, ["profile", "new", "mine", "--from", "cli"])
    assert again.exit_code == 2
    assert "architecture/mine/mine.yaml" in again.output and "already exist" in again.output
    assert (folder / "mine.yaml").read_text() == "edited\n"


def test_nothing_is_written_when_one_file_exists(tmp_path):
    (tmp_path / "architecture" / "mine").mkdir(parents=True)
    (tmp_path / "architecture" / "mine" / "agents.md").write_text("mine\n")
    refused = runner.invoke(app, ["profile", "new", "mine", "--from", "cli"])
    assert refused.exit_code == 2
    assert [p.name for p in (tmp_path / "architecture" / "mine").iterdir()] == ["agents.md"]


def test_an_unknown_bundled_profile_and_a_bad_name_are_refused(tmp_path):
    assert runner.invoke(app, ["profile", "new", "mine", "--from", "nope"]).exit_code == 2
    assert runner.invoke(app, ["profile", "new", "a b", "--from", "cli"]).exit_code == 2
    assert not (tmp_path / "architecture").exists()
    assert runner.invoke(app, ["profile", "new", "mine"]).exit_code == 2
