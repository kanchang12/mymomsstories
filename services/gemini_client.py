"""
services/gemini_client.py — one shared Gemini client, same pattern as
aitutor/services/language_reader.py (google-genai SDK, genai.Client).

Lazily constructed on first use, not at import time — genai.Client()
raises immediately if no API key is present, which would otherwise
crash the whole app on startup before GEMINI_API_KEY is ever configured
(this same risk exists in aitutor/services/language_reader.py, worth
checking there too).
"""
import os
from google import genai

MODEL = "gemini-2.5-flash"   # cheap + fast; this is short text-in/text-out scoring, not audio

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set — scoring will fail until it is.")
        _client = genai.Client(api_key=api_key)
    return _client
