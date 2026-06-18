-- 003_admin_trial.sql — admin role + 7-day trial

-- Add admin role
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;
ALTER TABLE users ADD CONSTRAINT users_role_check CHECK (role IN ('parent','child','admin'));

-- Add trial_started_at to subscriptions
ALTER TABLE subscriptions
    ADD COLUMN IF NOT EXISTS trial_started_at TIMESTAMPTZ DEFAULT NOW();

-- Backfill trial_started_at from users.created_at for existing parents
UPDATE subscriptions s
SET trial_started_at = u.created_at
FROM users u
WHERE s.user_id = u.id
  AND s.trial_started_at IS NULL;

-- Any parent without a subscription row gets a trial
INSERT INTO subscriptions (user_id, plan, status, trial_started_at)
SELECT id, 'trial', 'active', created_at
FROM users WHERE role='parent'
ON CONFLICT (user_id) DO NOTHING;
