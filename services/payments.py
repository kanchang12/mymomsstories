"""
services/payments.py — Billing: 7-day free trial, then £15/month via PayPal.

Flow:
  1. Parent registers → trial row auto-created (trial_started_at = NOW())
  2. After 7 days → is_access_allowed() returns False, dashboard shows paywall
  3. Parent clicks Subscribe → create_paypal_subscription() → PayPal approval
  4. PayPal redirects to /parent/paypal/success → activate_paypal_subscription()
  5. Webhooks at /webhooks/paypal keep status/renewal in sync

Same PayPal plumbing as aitutor/services/payments.py (OAuth client-credentials,
auto-provision product+plan cached in app_config, webhook handling).

Overage (£1.50/hr past 15 included hours/month) is tracked and shown on the
parent dashboard but NOT auto-charged — PayPal subscriptions API only bills a
fixed amount. Variable top-up needs PayPal Reference Transactions or Stripe.
"""
import os
from datetime import datetime, timedelta, timezone
import requests
from models.db import get_cur

PAYPAL_CLIENT_ID  = os.environ.get("PAYPAL_CLIENT_ID", "")
PAYPAL_SECRET     = os.environ.get("PAYPAL_SECRET", "")
PAYPAL_MODE       = os.environ.get("PAYPAL_MODE", "sandbox")
PAYPAL_WEBHOOK_ID = os.environ.get("PAYPAL_WEBHOOK_ID", "")

PAYPAL_BASE = "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

# ── Pricing ─────────────────────────────────────────────────────────────────
MONTHLY_PRICE_GBP          = 15
TRIAL_DAYS                 = 7
INCLUDED_MINUTES_PER_MONTH = 15 * 60   # 15 hours per child
OVERAGE_RATE_PER_HOUR_GBP  = 1.50
BILLING_CURRENCY           = "GBP"

_paypal_plan_id_cache = None


# ── Subscription helpers ─────────────────────────────────────────────────────

def _ensure_subscription(user_id: str):
    """Auto-create a trial row on first access — matches aitutor pattern."""
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
        "plan":                    plan,
        "status":                  status,
        "is_active":               is_active,
        "monthly_price":           MONTHLY_PRICE_GBP,
        "trial_days_left":         trial_days_left,
        "trial_exhausted":         trial_exhausted,
        "current_period_end":      row.get("current_period_end"),
        "paypal_subscription_id":  row.get("paypal_subscription_id"),
    }


def is_access_allowed(user_id: str) -> bool:
    return get_subscription(user_id)["is_active"]


# ── PayPal OAuth + plan auto-provisioning ────────────────────────────────────

def _paypal_token() -> str:
    r = requests.post(
        f"{PAYPAL_BASE}/v1/oauth2/token",
        data={"grant_type": "client_credentials"},
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        timeout=10
    )
    data = r.json()
    token = data.get("access_token", "")
    if not token:
        print(f"[paypal] token failed (mode={PAYPAL_MODE}): {data}")
    return token


