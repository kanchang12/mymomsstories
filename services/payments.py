"""
services/payments.py — Billing: 7-day free trial, then £15/month via Stripe.

Flow:
  1. Parent registers → trial row auto-created (trial_started_at = NOW())
  2. After 7 days → is_access_allowed() returns False, dashboard shows paywall
  3. Parent clicks Subscribe → create_checkout_session() → Stripe Checkout
  4. Stripe redirects to /parent/stripe/success → activate_checkout_session()
  5. Webhooks at /webhooks/stripe keep status/renewal in sync

Overage (£1.50/hr past 15 included hours/month) is tracked and shown on the
parent dashboard but NOT auto-charged.
"""
import os
from datetime import datetime, timedelta, timezone
import stripe
from models.db import get_cur

STRIPE_SECRET_KEY     = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

stripe.api_key = STRIPE_SECRET_KEY

# ── Pricing ─────────────────────────────────────────────────────────────────
MONTHLY_PRICE_GBP          = 15
TRIAL_DAYS                 = 7
INCLUDED_MINUTES_PER_MONTH = 15 * 60   # 15 hours per child
OVERAGE_RATE_PER_HOUR_GBP  = 1.50
BILLING_CURRENCY           = "gbp"

_stripe_price_id_cache = None


# ── Subscription helpers ─────────────────────────────────────────────────────

def _ensure_subscription(user_id: str):
    """Auto-create a trial row on first access."""
    with get_cur() as cur:
        cur.execute("SELECT user_id FROM subscriptions WHERE user_id=%s", (user_id,))
        if cur.fetchone():
            return
        cur.execute("""
            INSERT INTO subscriptions (user_id, plan, status, trial_started_at)
            VALUES (%s, 'trial', 'active', NOW())
            ON CONFLICT (user_id) DO NOTHING
        """, (user_id,))


def get_subscription(user_id: str) -> dict:
    _ensure_subscription(user_id)
    with get_cur() as cur:
        cur.execute("SELECT * FROM subscriptions WHERE user_id=%s", (user_id,))
        row = cur.fetchone()

    if row is None:
        return {
            "plan": None, "status": None, "is_active": False,
            "monthly_price": MONTHLY_PRICE_GBP,
            "trial_days_left": None, "trial_exhausted": True,
            "current_period_end": None, "stripe_subscription_id": None,
        }

    plan   = row["plan"]
    status = row["status"]

    trial_days_left  = None
    trial_exhausted  = False
    if plan == "trial":
        started = row.get("trial_started_at")
        if started:
            if started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            elapsed = datetime.now(timezone.utc) - started
            trial_days_left = max(0, TRIAL_DAYS - elapsed.days)
            trial_exhausted = elapsed.days >= TRIAL_DAYS
        else:
            trial_days_left = TRIAL_DAYS

    is_active = (
        (plan == "trial" and not trial_exhausted) or
        (plan == "mms_monthly" and status == "active")
    )

    return {
        "plan":                     plan,
        "status":                   status,
        "is_active":                is_active,
        "monthly_price":            MONTHLY_PRICE_GBP,
        "trial_days_left":          trial_days_left,
        "trial_exhausted":          trial_exhausted,
        "current_period_end":       row.get("current_period_end"),
        "stripe_subscription_id":   row.get("stripe_subscription_id"),
    }


def is_access_allowed(user_id: str) -> bool:
    return get_subscription(user_id)["is_active"]


# ── Stripe price auto-provisioning ───────────────────────────────────────────

