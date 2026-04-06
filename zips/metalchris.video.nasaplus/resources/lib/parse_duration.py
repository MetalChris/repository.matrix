def parse_duration(duration_str):
    """
    Convert duration strings (HH:MM:SS or MM:SS) into seconds.
    Safe to reuse across add-ons.
    """
    if not duration_str:
        return 0

    parts = duration_str.strip().split(":")
    try:
        parts = [int(p) for p in parts]
    except ValueError:
        return 0

    if len(parts) == 3:
        hours, minutes, seconds = parts
    elif len(parts) == 2:
        hours = 0
        minutes, seconds = parts
    else:
        return 0

    return hours * 3600 + minutes * 60 + seconds