def _get_or_create_paypal_plan() -> str:
    """Return the £15/month plan_id — creates product+plan once, caches in app_config."""
    global _paypal_plan_id_cache
    if _paypal_plan_id_cache:
        return _paypal_plan_id_cache
    try:
        with get_cur() as cur:
            cur.execute("SELECT value FROM app_config WHERE key='paypal_plan_id'")
            row = cur.fetchone()
            if row:
                _paypal_plan_id_cache = row["value"]
                return _paypal_plan_id_cache
    except Exception:
        pass

    token = _paypal_token()
    prod = requests.post(
        f"{PAYPAL_BASE}/v1/catalogs/products",
        json={"name": "My Mom's Stories",
              "description": "Heritage-language reading — monthly access",
              "type": "SERVICE", "category": "EDUCATIONAL_AND_TEXTBOOKS"},
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "PayPal-Request-Id": "mms-prod-monthly-gbp-v2"},
        timeout=10
    ).json()
    product_id = prod.get("id")
    if not product_id:
        raise Exception(f"PayPal product creation failed: {prod}")

    plan = requests.post(
        f"{PAYPAL_BASE}/v1/billing/plans",
        json={
            "product_id": product_id,
            "name":        "My Mom's Stories Monthly",
            "description": f"GBP {MONTHLY_PRICE_GBP}/month, 15 hours included per child",
            "quantity_supported": False,
            "billing_cycles": [{
                "frequency":      {"interval_unit": "MONTH", "interval_count": 1},
                "tenure_type":    "REGULAR",
                "sequence":       1,
                "total_cycles":   0,
                "pricing_scheme": {"fixed_price": {"value": str(MONTHLY_PRICE_GBP),
                                                   "currency_code": BILLING_CURRENCY}},
            }],
            "payment_preferences": {
                "auto_bill_outstanding":     True,
                "setup_fee":                 {"value": "0", "currency_code": BILLING_CURRENCY},
                "setup_fee_failure_action":  "CONTINUE",
                "payment_failure_threshold": 2,
            },
        },
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                 "PayPal-Request-Id": "mms-plan-monthly-gbp-v2"},
        timeout=10
    ).json()
    plan_id = plan.get("id")
    if not plan_id:
        raise Exception(f"PayPal plan creation failed: {plan}")

    try:
        with get_cur() as cur:
            cur.execute("INSERT INTO app_config (key,value) VALUES ('paypal_plan_id',%s) "
                        "ON CONFLICT (key) DO UPDATE SET value=EXCLUDED.value", (plan_id,))
    except Exception:
        pass
    _paypal_plan_id_cache = plan_id
    return plan_id


def create_paypal_subscription(parent_id: str, return_base: str) -> dict:
    try:
        plan_id = _get_or_create_paypal_plan()
    except Exception as e:
        return {"error": f"Could not set up billing plan: {e}"}

    token   = _paypal_token()
    payload = {
        "plan_id":   plan_id,
        "custom_id": parent_id,
        "application_context": {
            "brand_name":          "My Mom's Stories",
            "locale":              "en-GB",
            "shipping_preference": "NO_SHIPPING",
            "user_action":         "SUBSCRIBE_NOW",
            "return_url":          f"{return_base}/parent/paypal/success",
            "cancel_url":          f"{return_base}/parent/paypal/cancel",
        },
    }
    r    = requests.post(f"{PAYPAL_BASE}/v1/billing/subscriptions", json=payload,
                         headers={"Authorization": f"Bearer {token}",
                                  "Content-Type": "application/json"}, timeout=10)
    data = r.json()
    approve_url = next((l["href"] for l in data.get("links", []) if l["rel"] == "approve"), None)
    if not approve_url:
        print(f"[paypal] subscription creation failed: {data}")
    return {
        "subscription_id": data.get("id"),
        "approve_url":     approve_url,
        "status":          data.get("status"),
        "error":           data.get("message") if not approve_url else None,
    }


def activate_paypal_subscription(parent_id: str, subscription_id: str) -> dict:
    token = _paypal_token()
    r     = requests.get(f"{PAYPAL_BASE}/v1/billing/subscriptions/{subscription_id}",
                         headers={"Authorization": f"Bearer {token}"}, timeout=10)
    data  = r.json()
    status = data.get("status", "")
    if status not in ("ACTIVE", "APPROVAL_PENDING"):
        return {"ok": False, "error": f"Unexpected status: {status}"}

    payer_id   = data.get("subscriber", {}).get("payer_id", "")
    period_end = datetime.now(timezone.utc) + timedelta(days=30)

    with get_cur() as cur:
        cur.execute("""
            INSERT INTO subscriptions
              (user_id, plan, status, paypal_subscription_id, paypal_payer_id, current_period_end)
            VALUES (%s,'mms_monthly','active',%s,%s,%s)
            ON CONFLICT (user_id) DO UPDATE SET
                plan='mms_monthly', status='active',
                paypal_subscription_id=EXCLUDED.paypal_subscription_id,
                paypal_payer_id=EXCLUDED.paypal_payer_id,
                current_period_end=EXCLUDED.current_period_end,
                updated_at=NOW()
        """, (parent_id, subscription_id, payer_id, period_end))
        cur.execute("""
            INSERT INTO payment_events
              (user_id, event_type, amount_pence, status, gateway, paypal_subscription_id)
            VALUES (%s,'subscription_activated',0,'activated','paypal',%s)
        """, (parent_id, subscription_id))
    return {"ok": True, "plan": "mms_monthly"}


