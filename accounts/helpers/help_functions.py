def truncate(text: str, max_length: int) -> str:
    if not text:
        return ""

    if len(text) <= max_length:
        return text

    return text[: max_length - 3].rstrip() + "..."
