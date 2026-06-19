"""
services/content.py — loads language content from content/<code>.json files.
To add or edit content for any language, edit the JSON file for that language.
Never touch this file for content changes.
"""
import os, json

_CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'content')

def _load():
    langs = {}
    if not os.path.isdir(_CONTENT_DIR):
        return langs
    for fname in sorted(os.listdir(_CONTENT_DIR)):
        if not fname.endswith('.json'):
            continue
        code = fname[:-5]
        try:
            with open(os.path.join(_CONTENT_DIR, fname), encoding='utf-8') as f:
                langs[code] = json.load(f)
        except Exception as e:
            print(f'[content] Failed to load {fname}: {e}')
    return langs

LANGUAGES = _load()
STOPS = ['alphabet', 'words', 'lines', 'customs', 'story']


def list_languages():
    return [{'code': code, 'name': data['name']} for code, data in LANGUAGES.items()]


def get_language(code):
    return LANGUAGES.get(code)


def pick_item(language_code, stop):
    import random
    lang = LANGUAGES.get(language_code)
    if not lang:
        return None
    key = 'stories' if stop == 'story' else stop
    pool = lang.get(key, [])
    if not pool:
        return None
    return random.choice(pool)


# ── story cycling ─────────────────────────────────────────────────────────────
_story_idx = {}   # {language_code: int}

def next_story(language_code):
    """Returns stories in order, cycling — so the child sees all of them."""
    lang = LANGUAGES.get(language_code)
    if not lang:
        return None
    pool = lang.get('stories', [])
    if not pool:
        return None
    idx = _story_idx.get(language_code, 0) % len(pool)
    _story_idx[language_code] = idx + 1
    return pool[idx]