def _get_or_create_stripe_price() -> str:
    """Return the £15/month price_id — creates product+price once, caches in app_config."""
    global _stripe_price_id_cache
    if _stripe_price_id_cache:
        return _stripe_price_id_cache
    try:
        with get_cur() as cur:
            cur.execute("SELECT value FROM app_config WHERE key='stripe_price_id'")
            row = cur.fetchone()
            if row:
                _stripe_price_id_cache = row["value"]
                return _stripe_price_id_cache
    except Exception:
        pass

    product = stripe.Product.create(
        name="My Mom's Stories",
        description="Heritage-language reading — monthly access",
    )
    price = stripe.Price.create(
        product=product.id,
        unit_amount=MONTHLY_PRICE_GBP * 100,
        currency=BILLING_CURRENCY,
        recurring={"interval": "month"},
        nickname="My Mom's Stories Monthly",
    )

    try:
        with get_cur() as cur:
            cur.execute("INSERT INTO app_config (key,value) VALUES ('stripe_price_id',%s) "
                        "ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value", (price.id,))
    except Exception:
        pass
    _stripe_price_id_cache = price.id
    return price.id


def create_checkout_session(parent_id: str, return_base: str) -> dict:
    try:
        price_id = _get_or_create_stripe_price()
    except Exception as e:
        return {"error": f"Could not set up billing plan: {e}"}

    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            client_reference_id=parent_id,
            metadata={"parent_id": parent_id},
            success_url=f"{return_base}/parent/stripe/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{return_base}/parent/stripe/cancel",
        )
    except Exception as e:
        return {"error": f"Could not start checkout: {e}"}

    return {"checkout_url": session.url, "session_id": session.id}


def activate_checkout_session(parent_id: str, session_id: str) -> dict:
    """Called from the success redirect — confirms payment and activates.
    Webhook also does this independently, so this is a fast-path, not the
    only source of truth."""
    try:
        session = stripe.checkout.Session.retrieve(session_id, expand=["subscription"])
    except Exception as e:
        return {"ok": False, "error": str(e)}

    if session.get("payment_status") != "paid" and session.get("status") != "complete":
        return {"ok": False, "error": f"Unexpected status: {session.get('status')}"}

    sub_obj = session.get("subscription")
    subscription_id = sub_obj.get("id") if isinstance(sub_obj, dict) else sub_obj
    customer_id      = session.get("customer")
    period_end       = datetime.now(timezone.utc) + timedelta(days=30)

    if isinstance(sub_obj, dict) and sub_obj.get("current_period_end"):
        period_end = datetime.fromtimestamp(sub_obj["current_period_end"], tz=timezone.utc)

    _activate_subscription(parent_id, subscription_id, customer_id, period_end)
    return {"ok": True, "plan": "mms_monthly"}


def _activate_subscription(parent_id: str, subscription_id: str, customer_id: str, period_end) -> None:
    with get_cur() as cur:
        cur.execute("""
            INSERT INTO subscriptions
              (user_id, plan, status, stripe_subscription_id, stripe_customer_id, current_period_end)
            VALUES (%s,'mms_monthly','active',%s,%s,%s)
            ON CONFLICT (user_id) DO UPDATE SET
                plan='mms_monthly', status='active',
                stripe_subscription_id=EXCLUDED.stripe_subscription_id,
                stripe_customer_id=EXCLUDED.stripe_customer_id,
                current_period_end=EXCLUDED.current_period_end,
                updated_at=NOW()
        """, (parent_id, subscription_id, customer_id, period_end))
        cur.execute("""
            INSERT INTO payment_events
              (user_id, event_type, amount_pence, status, gateway, stripe_subscription_id)
            VALUES (%s,'subscription_activated',0,'activated','stripe',%s)
        """, (parent_id, subscription_id))


# ── Webhook handling ─────────────────────────────────────────────────────────

def verify_stripe_webhook_signature(payload: bytes, sig_header: str):
    """Returns the parsed Stripe event dict, or None if verification fails."""
    if not STRIPE_WEBHOOK_SECRET:
        import json as _json
        return _json.loads(payload)  # dev mode — skip verification
    try:
        return stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)
    except Exception as e:
        print(f"[stripe] webhook signature verification failed: {e}")
        return None


