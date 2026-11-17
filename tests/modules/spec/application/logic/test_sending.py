"""The top-level `review` key: the files review never sends (`review.never`) and the texts it hides (`review.mask`),
each as written, and every way of writing one wrong refused at its address."""
import pytest

from tests.modules.spec.profiles import layered, parsed, problems


def test_a_profile_without_review_never_holds_back_or_hides_anything():
    architecture = parsed(layered())
    assert (architecture.never, architecture.mask) == ((), ())


def test_the_paths_review_never_sends_and_the_texts_it_hides_load_as_written_in_the_order_of_the_file():
    architecture = parsed(layered(review={"never": ["src/documents/drafts", "**/secrets", "shared/*_keys.py"],
                                          "mask": ["Northwind", "DOC-*"]}))
    assert architecture.never == ("src/documents/drafts", "**/secrets", "shared/*_keys.py")
    assert architecture.mask == ("Northwind", "DOC-*")


def test_either_key_may_be_written_alone():
    assert parsed(layered(review={"mask": ["Northwind"]})).never == ()
    assert parsed(layered(review={"never": ["src/drafts"]})).mask == ()


NOT_A_PATH = ("is not a path below the app: write its steps with /, * for any text inside one step and ** for any "
              "number of folders, such as documents/drafts")
NOT_A_TEXT = "is not a text to hide: write one line of text, * for any run of letters, digits, _, - and ."


@pytest.mark.parametrize("review, problem", [
    pytest.param(["src/drafts"], "review: must be a mapping {never, mask}: the files review never sends and the texts "
                                 "it hides before it sends", id="a list instead of a mapping"),
    pytest.param({"never": [], "hide": []}, "review: unknown key 'hide': use mask, never", id="an unknown key"),
    pytest.param({"never": "src/drafts"}, "review.never: must be a list of paths below the app, such as "
                                          "[documents/drafts, '**/secrets']", id="a path instead of a list"),
    pytest.param({"never": [""]}, f"review.never: '' {NOT_A_PATH}", id="an empty path"),
    pytest.param({"never": [3]}, f"review.never: 3 {NOT_A_PATH}", id="a path that is no text"),
    pytest.param({"never": ["/src/drafts"]}, f"review.never: '/src/drafts' {NOT_A_PATH}",
                 id="a path that starts with a slash"),
    pytest.param({"never": ["src/../drafts"]}, f"review.never: 'src/../drafts' {NOT_A_PATH}", id="a path with .."),
    pytest.param({"never": ["./drafts"]}, f"review.never: './drafts' {NOT_A_PATH}", id="a path with ."),
    pytest.param({"never": ["src//drafts"]}, f"review.never: 'src//drafts' {NOT_A_PATH}",
                 id="a path with an empty step"),
    pytest.param({"never": ["src/drafts/"]}, f"review.never: 'src/drafts/' {NOT_A_PATH}",
                 id="a path ending in a slash"),
    pytest.param({"never": ["src/drafts\nshared"]}, f"review.never: 'src/drafts\\nshared' {NOT_A_PATH}",
                 id="a path of two lines"),
    pytest.param({"never": ["src/**drafts"]},
                 "review.never: 'src/**drafts': ** stands alone as a step, for any number of folders",
                 id="two stars inside a longer step"),
    pytest.param({"never": ["**"]}, "review.never: '**' holds back every file: name the files or folders review must "
                                    "not send", id="any number of folders alone"),
    pytest.param({"never": ["*/**"]}, "review.never: '*/**' holds back every file: name the files or folders review "
                                      "must not send", id="nothing but stars"),
    pytest.param({"never": ["src/drafts", "src/drafts"]}, "review.never: 'src/drafts' is listed twice",
                 id="the same path twice"),
    pytest.param({"mask": "Northwind"}, "review.mask: must be a list of texts to hide before review sends, such as "
                                        "[Northwind, 'DOC-*']", id="a text instead of a list"),
    pytest.param({"mask": [""]}, f"review.mask: '' {NOT_A_TEXT}", id="an empty text"),
    pytest.param({"mask": ["  "]}, f"review.mask: '  ' {NOT_A_TEXT}", id="a blank text"),
    pytest.param({"mask": [7]}, f"review.mask: 7 {NOT_A_TEXT}", id="a text that is no text"),
    pytest.param({"mask": ["North\nwind"]}, f"review.mask: 'North\\nwind' {NOT_A_TEXT}", id="a text of two lines"),
    pytest.param({"mask": ["*"]}, "review.mask: '*' would hide every word: write the text around the *",
                 id="a star alone"),
    pytest.param({"mask": ["* *"]}, "review.mask: '* *' would hide every word: write the text around the *",
                 id="stars and spaces"),
    pytest.param({"mask": ["Northwind", "Northwind"]}, "review.mask: 'Northwind' is listed twice",
                 id="the same text twice"),
])
def test_a_badly_written_review_key_is_refused_at_its_address(review, problem):
    assert problems(layered(review=review)) == [f"layered.yaml: {problem}"]
