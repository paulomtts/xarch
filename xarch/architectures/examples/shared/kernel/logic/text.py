# documents and moderation both compare titles this way
def normalized(text: str) -> str:
    return " ".join(text.split()).casefold()

def same_text(one: str, other: str) -> bool:
    return normalized(one) == normalized(other)

def shortened(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"
