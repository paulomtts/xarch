"""What review reads of a profile, from spec's contract: each part of the profile view, in order, with its folder,
litmus, role and line (the profile's, else spec's default), and what review may send; a profile spec refuses raises
Refused with spec's reason."""
import pytest

from xarch.kernel.source import CommentSpan, Import
from xarch.modules.review.adapters.spec_profile import SpecWords
from xarch.modules.review.domain.errors import Refused
from xarch.modules.review.domain.published import SCORE, Choice, Option
from xarch.modules.review.domain.values import CodeFile, EvalText, PartText, Words
from xarch.modules.spec.contract import (
    Eval,
    ExampleFile,
    ExamplesRead,
    ExamplesResult,
    PartView,
    ProfileRefused,
    ProfileResult,
    ProfileView,
)
from xarch.profile_values.checks import APP, Condition, Scope

VIEW = ProfileView(parts=(PartView("core", ("core",), (), "the rules", "Is it a rule?", "core/"),
                          PartView("api", ("src", "*", "api"), (), "handlers", shown="api/ of src/<module>")),
                   never=("src/*/drafts", "**/secrets"), mask=("Northwind",), lines={"api": 0.2})


class Spec:
    """Spec's controller as review's adapter uses it, answering from a fixed result."""

    def __init__(self, result: ProfileResult, examples: ExamplesResult = ExamplesRead((), ())):
        self._result, self._examples = result, examples

    def profile(self, location: str) -> ProfileResult:
        return self._result

    def examples(self, location: str) -> ExamplesResult:
        return self._examples


def test_each_part_is_read_with_its_folder_litmus_role_and_line_in_order_and_what_review_may_send_as_written():
    assert SpecWords(Spec(VIEW)).words("p") == Words(
        (PartText("core", "core/", "Is it a rule?", "the rules", 0.3),
         PartText("api", "api/ of src/<module>", "", "handlers", 0.2, by_hand=True)),
        ("src/*/drafts", "**/secrets"), ("Northwind",), examples_root="app")


def test_each_part_of_a_group_read_alike_is_read_with_the_other_parts_of_its_group_in_the_group_s_order():
    parts = (PartView("core", ("core",), (), "the rules"), PartView("api", ("api",), (), "handlers"),
             PartView("kernel", ("kernel",), (), "shared rules"))
    words = SpecWords(Spec(ProfileView(parts=parts, alike=(("kernel", "core"),)))).words("p")
    assert [(part.name, part.alike) for part in words.parts] == [("core", ("kernel",)), ("api", ()),
                                                                  ("kernel", ("core",))]


def test_a_profile_spec_refuses_is_refused_with_spec_s_reason():
    with pytest.raises(Refused, match="gone: no such file"):
        SpecWords(Spec(ProfileRefused("gone: no such file"))).words("gone")


PURITY = Eval("How far does it reach?", "score", tuple((str(n), f"level {n}") for n in range(5)), ("3", "4"), "function",
              Scope(APP, "core", "", (Condition("placed"),)), (Condition("public"), Condition("named", "run*", True)),
              0.7, "{name} ({value})", "read it", (("core/a.py", "x\n"),), (("core/b.py", "y\n"),))


def test_each_eval_of_the_profile_own_is_read_with_its_question_its_form_and_what_it_reads_as_one_text():
    words = SpecWords(Spec(ProfileView(parts=(), evals={"purity": PURITY}))).words("p")
    assert words.evals == (EvalText(
        "purity", Choice("How far does it reach?", tuple(Option(str(n), f"level {n}") for n in range(5)), SCORE),
        ("3", "4"), 0.7, "{name} ({value})", "read it", (("core/a.py", "x\n"),), (("core/b.py", "y\n"),),
        "function | core | where | placed | keep | public | not named run*"),)


def test_the_files_placement_is_held_to_are_read_with_their_part_code_and_imports_and_a_refusal_is_refused():
    clock = Import(1, ("app", "kernel", "time"), ("Clock",))
    noted = (CommentSpan(1, 2, 7),)
    read = ExamplesRead((ExampleFile("core/a.py", "core", "x\n", (clock,)),),
                        (ExampleFile("api/b.py", "api", "y  # b\n", comments=noted),))
    assert SpecWords(Spec(VIEW, read)).examples("p") == ((CodeFile("core/a.py", "core", "x\n", (clock,)),),
                                                          (CodeFile("api/b.py", "api", "y  # b\n", comments=noted),))
    with pytest.raises(Refused, match="gone: no such file"):
        SpecWords(Spec(VIEW, ProfileRefused("gone: no such file"))).examples("gone")
