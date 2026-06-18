-- 002_billing.sql — PayPal subscription billing
-- Flat plan: £15/month per parent account, no per-child quantity.
-- Each child still gets 15 included hours/month and £1.50/hr overage,
-- tracked in users.usage_minutes_this_month (unchanged, from 001).
-- Overage itself is NOT auto-charged by this migration — see README.

CREATE TABLE IF NOT EXISTS app_config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
    user_id                 UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    plan                    TEXT NOT NULL DEFAULT 'none',   -- 'none' | 'mms_monthly'
    status                  TEXT NOT NULL DEFAULT 'inactive', -- inactive | active | payment_failed | cancelled
    paypal_subscription_id  TEXT,
    paypal_payer_id         TEXT,
    current_period_end      TIMESTAMPTZ,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS payment_events (
    id                      SERIAL PRIMARY KEY,
    user_id                 UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type              TEXT NOT NULL,
    amount_pence            INT NOT NULL DEFAULT 0,
    status                  TEXT NOT NULL,
    gateway                 TEXT NOT NULL DEFAULT 'paypal',
    paypal_subscription_id  TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
