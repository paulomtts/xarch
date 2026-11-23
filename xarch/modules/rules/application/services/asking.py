from __future__ import annotations

from xarch.modules.rules.application.logic.asked import made, named, project, span
from xarch.modules.rules.application.logic.engine import kept
from xarch.modules.rules.application.ports.profile import Profiles
from xarch.modules.rules.application.ports.source_tree import SourceTree
from xarch.modules.rules.contract import FactKept, FactsKept, FileKept, KeepFacts
from xarch.modules.rules.domain.errors import ChecksRefused


class AskingService:
    """Finds what an eval of the profile's own reads in files given as text, for the module that asks it: each fact
    of the kind it reads, in its scope, passing what it keeps."""

    def __init__(self, tree: SourceTree, profiles: Profiles):
        self._tree, self._profiles = tree, profiles

    def kept(self, cmd: KeepFacts) -> FactsKept:
        """Raises ChecksRefused for an eval the profile does not write, or one that cannot be made."""
        profile = self._profiles.profile(cmd.profile)
        if cmd.asked not in profile.asked:
            raise ChecksRefused((f"evals.{cmd.asked}: the profile writes no eval of its own of this id",))
        rule, problems = made(cmd.asked, profile.asked[cmd.asked])
        if rule is None:
            raise ChecksRefused(tuple(problems))
        parsed = [(path, self._tree.parsed(text, profile.language.standard_modules)) for path, text in cmd.files]
        found = kept(rule, project(parsed, profile, cmd.app, (rule,)), profile)
        return FactsKept(tuple(FileKept(path, file.imports, tuple(
            FactKept(*span(fact, file.pieces), named(fact)) for read, fact in found if "/".join(read.file.path) == path),
            tuple(comment.span for comment in file.comments)) for path, file in parsed))
