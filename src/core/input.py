# Keeps track of what key is down
keys_down = set()

def is_key_pressed(key):
    return key in keys_down

def safe_remove_key(key):
    """Safely remove a key from keys_down set if it exists."""
    if key in keys_down:
        keys_down.remove(key)
        return True
    return False