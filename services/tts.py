"""
services/tts.py — text-to-speech via Gemini, one regional voice per language.

Cost: ~$10 per 1M audio output tokens, roughly 25 tokens/sec of speech.
A single word or line (2-3 sec) costs a fraction of a cent.

Each language gets its own locale (so pronunciation/accent is correct) and
its own prebuilt voice (for variety and a more natural, less "one robot for
everything" feel). Repeated requests for the same text+language are served
from an in-process cache so the same word/custom/story line isn't paid for
twice within the life of the running server.
"""
import os
import io
import wave
import hashlib
from google import genai
from google.genai import types

TTS_MODEL = "gemini-2.5-flash-preview-tts"

# language_code -> (BCP-47 locale for correct accent/pronunciation, prebuilt voice name)
# Voices are chosen for variety and a warm, natural narrator tone — not the
# same single voice reused for every language.
VOICE_MAP = {
    "bn": ("bn-IN", "Kore"),
    "hi": ("hi-IN", "Puck"),
    "mr": ("mr-IN", "Charon"),
    "ta": ("ta-IN", "Aoede"),
    "te": ("te-IN", "Leda"),
    "kn": ("kn-IN", "Umbriel"),
    "ml": ("ml-IN", "Despina"),
    "ar": ("ar-XA", "Algieba"),
    "es": ("es-US", "Autonoe"),
    "ja": ("ja-JP", "Callirrhoe"),
    "ru": ("ru-RU", "Schedar"),
    "uk": ("uk-UA", "Gacrux"),
    "ro": ("ro-RO", "Vindemiatrix"),
}

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set — TTS will fail until it is.")
        _client = genai.Client(api_key=api_key)
    return _client


# In-process cache only — resets on deploy/restart. Fine for cutting repeat
# costs on the same running server; not meant as permanent storage.
_cache = {}
_CACHE_MAX = 500


def _pcm_to_wav(pcm_data: bytes, channels=1, rate=24000, sample_width=2) -> bytes:
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)
    return buf.getvalue()


def synthesize(text: str, language_code: str) -> bytes:
    """Returns WAV audio bytes for the given text, spoken in that language's
    regional voice. Raises on failure — caller should catch and return a
    clean error to the client rather than a broken audio file."""
    text = (text or "").strip()
    if not text:
        raise ValueError("empty text")

    locale, voice_name = VOICE_MAP.get(language_code, ("en-US", "Kore"))

    cache_key = hashlib.sha256(f"{language_code}:{text}".encode("utf-8")).hexdigest()
    if cache_key in _cache:
        return _cache[cache_key]

    client = _get_client()
    response = client.models.generate_content(
        model=TTS_MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                language_code=locale,
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice_name)
                ),
            ),
        ),
    )
    pcm = response.candidates[0].content.parts[0].inline_data.data
    wav_bytes = _pcm_to_wav(pcm)

    if len(_cache) < _CACHE_MAX:
        _cache[cache_key] = wav_bytes

    return wav_bytes
