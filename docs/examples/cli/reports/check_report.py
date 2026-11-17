from __future__ import annotations

from app.modules.rules.contract import AppChecked, CheckAppResult, CheckRefused, ChecksCannotRun


def check_text(result: CheckAppResult) -> str:
    match result:
        case AppChecked(violations=(), cycles=()):
            return f"xarch check: clean ({result.profile})"
        case AppChecked():
            return "\n".join([*_violations(result), *_cycles(result), _count(result)])
        case ChecksCannotRun(problems=problems):
            return "\n".join(["the checks cannot run:", *(f"  {problem}" for problem in problems)])
        case CheckRefused(reason=reason):
            return f"xarch check: {reason}"


def _violations(result: AppChecked) -> list[str]:
    return [f"{v.place.shown()}: {v.message} [{v.rule}]\n  fix: {v.fix}" for v in result.violations]


def _cycles(result: AppChecked) -> list[str]:
    return [f"cycle: {' -> '.join((*ring.modules, ring.modules[0]))}" for ring in result.cycles]


def _count(result: AppChecked) -> str:
    found = len(result.violations) + len(result.cycles)
    return f"{found} violation{'' if found == 1 else 's'}"
