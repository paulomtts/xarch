# documents and moderation both compare titles this way
def normalized(title: str) -> str:
    return " ".join(title.split()).casefold()

def same_title(one: str, other: str) -> bool:
    return normalized(one) == normalized(other)
