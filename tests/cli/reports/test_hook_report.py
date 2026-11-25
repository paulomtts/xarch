"""The Claude Code hooks `xarch hook claude` prints: after each edit, the check of the file edited; before the agent
stops, the whole check under --strict; each failing with exit 2 and the check's output on stderr, which Claude Code
hands back to the agent."""
import json

from xarch.cli.reports.hook_report import claude_hooks

EDITED = ("cd \"$CLAUDE_PROJECT_DIR\" && jq -r '.tool_input.file_path' | xarch check --files-from - >&2 || exit 2")
STOPPING = ("[ \"$(jq -r '.stop_hook_active')\" = true ] && exit 0; "
            "cd \"$CLAUDE_PROJECT_DIR\" && xarch check --strict >&2 || exit 2")


def test_the_hooks_check_the_file_each_edit_wrote_and_the_whole_app_before_the_agent_stops():
    assert json.loads(claude_hooks("xarch")) == {"hooks": {
        "PostToolUse": [{"matcher": "Edit|Write", "hooks": [{"type": "command", "command": EDITED}]}],
        "Stop": [{"hooks": [{"type": "command", "command": STOPPING}]}]}}


def test_the_command_that_runs_xarch_is_the_one_given():
    hooks = json.loads(claude_hooks("uv run xarch"))["hooks"]
    assert "| uv run xarch check --files-from -" in hooks["PostToolUse"][0]["hooks"][0]["command"]
    assert "&& uv run xarch check --strict" in hooks["Stop"][0]["hooks"][0]["command"]
