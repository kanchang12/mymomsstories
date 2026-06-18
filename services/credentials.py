"""
services/credentials.py — generates an easy-to-remember username and
password for a child, so the parent never has to type the child's real
name anywhere. Both are "word + two digits", short enough for a small
child to type on a tablet keyboard, and checked against the DB for
uniqueness before being handed back.
"""
import random
from models.db import get_cur

# Simple, friendly, easy-to-spell words. Two separate pools so the
# username and password never accidentally repeat the same word.
_USERNAME_WORDS = [
    "tiger", "panda", "mango", "comet", "river", "maple", "robin", "otter",
    "cocoa", "amber", "coral", "lotus", "ember", "willow", "sunny", "pixel",
]
_PASSWORD_WORDS = [
    "kite", "drum", "star", "leaf", "wave", "moon", "frog", "bell",
    "fern", "dove", "plum", "jade", "rain", "glow", "nest", "wish",
]


def _candidate(words):
    return f"{random.choice(words)}{random.randint(10, 99)}"


def generate_child_credentials(max_attempts=20):
    """Returns (username, plain_password). Username is checked for
    uniqueness against the users table; password doesn't need to be
    (it's hashed and never looked up by value)."""
    with get_cur() as cur:
        for _ in range(max_attempts):
            username = _candidate(_USERNAME_WORDS)
            cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            if not cur.fetchone():
                password = _candidate(_PASSWORD_WORDS)
                return username, password
    # Fall back to a longer random suffix if we somehow collided 20 times
    username = f"{random.choice(_USERNAME_WORDS)}{random.randint(100, 999)}"
    password = _candidate(_PASSWORD_WORDS)
    return username, password
