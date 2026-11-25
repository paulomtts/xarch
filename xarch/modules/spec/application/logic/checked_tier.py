"""A tier as the checks read it: each part it tests as a target, in the tested file's own instance for a part of a
repeating folder, outside every instance for any other."""
from __future__ import annotations

from xarch.modules.spec.domain.values import Architecture, Tier
from xarch.profile_values.placement import Target
from xarch.profile_values.tiers import CheckedTier


def checked_tier(architecture: Architecture, tier: Tier) -> CheckedTier:
    subject = tuple(Target(s.part, "own" if architecture.parts[s.part].in_instance else "none", s.sub)
                    for s in tier.subject)
    return CheckedTier(tier.name, subject, tier.folder, tier.types_only, tier.apply_never, tier.proves, tier.may_touch,
                       tier.litmus, tier.one_file_per, tier.may_import, tier.must_import, tier.plain_tables,
                       tier.may_also_import)