def handle_paypal_webhook(event_type: str, resource: dict) -> dict:
    subscription_id = resource.get("id") or resource.get("billing_agreement_id", "")

    if event_type == "PAYMENT.SALE.COMPLETED":
        amount_pence = int(float(resource.get("amount", {}).get("total", "0")) * 100)
        period_end   = datetime.now(timezone.utc) + timedelta(days=30)
        with get_cur() as cur:
            cur.execute("""
                UPDATE subscriptions SET status='active', current_period_end=%s, updated_at=NOW()
                WHERE paypal_subscription_id=%s
            """, (period_end, subscription_id))
            cur.execute("SELECT user_id FROM subscriptions WHERE paypal_subscription_id=%s",
                        (subscription_id,))
            row = cur.fetchone()
            if row:
                cur.execute("""
                    INSERT INTO payment_events
                      (user_id, event_type, amount_pence, status, gateway, paypal_subscription_id)
                    VALUES (%s,'payment_captured',%s,'captured','paypal',%s)
                """, (row["user_id"], amount_pence, subscription_id))
        return {"ok": True, "action": "renewed"}

    elif event_type in ("BILLING.SUBSCRIPTION.CANCELLED", "BILLING.SUBSCRIPTION.SUSPENDED"):
        with get_cur() as cur:
            cur.execute("UPDATE subscriptions SET status='cancelled', updated_at=NOW() "
                        "WHERE paypal_subscription_id=%s", (subscription_id,))
        return {"ok": True, "action": "cancelled"}

    elif event_type == "PAYMENT.SALE.DENIED":
        with get_cur() as cur:
            cur.execute("UPDATE subscriptions SET status='payment_failed', updated_at=NOW() "
                        "WHERE paypal_subscription_id=%s", (subscription_id,))
        return {"ok": True, "action": "suspended"}

    elif event_type == "BILLING.SUBSCRIPTION.ACTIVATED":
        with get_cur() as cur:
            cur.execute("UPDATE subscriptions SET status='active', updated_at=NOW() "
                        "WHERE paypal_subscription_id=%s", (subscription_id,))
        return {"ok": True, "action": "activated"}

    return {"ok": True, "action": "ignored"}


def verify_paypal_webhook_signature(headers: dict, raw_body: bytes) -> bool:
    if not PAYPAL_WEBHOOK_ID:
        return True   # dev mode — skip verification
    import json as _json
    token   = _paypal_token()
    payload = {
        "auth_algo":         headers.get("PAYPAL-AUTH-ALGO", ""),
        "cert_url":          headers.get("PAYPAL-CERT-URL", ""),
        "transmission_id":   headers.get("PAYPAL-TRANSMISSION-ID", ""),
        "transmission_sig":  headers.get("PAYPAL-TRANSMISSION-SIG", ""),
        "transmission_time": headers.get("PAYPAL-TRANSMISSION-TIME", ""),
        "webhook_id":        PAYPAL_WEBHOOK_ID,
        "webhook_event":     _json.loads(raw_body),
    }
    try:
        r = requests.post(f"{PAYPAL_BASE}/v1/notifications/verify-webhook-signature",
                          json=payload,
                          headers={"Authorization": f"Bearer {token}",
                                   "Content-Type": "application/json"}, timeout=10)
        return r.json().get("verification_status") == "SUCCESS"
    except Exception:
        return False


# ── Admin helpers ─────────────────────────────────────────────────────────────

def get_all_subscriptions():
    with get_cur() as cur:
        cur.execute("""
            SELECT u.username, u.display_name, u.created_at, u.id as user_id,
                   s.plan, s.status, s.current_period_end, s.trial_started_at,
                   s.paypal_subscription_id,
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