def handle_stripe_webhook(event_type: str, data_object: dict) -> dict:
    if event_type == "checkout.session.completed":
        parent_id = data_object.get("client_reference_id") or (data_object.get("metadata") or {}).get("parent_id")
        subscription_id = data_object.get("subscription")
        customer_id      = data_object.get("customer")
        if parent_id and subscription_id:
            period_end = datetime.now(timezone.utc) + timedelta(days=30)
            try:
                sub = stripe.Subscription.retrieve(subscription_id)
                if sub.get("current_period_end"):
                    period_end = datetime.fromtimestamp(sub["current_period_end"], tz=timezone.utc)
            except Exception:
                pass
            _activate_subscription(parent_id, subscription_id, customer_id, period_end)
        return {"ok": True, "action": "activated"}

    elif event_type == "invoice.paid":
        subscription_id = data_object.get("subscription")
        amount_pence     = data_object.get("amount_paid", 0)
        period_end       = datetime.now(timezone.utc) + timedelta(days=30)
        lines = data_object.get("lines", {}).get("data", [])
        if lines and lines[0].get("period", {}).get("end"):
            period_end = datetime.fromtimestamp(lines[0]["period"]["end"], tz=timezone.utc)
        with get_cur() as cur:
            cur.execute("""
                UPDATE subscriptions SET status='active', current_period_end=%s, updated_at=NOW()
                WHERE stripe_subscription_id=%s
            """, (period_end, subscription_id))
            cur.execute("SELECT user_id FROM subscriptions WHERE stripe_subscription_id=%s",
                        (subscription_id,))
            row = cur.fetchone()
            if row:
                cur.execute("""
                    INSERT INTO payment_events
                      (user_id, event_type, amount_pence, status, gateway, stripe_subscription_id)
                    VALUES (%s,'payment_captured',%s,'captured','stripe',%s)
                """, (row["user_id"], amount_pence, subscription_id))
        return {"ok": True, "action": "renewed"}

    elif event_type == "invoice.payment_failed":
        subscription_id = data_object.get("subscription")
        with get_cur() as cur:
            cur.execute("UPDATE subscriptions SET status='payment_failed', updated_at=NOW() "
                        "WHERE stripe_subscription_id=%s", (subscription_id,))
        return {"ok": True, "action": "suspended"}

    elif event_type in ("customer.subscription.deleted", "customer.subscription.updated"):
        subscription_id = data_object.get("id")
        status = data_object.get("status")
        if event_type == "customer.subscription.deleted" or status in ("canceled", "incomplete_expired"):
            with get_cur() as cur:
                cur.execute("UPDATE subscriptions SET status='cancelled', updated_at=NOW() "
                            "WHERE stripe_subscription_id=%s", (subscription_id,))
            return {"ok": True, "action": "cancelled"}

    return {"ok": True, "action": "ignored"}


# ── Cancellation ──────────────────────────────────────────────────────────────

def cancel_stripe_subscription(subscription_id: str) -> dict:
    """Cancels an active Stripe subscription immediately. Local DB status is
    updated by the caller — Stripe also sends a customer.subscription.deleted
    webhook which handle_stripe_webhook() will pick up as a second
    confirmation."""
    if not subscription_id:
        return {"ok": False, "error": "No subscription on file"}
    try:
        stripe.Subscription.delete(subscription_id)
        return {"ok": True}
    except Exception as e:
        print(f"[stripe] cancel failed: {e}")
        return {"ok": False, "error": str(e)}


# ── Admin helpers ─────────────────────────────────────────────────────────────

def get_all_subscriptions():
    with get_cur() as cur:
        cur.execute("""
            SELECT u.username, u.display_name, u.created_at, u.id as user_id,
                   s.plan, s.status, s.current_period_end, s.trial_started_at,
                   s.stripe_subscription_id,
                   (SELECT COUNT(*) FROM users c WHERE c.parent_id=u.id AND c.role='child') AS child_count
            FROM users u
            LEFT JOIN subscriptions s ON s.user_id=u.id
            WHERE u.role='parent'
            ORDER BY u.created_at DESC
        """)
        rows = cur.fetchall()
    for r in rows:
        plan = r.get("plan")
        r["monthly_total"] = 0 if plan in (None, "trial") else MONTHLY_PRICE_GBP
    return rows
