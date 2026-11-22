"""A profile ships a folder of ready-made files with `init`: copied as they are, inside a part when it says so, checked
like any code, and every file a bundled profile ships is there in a fresh project that passes the check."""
from pathlib import Path

import pytest

from tests.bootstrap.project import app_check
from xarch.bootstrap.wiring import build_controllers
from xarch.modules.scaffold.contract import InitProject, NewInstance, Scaffolded

PROFILE = """\
name: presets
never:
  nothing_printed: [builtins.print]
parts:
  kernel: {path: kernel, role: primitives}
  ui:
    path: web/ui
    role: pages
    uses: {never: nothing_printed}
files:
  "{{app}}/web/ui/design/": {from: presets/design/}
  "notes.txt": {from: presets/design/tokens.css, fill: false}
"""
FILLED = '  "docs/design/": {from: presets/design/, fill: true}\n'
FONT = bytes(range(256))
TOKENS = ":root { --brand: #036; } /* {{app}} stays as written */\n"


def profile_in(tmp_path: Path, palette: bytes = b"BRAND = '#036'\n", font: bytes = FONT, filled: bool = False) -> Path:
    design = tmp_path / "presets" / "design"
    (design / "fonts").mkdir(parents=True)
    (design / "tokens.css").write_text(TOKENS)
    (design / "palette.py").write_bytes(palette)
    (design / "fonts" / "serif.woff").write_bytes(font)
    (tmp_path / "presets.yaml").write_text(PROFILE + (FILLED if filled else ""))
    return tmp_path / "presets.yaml"


def init(app: Path, profile: str | Path) -> Scaffolded:
    result = build_controllers().scaffold.init(InitProject(app, str(profile), Path.cwd()))
    assert isinstance(result, Scaffolded)
    return result


def problems(app: Path, profile: Path) -> list[tuple[str, str]]:
    return [(v.file, v.rule) for v in app_check(app, str(profile)).violations]


def test_a_preset_is_copied_below_the_app_folder_with_its_tree_and_every_byte_kept(tmp_path):
    profile = profile_in(tmp_path)
    report = init(tmp_path / "shop", profile).report
    design = tmp_path / "shop" / "web" / "ui" / "design"
    assert (design / "fonts" / "serif.woff").read_bytes() == FONT
    assert (design / "tokens.css").read_text() == TOKENS
    assert {design / "tokens.css", design / "palette.py", design / "fonts" / "serif.woff"} <= set(report.created)


def test_a_preset_is_never_overwritten_and_a_second_init_skips_every_file(tmp_path):
    profile = profile_in(tmp_path)
    init(tmp_path / "shop", profile)
    edited = tmp_path / "shop" / "web" / "ui" / "design" / "tokens.css"
    edited.write_text("mine")
    report = init(tmp_path / "shop", profile).report
    assert edited.read_text() == "mine" and edited in report.skipped
    assert not [path for path in report.created if "design" in path.parts]


def test_the_python_file_of_a_preset_that_follows_its_part_passes_the_check(tmp_path):
    profile = profile_in(tmp_path)
    init(tmp_path / "shop", profile)
    assert problems(tmp_path / "shop", profile) == []


@pytest.mark.parametrize("palette, rule", [
    pytest.param(b"print('loaded')\n", "never-use", id="a name the part forbids"),
    pytest.param(b"from shop.kernel import x\n", "rules", id="an import the part's rules do not allow"),
])
def test_the_python_file_of_a_preset_that_breaks_its_part_is_reported(tmp_path, palette, rule):
    profile = profile_in(tmp_path, palette)
    init(tmp_path / "shop", profile)
    assert problems(tmp_path / "shop", profile) == [("shop/web/ui/design/palette.py", rule)]


def test_a_file_entry_that_does_not_fill_keeps_a_placeholder_and_a_folder_may_ask_to_be_filled(tmp_path):
    profile = profile_in(tmp_path, font=b"plain text", filled=True)
    init(tmp_path / "shop", profile)
    assert (tmp_path / "notes.txt").read_text() == TOKENS
    assert (tmp_path / "docs" / "design" / "tokens.css").read_text() == TOKENS.replace("{{app}}", "shop")


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_a_fresh_project_of_a_bundled_profile_has_every_shipped_file_and_passes_the_check(tmp_path, profile):
    app = tmp_path / "app"
    init(app, profile)
    controllers = build_controllers()
    assert isinstance(controllers.scaffold.new(NewInstance(app, "module", "documents", profile)), Scaffolded)
    shipped = controllers.spec.files(profile, "app").files
    assert shipped and all((tmp_path.joinpath(*file.path)).is_file() for file in shipped)
    checked = app_check(app, profile, tmp_path / "tests")
    assert checked.violations == ()
    assert checked.enforcement.init_files == ()
