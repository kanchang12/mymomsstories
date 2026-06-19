-- 004_stripe_billing.sql — Switch billing gateway from PayPal to Stripe.
-- Renames the gateway-specific columns; existing PayPal subscription/payer
-- IDs are kept as-is under the new column names (harmless — they're just
-- opaque strings, and active PayPal subscribers will need to be migrated
-- to a Stripe subscription manually or re-subscribe).

ALTER TABLE subscriptions RENAME COLUMN paypal_subscription_id TO stripe_subscription_id;
ALTER TABLE subscriptions RENAME COLUMN paypal_payer_id TO stripe_customer_id;

ALTER TABLE payment_events RENAME COLUMN paypal_subscription_id TO stripe_subscription_id;
ALTER TABLE payment_events ALTER COLUMN gateway SET DEFAULT 'stripe';

-- Drop the cached PayPal plan_id — Stripe will auto-provision its own
-- product+price on first subscribe and cache it under 'stripe_price_id'.
DELETE FROM app_config WHERE key = 'paypal_plan_id';
