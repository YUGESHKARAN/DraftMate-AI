def is_valid_post_description(text: str):

    if not text or len(text.split()) < 8:
        return False

    banned_patterns = [
        "who is",
        "what is the capital",
        "tell me a joke",
        "weather",
        "movie",
        "song",
        "politics"
    ]

    text_lower = text.lower()

    for pattern in banned_patterns:
        if pattern in text_lower:
            return False

    return True