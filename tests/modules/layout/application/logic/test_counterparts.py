"""What lies with what (counterparts), held against the files below the app and below the tests: each match of a
counterpart's `for`, where every path of its `when` matches too, with no match of its `has` is a finding at it; a
placeholder binds the text of a step or part of one, the same text wherever it is written twice, and a repeating
folder's word at that folder's place binds only its instances; an entry of `accepted` waives the finding of its source,
and is a finding itself once it waives none; how many sources each counterpart read is counted."""
from tests.modules.layout.builders import PYTHON_NAMING
from xarch.kernel.violations import Violation
from xarch.modules.layout.application.logic.counterparts import paired
from xarch.modules.layout.domain.published import Waived
from xarch.modules.layout.domain.structure import Allowed, Counterpart, Pattern, Word

SQL = ("adapters", "sql")
WORDS = (Word("store", SQL, frozenset({"models", "alembic"})),)


def at_app(path: str) -> Pattern:
    return Pattern(tuple(path.strip("/").split("/")), False, path.endswith("/"))


def at_tests(path: str) -> Pattern:
    return Pattern(tuple(path.strip("/").split("/")), True, path.endswith("/"))


def steps(*paths: str) -> list[tuple[str, ...]]:
    return [tuple(path.split("/")) for path in paths]


CONFORMANCE = Counterpart("fakes-have-conformance", at_app("adapters/sql/<store>/"), at_tests("conformance/<store>/"),
                          (at_tests("fakes/<store>/"),))
APP = steps("adapters/sql/cart/repo.py", "adapters/sql/shop/repo.py", "adapters/sql/models/base.py",
            "adapters/sql/alembic/env.py", "adapters/sql/engine.py")


def findings(entry: Counterpart, app_files, test_files, words=WORDS) -> list[str]:
    return [f"{v.file}: {v.message}" for v in paired([entry], app_files, test_files, words, PYTHON_NAMING, "app",
                                                      "tests")[0]]


def test_a_source_whose_when_matches_and_that_has_no_counterpart_is_a_finding_at_it():
    violations, waived, read = paired([CONFORMANCE], APP, steps("fakes/cart/fake.py", "fakes/shop/fake.py", "conformance/shop/test_x.py"),
                   WORDS, PYTHON_NAMING, "app", "tests")
    assert violations == (
        Violation("app/adapters/sql/cart", 0, "adapters/sql/cart/ has no tests/conformance/cart/, though it has "
                                              "tests/fakes/cart/ (counterparts.fakes-have-conformance)", "counterpart",
                  "create tests/conformance/cart/, or name adapters/sql/cart/ under "
                  "counterparts.fakes-have-conformance.accepted with the reason it has none"),)
    assert read == (("fakes-have-conformance", 2),)


def test_a_source_whose_when_does_not_match_needs_no_counterpart():
    assert findings(CONFORMANCE, APP, steps("fakes/shop/fake.py", "conformance/shop/t.py")) == []


def test_a_word_at_its_folder_s_place_binds_only_instances_never_a_folder_the_layout_names_beside_them():
    entry = Counterpart("x", at_app("adapters/sql/<store>/"), at_tests("conformance/<store>/"))
    assert findings(entry, APP, []) == [
        "app/adapters/sql/cart: adapters/sql/cart/ has no tests/conformance/cart/ (counterparts.x)",
        "app/adapters/sql/shop: adapters/sql/shop/ has no tests/conformance/shop/ (counterparts.x)"]


def test_a_placeholder_off_its_word_s_place_binds_any_name():
    entry = Counterpart("x", at_tests("fakes/<store>/"), at_app("adapters/sql/<store>/"))
    assert findings(entry, APP, steps("fakes/models/fake.py", "fakes/cart/fake.py")) == []
    assert findings(entry, APP, steps("fakes/orders/fake.py")) == [
        "tests/fakes/orders: tests/fakes/orders/ has no adapters/sql/orders/ (counterparts.x)"]


def test_a_placeholder_binds_part_of_a_file_name():
    entry = Counterpart("x", at_app("ports/<port>_repo.py"), at_app("adapters/sql/*/<port>_repo.py"))
    files = steps("ports/entry_repo.py", "ports/clock.py", "ports/order_repo.py", "adapters/sql/shop/entry_repo.py")
    assert findings(entry, files, []) == [
        "app/ports/order_repo.py: ports/order_repo.py has no adapters/sql/*/order_repo.py (counterparts.x)"]


def test_a_star_in_has_matches_any_text_and_several_matches_satisfy():
    entry = Counterpart("x", at_app("adapters/sql/<store>/transaction.py"),
                        at_tests("conformance/<store>/test_*_transaction_contract.py"))
    files = steps("adapters/sql/cart/transaction.py", "adapters/sql/shop/transaction.py")
    contracts = steps("conformance/shop/test_a_transaction_contract.py", "conformance/shop/test_b_transaction_contract.py")
    assert findings(entry, files, contracts) == [
        "app/adapters/sql/cart/transaction.py: adapters/sql/cart/transaction.py has no "
        "tests/conformance/cart/test_*_transaction_contract.py (counterparts.x)"]


def test_a_folder_is_there_when_a_file_lies_below_it_and_a_file_in_its_place_is_none():
    entry = Counterpart("x", at_app("adapters/sql/<store>/"), at_tests("conformance/<store>/"))
    assert findings(entry, steps("adapters/sql/cart/repo.py"), steps("conformance/cart")) == [
        "app/adapters/sql/cart: adapters/sql/cart/ has no tests/conformance/cart/ (counterparts.x)"]
    assert findings(entry, steps("adapters/sql/cart/repo.py"), steps("conformance/cart/a/b.py")) == []


