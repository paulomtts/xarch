"""What a skeleton turns into on disk."""
from xarch.modules.scaffold.application.logic.plan import plan


def test_plan_writes_a_package_file_for_the_root_and_every_folder_and_every_file_parents_first():
    entries = [(("kernel",), True), (("kernel", "logic"), True), (("main.src",), False)]
    assert plan(entries, "index.src") == [("index.src",), ("kernel", "index.src"), ("kernel", "logic", "index.src"),
                                          ("main.src",)]


def test_plan_writes_no_package_file_when_the_language_has_none():
    entries = [(("kernel",), True), (("kernel", "logic"), True), (("main.src",), False)]
    assert plan(entries, "") == [("main.src",)]
