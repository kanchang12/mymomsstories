"""
routes/parent.py — parent dashboard, add/manage children, Stripe billing,
account-level controls (cancel subscription, delete account — GDPR).
"""
import secrets
import bcrypt
from datetime import datetime, timezone
from flask import Blueprint, render_template, jsonify, session, request, redirect, url_for
from models.db import get_cur
from routes.auth import login_required
from services.content import get_language, list_languages
from services.payments import (
    INCLUDED_MINUTES_PER_MONTH, OVERAGE_RATE_PER_HOUR_GBP,
    get_subscription, create_checkout_session, activate_checkout_session,
    cancel_stripe_subscription,
)

parent_bp = Blueprint("parent", __name__)

_PW_WORDS = ["Mango","Tiger","Comet","Rocket","Panda","Falcon","Maple","Sunny",
             "River","Echo","Cobra","Nimbus","Pixel","Robin","Atlas","Cloud"]


def _gen_password():
    return f"{secrets.choice(_PW_WORDS)}{secrets.randbelow(90) + 10}"


@parent_bp.route("/dashboard")
@login_required(role="parent")
def dashboard():
    with get_cur() as cur:
        cur.execute("""
            SELECT id, username, display_name, language, country,
                   usage_minutes_this_month, usage_month
            FROM users WHERE parent_id = %s ORDER BY created_at
        """, (session["user_id"],))
        children = cur.fetchall()

    now_month = datetime.now(timezone.utc).strftime("%Y-%m")
    for c in children:
        minutes = c["usage_minutes_this_month"] or 0
        if c["usage_month"] != now_month:
            minutes = 0
        c["minutes_used"]    = minutes
        c["included_minutes"] = INCLUDED_MINUTES_PER_MONTH
        overage_minutes      = max(0, minutes - INCLUDED_MINUTES_PER_MONTH)
        c["overage_minutes"]  = overage_minutes
        c["overage_cost_gbp"] = round((overage_minutes / 60) * OVERAGE_RATE_PER_HOUR_GBP, 2)
        c["language_name"]    = (get_language(c["language"]) or {}).get("name", c["language"])

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

    subscription = get_subscription(session["user_id"])
    languages    = list_languages()

    return render_template("parent_dashboard.html",
                           children=children, records=records,
                           subscription=subscription, languages=languages,
                           suggested_password=_gen_password())


# ── Add child ──────────────────────────────────────────────────────────────────