def test_a_file_pattern_matches_no_folder():
    entry = Counterpart("x", at_app("adapters/sql/<store>"), at_tests("conformance/<store>/"))
    assert paired([entry], APP, [], WORDS, PYTHON_NAMING, "app", "tests")[2] == (("x", 0),)


def test_a_placeholder_written_twice_binds_the_same_text():
    entry = Counterpart("x", at_app("modules/<m>/<m>_service.py"), at_tests("unit/<m>/"))
    files = steps("modules/docs/docs_service.py", "modules/docs/billing_service.py")
    assert findings(entry, files, []) == [
        "app/modules/docs/docs_service.py: modules/docs/docs_service.py has no tests/unit/docs/ (counterparts.x)"]


def test_a_private_or_cache_folder_never_binds():
    entry = Counterpart("x", at_app("modules/<m>/"), at_tests("unit/<m>/"))
    files = steps("modules/__pycache__/x.pyc", "modules/_support/x.py", "modules/docs/x.py")
    assert findings(entry, files, steps("unit/docs/test_x.py")) == []


def test_an_accepted_source_is_waived_with_its_reason():
    entry = Counterpart("x", at_app("adapters/sql/<store>/"), at_tests("conformance/<store>/"),
                        accepted=(Allowed(("adapters", "sql", "cart"), False, "adapters/sql/cart/", "no contract yet"),))
    violations, waived, read = paired([entry], APP, steps("conformance/shop/t.py"), WORDS, PYTHON_NAMING, "app", "tests")
    assert violations == ()
    assert waived == (Waived("counterpart", "app/adapters/sql/cart", "adapters/sql/cart/ has no "
                                   "tests/conformance/cart/ (counterparts.x)", "no contract yet", "counterparts.x.accepted"),)


def test_an_accepted_source_that_now_has_its_counterpart_or_is_gone_is_a_finding():
    entry = Counterpart("x", at_app("adapters/sql/<store>/"), at_tests("conformance/<store>/"),
                        accepted=(Allowed(("adapters", "sql", "cart"), False, "adapters/sql/cart/", "w"),
                                  Allowed(("adapters", "sql", "gone"), False, "adapters/sql/gone/", "w")))
    violations, waived, read = paired([entry], APP, steps("conformance/shop/t.py", "conformance/cart/t.py"), WORDS, PYTHON_NAMING, "app",
                   "tests")
    assert violations == (
        Violation("app/adapters/sql/cart", 0, "counterparts.x.accepted names adapters/sql/cart/, which now has its "
                                              "counterpart tests/conformance/cart/", "counterpart",
                  "drop the entry of adapters/sql/cart/ from counterparts.x.accepted"),
        Violation("app/adapters/sql/gone", 0, "counterparts.x.accepted names adapters/sql/gone/, which is no match of "
                                              "adapters/sql/<store>/ that needs a counterpart (counterparts.x)",
                  "counterpart", "drop the entry of adapters/sql/gone/ from counterparts.x.accepted"))



def test_an_accepted_source_written_with_the_app_folder_first_is_told_to_write_its_path_below_the_app():
    entry = Counterpart("x", at_app("adapters/sql/<store>/"), at_tests("conformance/<store>/"),
                        accepted=(Allowed(("app", "adapters", "sql", "cart"), False, "app/adapters/sql/cart/", "w"),))
    violations = paired([entry], APP, steps("conformance/shop/t.py"), WORDS, PYTHON_NAMING, "app", "tests")[0]
    assert [(v.file, v.fix) for v in violations if v.file == "app/app/adapters/sql/cart"] == [
        ("app/app/adapters/sql/cart",
         "write the path relative to the app: adapters/sql/cart/, not app/adapters/sql/cart/")]

def test_a_message_and_a_fix_of_the_profile_s_own_are_said_with_their_variables():
    entry = Counterpart("x", at_app("adapters/sql/<store>/"), at_tests("conformance/<store>/"), (at_tests("fakes/<store>/"),),
                        message="{store}: {source} lacks {expected} beside {when} ({key})", fix="write {expected}")
    violations = paired([entry], APP, steps("fakes/cart/f.py"), WORDS, PYTHON_NAMING, "app", "tests")[0]
    assert [(v.message, v.fix) for v in violations] == [
        ("cart: adapters/sql/cart/ lacks tests/conformance/cart/ beside tests/fakes/cart/ (counterparts.x)",
         "write tests/conformance/cart/")]


def test_for_in_a_message_or_a_fix_is_the_match_as_source_is():
    entry = Counterpart("x", at_app("adapters/sql/<store>/"), at_tests("conformance/<store>/"),
                        message="{for} has no {expected}", fix="give {for} its contract")
    violations = paired([entry], APP, None, WORDS, PYTHON_NAMING, "app", "tests")[0]
    assert [(v.message, v.fix) for v in violations][:1] == [
        ("adapters/sql/cart/ has no tests/conformance/cart/", "give adapters/sql/cart/ its contract")]


def test_with_no_tests_a_pattern_below_the_tests_matches_nothing():
    entry = Counterpart("x", at_tests("fakes/<store>/"), at_app("adapters/sql/<store>/"))
    violations, waived, read = paired([entry], APP, None, WORDS, PYTHON_NAMING, "app", None)
    assert (violations, read) == ((), (("x", 0),))
