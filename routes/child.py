"""
routes/child.py — the child-facing side: today's mixed-up set of stops,
the reading/scoring endpoint, and the usage heartbeat.
"""
import random
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, jsonify, session
from models.db import get_cur
from routes.auth import login_required
from services.content import get_language, pick_item, STOPS
from services.scoring import score_attempt

child_bp = Blueprint("child", __name__)

INCLUDED_MINUTES_PER_MONTH = 15 * 60   # 15 hours
OVERAGE_RATE_PER_HOUR_GBP  = 1.50

STOP_LABELS = {
    "alphabet": "Alphabet & sounds",
    "words":    "Small words",
    "lines":    "Small lines",
    "customs":  "A custom from home",
    "story":    "A famous story",
}


@child_bp.route("/dashboard")
@login_required(role="child")
def dashboard():
    lang_code = session.get("language")
    lang = get_language(lang_code)
    stops_today = STOPS.copy()
    random.shuffle(stops_today)  # "some days alphabets, some days customs" — mixed every visit
    return render_template(
        "child_dashboard.html",
        lang=lang, lang_code=lang_code,
        stops_today=stops_today, stop_labels=STOP_LABELS,
        child_name=session.get("display_name"),
    )


@child_bp.route("/api/item")
@login_required(role="child")
def api_item():
    """Fetch one content item for a given stop, for the child's language."""
    stop = request.args.get("stop")
    if stop not in STOPS:
        return jsonify({"error": "unknown stop"}), 400
    item = pick_item(session.get("language"), stop)
    if not item:
        return jsonify({"error": "no content for this language yet"}), 404
    return jsonify({"stop": stop, "item": item})


@child_bp.route("/api/attempt", methods=["POST"])
@login_required(role="child")
def api_attempt():
    """Child read something aloud; browser already turned it into a
    transcript (Web Speech API) and posts that here for scoring."""
    body       = request.get_json() or {}
    stop       = body.get("stop")
    item_key   = body.get("item_key", "")
    item_shown = body.get("item_shown", "")
    transcript = body.get("transcript", "")

    if stop not in STOPS:
        return jsonify({"error": "unknown stop"}), 400

    lang = get_language(session.get("language"))
    lang_name = lang["name"] if lang else session.get("language")

    if stop in ("customs", "story"):
        # No spoken check for these — just log that it was read/heard.
        result = {"score": None, "correct": True, "feedback": "Nice — that's one more piece of home you know."}
    else:
        result = score_attempt(lang_name, stop, item_shown, transcript, session.get("display_name"))

    with get_cur() as cur:
        cur.execute("""
            INSERT INTO activity_log (child_id, language, stop, item_key, item_shown, transcript, score, feedback)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (session["user_id"], session.get("language"), stop, item_key, item_shown,
              transcript or None, result.get("score"), result.get("feedback")))

    return jsonify(result)


@child_bp.route("/api/heartbeat", methods=["POST"])
@login_required(role="child")
def heartbeat():
    """Pinged once a minute by the child dashboard while the tab is open
    and visible. Tracks minutes used this month and the running overage
    cost past the 15 included hours, at £1.50/hour. This only tracks the
    number — it doesn't charge anything; wire that total into your
    billing provider of choice when you're ready."""
    now_month = datetime.now(timezone.utc).strftime("%Y-%m")

    with get_cur() as cur:
        cur.execute("SELECT usage_minutes_this_month, usage_month FROM users WHERE id=%s", (session["user_id"],))
        row = cur.fetchone()
        minutes = row["usage_minutes_this_month"] or 0
        if row["usage_month"] != now_month:
            minutes = 0  # new month, fair-use counter resets

        minutes += 1
        cur.execute(
            "UPDATE users SET usage_minutes_this_month=%s, usage_month=%s WHERE id=%s",
            (minutes, now_month, session["user_id"]),
        )

    overage_minutes = max(0, minutes - INCLUDED_MINUTES_PER_MONTH)
    overage_cost = round((overage_minutes / 60) * OVERAGE_RATE_PER_HOUR_GBP, 2)

    return jsonify({
        "minutes_used_this_month": minutes,
        "included_minutes": INCLUDED_MINUTES_PER_MONTH,
        "overage_minutes": overage_minutes,
        "overage_cost_gbp": overage_cost,
    })
