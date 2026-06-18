"""
routes/parent.py — the parent-facing side: every record, in full, plus
the button to clear it all.
"""
from datetime import datetime, timezone
from flask import Blueprint, render_template, jsonify, session
from models.db import get_cur
from routes.auth import login_required
from routes.child import INCLUDED_MINUTES_PER_MONTH, OVERAGE_RATE_PER_HOUR_GBP
from services.content import get_language

parent_bp = Blueprint("parent", __name__)


@parent_bp.route("/dashboard")
@login_required(role="parent")
def dashboard():
    with get_cur() as cur:
        cur.execute("""
            SELECT id, display_name, language, country, usage_minutes_this_month, usage_month
            FROM users WHERE parent_id = %s ORDER BY created_at
        """, (session["user_id"],))
        children = cur.fetchall()

    now_month = datetime.now(timezone.utc).strftime("%Y-%m")
    for c in children:
        minutes = c["usage_minutes_this_month"] or 0
        if c["usage_month"] != now_month:
            minutes = 0
        c["minutes_used"] = minutes
        c["included_minutes"] = INCLUDED_MINUTES_PER_MONTH
        overage_minutes = max(0, minutes - INCLUDED_MINUTES_PER_MONTH)
        c["overage_minutes"] = overage_minutes
        c["overage_cost_gbp"] = round((overage_minutes / 60) * OVERAGE_RATE_PER_HOUR_GBP, 2)
        c["language_name"] = (get_language(c["language"]) or {}).get("name", c["language"])

    records = []
    if children:
        child_ids = tuple(str(c["id"]) for c in children)
        with get_cur() as cur:
            cur.execute("""
                SELECT child_id, language, stop, item_shown, transcript, score, feedback, created_at
                FROM activity_log WHERE child_id IN %s
                ORDER BY created_at DESC LIMIT 200
            """, (child_ids,))
            records = cur.fetchall()

    return render_template("parent_dashboard.html", children=children, records=records)


@parent_bp.route("/api/clear-data/<child_id>", methods=["POST"])
@login_required(role="parent")
def clear_data(child_id):
    """Deletes every activity record for this child. The child's login
    itself is untouched — only the history is wiped, completely."""
    with get_cur() as cur:
        # Ownership check — only ever clear a child that belongs to this parent.
        cur.execute("SELECT 1 FROM users WHERE id=%s AND parent_id=%s", (child_id, session["user_id"]))
        if not cur.fetchone():
            return jsonify({"error": "not found"}), 404
        cur.execute("DELETE FROM activity_log WHERE child_id=%s", (child_id,))
        deleted = cur.rowcount

    return jsonify({"cleared": True, "rows_deleted": deleted})
