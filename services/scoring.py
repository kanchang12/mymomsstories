"""
services/scoring.py — scores a child's reading attempt via Gemini.
Prompt is kept tiny to minimise latency.
"""
import json, re
from services.gemini_client import get_client, MODEL


def score_attempt(language_name, stop, item_shown, transcript, child_name):
    if not transcript or not transcript.strip():
        return {"score": 0, "correct": False,
                "feedback": "Didn't catch that — tap the mic and try again."}

    prompt = (
        f"Heritage language reading check. Language: {language_name}. "
        f"Shown: [{item_shown}] Heard: [{transcript}]. "
        f"Be warm and encouraging. "
        f'Reply JSON only: {{"score":0-100,"correct":true/false,"feedback":"one short sentence"}}'
    )

    try:
        client = get_client()
        r = client.models.generate_content(model=MODEL, contents=prompt)
        raw = re.sub(r"```json|```", "", r.text).strip()
        result = json.loads(raw)
        result["score"] = max(0, min(100, int(result.get("score", 50))))
        result.setdefault("correct", result["score"] >= 60)
        return result
    except Exception:
        return {"score": 50, "correct": True, "feedback": "Good effort — keep going!"}
