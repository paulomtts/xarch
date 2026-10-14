# xarch

Check and scaffold the architecture described in `docs/project/architecture.md`: bounded modules under
`modules/`, the rings around them, and the dependency rules of section 5.

## Commands

```
xarch init [--app PATH] [--profile cli|web]                # create the top-level skeleton and project docs; never overwrites
xarch new-module NAME [--app PATH] [--profile cli|web]     # create a module with its full skeleton
xarch check [--app PATH] [--profile cli|web]               # report import-rule and structure violations
```

`--app` defaults to `app` (relative to the working directory). `check` exits 0 when clean, 1 with violations,
and 2 on a usage error (a missing app folder, an unknown profile, an unreadable `pyproject.toml`). `init` and
`new-module` exit 2 when they refuse (bad module name, module already exists, no `modules/` yet).

## Profiles

A profile names the entry-point folder, the part that drives the modules. Everything else is the same.

| Profile | Top level |
|---|---|
| `cli` (default) | `bootstrap/` (`migrations/`), `kernel/`, `modules/`, `platform/`, `cli/` (`commands/`) |
| `web` | `bootstrap/` (`migrations/`), `kernel/`, `modules/`, `platform/`, `web/` (`routes/`, `i18n/`, `ui/`) |

The entry point follows the same rule in both: it may import any module's `controller` and `contract/`,
`kernel/`, and itself. Violations name the real folder, e.g. `web/ may not import platform/`.

The profile is chosen in this order:

1. `--profile` on the command;
2. `profile` under `[tool.xarch]` in the nearest `pyproject.toml`, looked up from the folder holding the app
   folder upward (the nearest `pyproject.toml` decides, even when it has no `[tool.xarch]` table);
3. `cli`.

```toml
[tool.xarch]
profile = "web"
```

## A protocol, not a closed world

`check` requires what the profile demands and is not bothered by anything else.

- Required: every top-level folder of the profile, and in every module `contract/`, `domain/`,
  `application/controller.py`, `application/services/`, `application/ports/` and `adapters/`. A missing one is
  reported, e.g. `app: missing web/` or `app/modules/docs: missing application/ports/`.
- Enforced: the section 5 import table between the parts the profile knows.
- Ignored: extra top-level folders, extra files or folders directly inside a module or `application/`
  (e.g. `modules/a/helpers.py`, `modules/a/utils/`, `application/helpers.py`), files at the app root. Files in
  places the profile does not govern are not checked, and imports into such places are not reported. Under
  `cli`, a `web/` folder is just an extra, and the other way round.
- Extra files and subfolders inside a known part (e.g. `domain/rules/x.py`) are welcome too; they belong to that
  part, so their imports are checked as that part's.

## Project docs

`init` also writes the project docs beside the app folder (in the folder holding it), from short templates:
a title, the question the document answers, and fixed section headings. `testing.md` is written as content
instead, since the rings fix which tests each part admits; only its driver row depends on the profile.
Existing files are skipped, never overwritten, and extras (e.g. `.obsidian/`) are left alone.

```
docs/project/
  statement.md  domain.md  design.md  architecture.md  testing.md  requirements.md
  adrs/0000-template.md
  artifacts/{standards,audits,taxonomy,modules,guards}/_template.md
```

Copy a folder's template to start a new document of that kind. `new-module` does not touch the docs, and
`check` does not require them: they are not part of the app structure.

## Development

```
uv run pytest tests
uv tool install --editable . --reinstall     # refresh the system-wide `xarch`
```

`tests/architecture/test_self_check.py` runs xarch on its own source, which follows the architecture it enforces
with the `cli` profile.
