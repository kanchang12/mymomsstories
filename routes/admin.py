"""
routes/admin.py — Admin panel. Login with role='admin' account.
Shows all parents, subscriptions, children, recent activity.
Create an admin account directly in the DB:
  INSERT INTO users (username, password_hash, role, display_name)
  VALUES ('admin@mms.com', '<bcrypt_hash>', 'admin', 'Admin');
"""
import bcrypt
from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from routes.auth import login_required
from models.db import get_cur
from services.payments import get_all_subscriptions, MONTHLY_PRICE_GBP, TRIAL_DAYS

admin_bp = Blueprint("admin", __name__)


def _stats():
    with get_cur() as cur:
        cur.execute("SELECT COUNT(*) as c FROM users WHERE role='parent'")
        parents = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM users WHERE role='child'")
        children = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM subscriptions WHERE plan='mms_monthly' AND status='active'")
        paid = cur.fetchone()["c"]
        cur.execute("SELECT COUNT(*) as c FROM subscriptions WHERE plan='trial'")
        trial = cur.fetchone()["c"]
        cur.execute("SELECT COALESCE(SUM(amount_pence),0) as t FROM payment_events WHERE status IN ('activated','captured') AND gateway='stripe'")
        revenue_pence = cur.fetchone()["t"]
        cur.execute("SELECT COUNT(*) as c FROM activity_log WHERE created_at > NOW() - INTERVAL '7 days'")
        attempts_7d = cur.fetchone()["c"]
    return dict(
        parents=parents, children=children,
        paid=paid, trial=trial,
        revenue_gbp=int(revenue_pence) // 100,
        attempts_7d=attempts_7d,
    )


@admin_bp.route("/")
@login_required(role="admin")
def dashboard():
    stats = _stats()
    subs  = get_all_subscriptions()

    with get_cur() as cur:
        cur.execute("""
            SELECT u.id, u.display_name, u.username, u.last_login, u.created_at,
                   p.display_name AS parent_name,
                   (SELECT COUNT(*) FROM activity_log al WHERE al.child_id=u.id) AS attempt_count,
                   (SELECT MAX(created_at) FROM activity_log al WHERE al.child_id=u.id) AS last_activity
            FROM users u
            JOIN users p ON p.id=u.parent_id
            WHERE u.role='child'
            ORDER BY u.created_at DESC
        """)
        children = cur.fetchall()

    with get_cur() as cur:
        cur.execute("""
            SELECT al.created_at, al.language, al.stop, al.item_shown,
                   al.transcript, al.score, u.display_name as child_name,
                   p.display_name as parent_name
            FROM activity_log al
            JOIN users u ON u.id=al.child_id
            JOIN users p ON p.id=u.parent_id
            ORDER BY al.created_at DESC LIMIT 100
        """)
        recent = cur.fetchall()

    return render_template("admin.html",
                           stats=stats, subs=subs, children=children, recent=recent)


@admin_bp.route("/create-admin", methods=["POST"])
@login_required(role="admin")
def create_admin():
    """POST email + password to create another admin account."""
    email    = (request.form.get("email") or "").strip().lower()
    password = (request.form.get("password") or "").strip()
    if not email or len(password) < 8:
        return jsonify({"error": "email and password (min 8 chars) required"}), 400
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    try:
        with get_cur() as cur:
            cur.execute("""
                INSERT INTO users (username, password_hash, role, display_name)
                VALUES (%s, %s, 'admin', %s)
            """, (email, pw_hash, email.split("@")[0]))
    except Exception as e:
        if "unique" in str(e).lower():
            return jsonify({"error": "email already exists"}), 400
        return jsonify({"error": str(e)}), 500
    return jsonify({"ok": True})


@admin_bp.route("/reset-password/<user_id>", methods=["POST"])
@login_required(role="admin")
def reset_password(user_id):
    password = (request.form.get("password") or "").strip()
    if len(password) < 6:
        return jsonify({"error": "min 6 chars"}), 400
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()
    with get_cur() as cur:
        cur.execute("UPDATE users SET password_hash=%s WHERE id=%s", (pw_hash, user_id))
    return jsonify({"ok": True})
