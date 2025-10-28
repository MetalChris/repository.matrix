def format_channel_name(slug: str) -> str:
    """
    Convert a channel slug into a nicely formatted name.
    Handles special capitalization cases like CW, UK, A&E, etc.
    """
    # Base capitalization
    name = slug.replace('-', ' ').title()

    # Map of special words to uppercase or custom forms
    special_cases = {
        "Cw": "CW",
        "Uk": "UK",
        "Er": "ER",
        "Ae": "A&E",
        "Tv": "TV",
        "Fbi": "FBI",
        "Acc": "ACC"
    }

    # Apply replacements
    name = " ".join(special_cases.get(word, word) for word in name.split())
    return name