@parent_bp.route("/add-child", methods=["POST"])
@login_required(role="parent")
def add_child():
    parent_id    = session["user_id"]
    nickname     = (request.form.get("nickname") or "").strip()
    child_username = (request.form.get("child_username") or "").strip().lower()
    password     = (request.form.get("password") or "").strip()
    language     = (request.form.get("language") or session.get("language", "")).strip()

    if not nickname:
        return jsonify({"error": "Give your child a nickname"}), 400
    if not child_username or len(child_username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if not child_username.replace("_","").replace("-","").isalnum():
        return jsonify({"error": "Username can only contain letters, numbers, - and _"}), 400
    if not password or len(password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

    with get_cur() as cur:
        cur.execute("SELECT country FROM users WHERE id=%s", (parent_id,))
        row = cur.fetchone()
    country = (row["country"] if row else "") or ""

    try:
        with get_cur() as cur:
            cur.execute("""
                INSERT INTO users
                  (username, password_hash, role, display_name, country, language, parent_id)
                VALUES (%s, %s, 'child', %s, %s, %s, %s)
                RETURNING id
            """, (child_username, pw_hash, nickname, country, language, parent_id))
            child_id = str(cur.fetchone()["id"])
    except Exception as e:
        if "unique" in str(e).lower():
            return jsonify({"error": "That username is already taken — try another"}), 400
        return jsonify({"error": "Something went wrong"}), 500

    return jsonify({
        "ok": True,
        "child_id":       child_id,
        "child_username": child_username,
        "child_password": password,
        "nickname":       nickname,
    })


# ── Edit child login (username / password) ──────────────────────────────────────

@parent_bp.route("/edit-child/<child_id>", methods=["POST"])
@login_required(role="parent")
def edit_child(child_id):
    """Change a child's username and/or password. Either field can be left
    blank to keep it unchanged — but if a new password is given it must
    meet the same minimum as add-child."""
    with get_cur() as cur:
        cur.execute("SELECT id, username, display_name FROM users WHERE id=%s AND parent_id=%s",
                    (child_id, session["user_id"]))
        child = cur.fetchone()
    if not child:
        return jsonify({"error": "not found"}), 404

    new_username = (request.form.get("child_username") or "").strip().lower()
    new_password = (request.form.get("password") or "").strip()

    if not new_username or len(new_username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if not new_username.replace("_", "").replace("-", "").isalnum():
        return jsonify({"error": "Username can only contain letters, numbers, - and _"}), 400
    if not new_password or len(new_password) < 4:
        return jsonify({"error": "Password must be at least 4 characters"}), 400

    pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt(12)).decode()

    try:
        with get_cur() as cur:
            cur.execute("UPDATE users SET username=%s, password_hash=%s WHERE id=%s",
                        (new_username, pw_hash, child_id))
    except Exception as e:
        if "unique" in str(e).lower():
            return jsonify({"error": "That username is already taken — try another"}), 400
        return jsonify({"error": "Something went wrong"}), 500

    return jsonify({
        "ok": True,
        "child_id":       child_id,
        "child_username": new_username,
        "child_password": new_password,
        "nickname":       child["display_name"],
    })


# ── Clear child data ───────────────────────────────────────────────────────────

@parent_bp.route("/api/clear-data/<child_id>", methods=["POST"])
@login_required(role="parent")
def clear_data(child_id):
    with get_cur() as cur:
        cur.execute("SELECT 1 FROM users WHERE id=%s AND parent_id=%s",
                    (child_id, session["user_id"]))
        if not cur.fetchone():
            return jsonify({"error": "not found"}), 404
        cur.execute("DELETE FROM activity_log WHERE child_id=%s", (child_id,))
        deleted = cur.rowcount
    return jsonify({"cleared": True, "rows_deleted": deleted})


# ── Stripe subscription ────────────────────────────────────────────────────────

@parent_bp.route("/stripe/subscribe", methods=["POST"])
@login_required(role="parent")
def stripe_subscribe():
    parent_id = session["user_id"]
    base_url  = request.host_url.rstrip("/")
    result    = create_checkout_session(parent_id, base_url)
    if result.get("checkout_url"):
        return jsonify({"ok": True, "approve_url": result["checkout_url"]})
    return jsonify({"error": result.get("error", "Stripe error")}), 500


@parent_bp.route("/stripe/success")
@login_required(role="parent")
def stripe_success():
    session_id = request.args.get("session_id")
    parent_id  = session["user_id"]
    if not session_id:
        return redirect(url_for("parent.dashboard") + "?payment=failed")
    result = activate_checkout_session(parent_id, session_id)
    if result.get("ok"):
        return redirect(url_for("parent.dashboard") + "?payment=success")
    return redirect(url_for("parent.dashboard") + "?payment=failed")


@parent_bp.route("/stripe/cancel")
@login_required(role="parent")
def stripe_cancel():
    """Landed here if the parent backs out of Stripe Checkout itself —
    not the same as cancelling an active subscription, see below."""
    return redirect(url_for("parent.dashboard") + "?payment=cancelled")


@parent_bp.route("/subscription/cancel", methods=["POST"])
@login_required(role="parent")
def subscription_cancel():
    """Cancels an active paid subscription. Trial isn't a Stripe
    subscription so there's nothing to cancel there — it just expires."""
    sub = get_subscription(session["user_id"])
    stripe_sub_id = sub.get("stripe_subscription_id")

    if not stripe_sub_id:
        return jsonify({"error": "No active subscription to cancel"}), 400

    result = cancel_stripe_subscription(stripe_sub_id)
    if not result.get("ok"):
        return jsonify({"error": result.get("error", "Could not cancel — try again or contact support")}), 500

    with get_cur() as cur:
        cur.execute("UPDATE subscriptions SET status='cancelled', updated_at=NOW() WHERE user_id=%s",
                    (session["user_id"],))

    return jsonify({"ok": True})


# ── Account deletion (GDPR right to erasure) ────────────────────────────────────

@parent_bp.route("/delete-account", methods=["POST"])
@login_required(role="parent")
def delete_account():
    """Permanently deletes the parent account and everything tied to it —
    children, activity logs, subscription record, payment events. Cascade
    deletes are set up at the DB level (ON DELETE CASCADE on parent_id /
    user_id foreign keys), so deleting the parent row does the rest.
    Cancels any live Stripe subscription first so they're not still being
    billed after the account is gone."""
    confirm_email = (request.form.get("confirm_email") or "").strip().lower()
    if confirm_email != session.get("username", "").strip().lower():
        return jsonify({"error": "Email didn't match — type your account email exactly to confirm"}), 400

    sub = get_subscription(session["user_id"])
    stripe_sub_id = sub.get("stripe_subscription_id")
    if stripe_sub_id and sub.get("status") == "active":
        cancel_stripe_subscription(stripe_sub_id)  # best-effort, don't block deletion on this

    with get_cur() as cur:
        cur.execute("DELETE FROM users WHERE id=%s AND role='parent'", (session["user_id"],))

    session.clear()
    return jsonify({"ok": True})
