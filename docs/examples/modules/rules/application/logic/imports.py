from __future__ import annotations

from collections.abc import Iterable, Mapping

from app.kernel.logic.placement import part_of
from app.kernel.source import Import
from app.kernel.violations import Place, Violation
from app.modules.rules.domain.rule import ImportRule, ImportSeen


def seen_imports(file: str, imports: Iterable[Import], patterns: Mapping[str, tuple[str, ...]],
                 package: str) -> tuple[ImportSeen, ...]:
    importer = part_of(tuple(file.split("/")), patterns)
    if importer is None:
        return ()
    found = []
    for imp in imports:
        steps = tuple(imp.module.split("."))
        target = part_of(steps[1:], patterns) if steps[0] == package else None
        if target is not None and target != importer:
            found.append(ImportSeen(Place(file, imp.line), importer, target))
    return tuple(found)


def forbidden_imports(seen: Iterable[ImportSeen], rules: Mapping[str, ImportRule]) -> tuple[Violation, ...]:
    found = []
    for one in seen:
        rule = rules.get(one.importer)
        if rule is None or rule.allows(one.target):
            continue
        found.append(Violation(one.place, "rules", f"{one.importer} imports {one.target}, which it may not import",
                               f"move what {one.importer} needs from {one.target} inward, or import it from a part "
                               f"parts.{one.importer}.may_import lists"))
    return tuple(found)
