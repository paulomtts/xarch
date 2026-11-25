"""The bundled profiles the origin of a custom one is found against: base, with three tiered parts, guards and a
pinned init file, and other, with one part."""
TESTING = {"files": ["test_*.py"], "functions": "test_*", "skips": ["pytest.mark.skip", "pytest.mark.xfail"]}
TIER = {"proves": "a rule", "litmus": "Does it call a rule?", "uses": {"apply_never": True}, "imports": {"types_only": ["store"]}}
PARTS = {"core": {"path": "core", "role": "rules", "imports": {"may": []}, "uses": {"never": "pure"}, "tests": "unit"},
         "store": {"path": "store", "role": "storage", "imports": {"may": ["core"], "libraries": ["sqlmodel"]},
                   "tests": "unit"},
         "edge": {"path": "edge", "role": "entry", "imports": {"may": "everything", "libraries": "everything"},
                  "untested": "it only wires"}}
BASE = {"name": "base", "parts": PARTS, "never": {"pure": ["time.time", "socket"]},
        "testing": TESTING, "tiers": {"unit": TIER}, "guards": {"no-comments": {}},
        "files": {"tests/test_rules.py": {"from": "guard.py", "pinned": True}}}
OFF = ("package-only", "scenario-coverage", "stand-ins", "closed-tree", "no-duplicates", "no-twins", "dead-code",
       "pass-through", "no-callbacks", "private-imports")
OTHER = {"name": "other", "parts": {"web": {"path": "web", "role": "all"}}}


def part(name: str, **changes) -> dict:
    return {**PARTS, name: {**PARTS[name], **changes}}
