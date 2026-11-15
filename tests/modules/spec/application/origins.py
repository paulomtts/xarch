"""The bundled profiles the origin of a custom one is found against: base, with three tiered parts, guards and a
pinned init file, and other, with one part."""
TESTING = {"files": ["test_*.py"], "functions": "test_*", "skips": ["pytest.mark.skip", "pytest.mark.xfail"]}
TIER = {"proves": "a rule", "litmus": "Does it call a rule?", "apply_forbidden": True, "types_only": ["store"]}
PARTS = {"core": {"path": "core", "role": "rules", "may_import": [], "forbidden": "pure", "tier": "unit"},
         "store": {"path": "store", "role": "storage", "may_import": ["core"], "libraries": ["sqlmodel"],
                   "tier": "unit"},
         "edge": {"path": "edge", "role": "entry", "may_import": "everything", "libraries": "everything",
                  "untested": "it only wires"}}
BASE = {"xarch": 2, "name": "base", "parts": PARTS, "forbidden": {"pure": ["time.time", "socket"]},
        "testing": TESTING, "tiers": {"unit": TIER}, "guards": {"no-comments": {}},
        "files": {"tests/test_rules.py": {"from": "guard.py", "pinned": True}}}
OFF = ("package-only", "scenario-coverage", "stand-ins", "closed-tree", "no-duplicates", "no-twins", "dead-code",
       "pass-through", "private-imports")
OTHER = {"xarch": 2, "name": "other", "parts": {"web": {"path": "web", "role": "all"}}}


def part(name: str, **changes) -> dict:
    return {**PARTS, name: {**PARTS[name], **changes}}
