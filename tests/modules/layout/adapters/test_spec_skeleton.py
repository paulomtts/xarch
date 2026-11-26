"""Layout's Skeleton read from spec's contract: the folders and files of the top level apart, and what every instance
of a repeating folder holds, as its leaves; and how the language names a folder."""
from dataclasses import replace

from xarch.modules.layout.adapters.spec_skeleton import SpecSkeleton
from xarch.modules.layout.domain.structure import Allowed, Beside, Naming, Pattern, Word
from xarch.modules.layout.domain.structure import Counterpart as Layout
from xarch.modules.spec.contract import AcceptedPath, Counterpart, Entry, PathPattern, Repeating, Skeleton

SKELETON = Skeleton(
    top_level=(Entry(("kernel",), True, True), Entry(("modules",), True, True), Entry(("__main__.py",), False, True)),
    repeating=(Repeating("module", ("modules",), (Entry(("domain",), True, True), Entry(("application",), True, False),
                                                  Entry(("application", "controller.py"), False, True))),),
    title="Python", package_file="__init__.py", private="_", reserved=frozenset({"class"}), names=r"\w+")


class Spec:
    """Spec's controller as layout's adapter uses it: the skeleton of the profile asked for."""

    def skeleton(self, profile: str) -> Skeleton:
        return SKELETON


def test_the_top_level_is_split_into_folders_and_files():
    skeleton = SpecSkeleton(Spec())
    assert skeleton.top_level("cli") == [("kernel",), ("modules",)]
    assert skeleton.top_level_files("cli") == [("__main__.py",)]


def test_each_repeating_folder_is_named_by_its_root_and_holds_its_leaves():
    skeleton = SpecSkeleton(Spec())
    assert skeleton.each_roots("cli") == [("modules",)]
    assert skeleton.each_parts("cli", ("modules",)) == [(("domain",), True), (("application", "controller.py"), False)]


def test_the_naming_is_what_a_name_may_be_and_how_a_private_one_starts():
    assert SpecSkeleton(Spec()).naming("cli") == Naming(r"\w+", "_")


def test_without_beside_there_is_no_beside_and_with_it_the_test_files_and_the_kept_folders():
    assert SpecSkeleton(Spec()).beside("cli") is None
    near = replace(SKELETON, beside=True, test_files=("test_*.py",), kept=(("architecture",), ("fakes",)))

    class Near:
        def skeleton(self, profile: str) -> Skeleton:
            return near

    assert SpecSkeleton(Near()).beside("cli") == Beside(("test_*.py",), (("architecture",), ("fakes",)))


OPTIONAL = Skeleton(
    top_level=(Entry(("kernel",), True, True), Entry(("api",), True, False, True), Entry(("api", "v1"), True, True,
                                                                                     when=("api",)),
               Entry(("main.py",), False, True, True)),
    repeating=(Repeating("module", ("modules",), (Entry(("domain",), True, True),
                                                  Entry(("config.py",), False, True, True),
                                                  Entry(("hooks",), True, False, True),
                                                  Entry(("hooks", "run.py"), False, True, when=("hooks",)))),))


class Sparse:
    def skeleton(self, profile: str) -> Skeleton:
        return OPTIONAL


def test_an_optional_part_is_required_nowhere_and_what_it_holds_only_where_it_is_there():
    skeleton = SpecSkeleton(Sparse())
    assert (skeleton.top_level("p"), skeleton.top_level_files("p")) == ([("kernel",), ("api", "v1")], [])
    assert skeleton.each_parts("p", ("modules",)) == [(("domain",), True), (("hooks", "run.py"), False)]
    assert skeleton.when("p") == {("api", "v1"): ("api",)}
    assert skeleton.when("p", ("modules",)) == {("hooks", "run.py"): ("hooks",)}


PAIRED = Skeleton(
    top_level=(Entry(("adapters",), True, False), Entry(("adapters", "sql"), True, False),
               Entry(("adapters", "sql", "models"), True, True, True), Entry(("adapters", "sql", "engine.py"), False,
                                                                             True)),
    repeating=(Repeating("store", ("adapters", "sql"), (Entry(("repo.py",), False, True),)),
               Repeating("module", ("modules",), ())),
    counterparts=(Counterpart("x", PathPattern(("adapters", "sql", "<store>"), True),
                              PathPattern(("tests", "conformance", "<store>"), True),
                              (PathPattern(("tests", "fakes", "<store>"), True),),
                              (AcceptedPath(("adapters", "sql", "cart"), "no contract yet"),
                               AcceptedPath(("tests", "fakes", "old"), "w")), "{source}", "fix {source}"),))


class Paired:
    def skeleton(self, profile: str) -> Skeleton:
        return PAIRED


def test_a_counterpart_reads_a_path_written_tests_path_as_below_the_tests_root():
    assert SpecSkeleton(Paired()).counterparts("p") == [
        Layout("x", Pattern(("adapters", "sql", "<store>"), False, True), Pattern(("conformance", "<store>"), True, True),
               (Pattern(("fakes", "<store>"), True, True),),
               (Allowed(("adapters", "sql", "cart"), False, "adapters/sql/cart/", "no contract yet"),
                Allowed(("fakes", "old"), True, "tests/fakes/old/", "w")), "{source}", "fix {source}")]


def test_a_repeating_folder_s_word_knows_the_names_the_layout_writes_beside_its_instances():
    assert SpecSkeleton(Paired()).words("p") == [Word("store", ("adapters", "sql"), frozenset({"models", "engine.py"})),
                                                  Word("module", ("modules",), frozenset())]
