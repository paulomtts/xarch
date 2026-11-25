"""The hooks `xarch hook claude` prints for Claude Code's settings (`.claude/settings.json`): after each edit or write
(PostToolUse, matched on `Edit|Write`), the check of the file it wrote, read from the hook's input with jq; before the
agent stops (Stop), the whole check under --strict, what the guard test runs, unless Claude Code is already going on
because of this hook (`stop_hook_active`), so that it never loops. Each runs from the project's folder
(`$CLAUDE_PROJECT_DIR`), writes the check's output on stderr and exits 2 when the check does not pass: Claude Code
then hands that output back to the agent, after the edit, or as the reason it may not stop yet."""
from __future__ import annotations

from xarch.cli.reports.document import document


def claude_hooks(xarch: str) -> str:
    """The hooks as the JSON document Claude Code's settings hold, running xarch as the command xarch says."""
    edited = (f"cd \"$CLAUDE_PROJECT_DIR\" && jq -r '.tool_input.file_path' | {xarch} check --files-from - >&2 "
              "|| exit 2")
    stopping = (f"[ \"$(jq -r '.stop_hook_active')\" = true ] && exit 0; "
                f"cd \"$CLAUDE_PROJECT_DIR\" && {xarch} check --strict >&2 || exit 2")
    return document({"hooks": {
        "PostToolUse": [{"matcher": "Edit|Write", "hooks": [{"type": "command", "command": edited}]}],
        "Stop": [{"hooks": [{"type": "command", "command": stopping}]}]}})
