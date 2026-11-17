def normalized(title: str) -> str:     # documents and moderation both compare titles this way
    return " ".join(title.split()).casefold()

def same_title(one: str, other: str) -> bool:
    return normalized(one) == normalized(other)
