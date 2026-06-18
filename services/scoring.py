"""
services/scoring.py — scores a child's reading attempt.

Same approach as aitutor/services/language_reader.py: the BROWSER does
speech-to-text (Web Speech API / SpeechRecognition, which already covers
bn-IN, hi-IN, mr-IN, ta-IN, te-IN, kn-IN, ml-IN, ar-SA, es-ES and ja-JP
locales in Chrome). We only ever send Gemini a short text-in/text-out
scoring prompt — never raw audio. This is the cheap path we settled on:
no ElevenLabs, no audio tokens, just a few hundred text tokens per turn.
"""
import json
import re
from services.gemini_client import get_client, MODEL


def score_attempt(language_name, stop, item_shown, transcript, child_name):
    """Compare what was shown vs. what the child said (already
    transcribed by the browser). Returns dict: score, correct, feedback."""
    if not transcript or not transcript.strip():
        return {"score": 0, "correct": False,
                "feedback": "I didn't catch that — tap the microphone and try again."}

    prompt = f"""You are a warm, patient {language_name} reading helper for a child learning to read their heritage language.

The child ({child_name}) was shown this {stop} to read aloud:
SHOWN: {item_shown}

This is the speech-to-text transcript of what they said:
HEARD: {transcript}

Score the attempt. Be encouraging — this child may not hear {language_name} spoken often, so reward genuine effort, not just a perfect match.
Return JSON only, no other text:
{{"score": 0-100, "correct": true/false, "feedback": "one short, warm sentence in English naming what they got right or what to try again"}}
correct=true if score>=60."""

    try:
        client = get_client()
        r = client.models.generate_content(model=MODEL, contents=prompt)
        raw = re.sub(r"```json|```", "", r.text).strip()
        result = json.loads(raw)
        result["score"] = max(0, min(100, int(result.get("score", 50))))
        return result
    except Exception:
        return {"score": 50, "correct": True,
                "feedback": "Good effort! Keep practising."}
