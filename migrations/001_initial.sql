-- 001_initial.sql — My Mom's Stories, PostgreSQL schema

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Users (parents and children share one table, like Cosmo) ────────
CREATE TABLE IF NOT EXISTS users (
    id                        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username                  TEXT NOT NULL UNIQUE,      -- parent: email. child: generated, e.g. "tiger42"
    password_hash             TEXT NOT NULL,
    role                      TEXT NOT NULL CHECK (role IN ('parent','child')),
    display_name              TEXT NOT NULL,             -- parent: their name. child: the nickname parent chose
    country                   TEXT,                      -- ISO-2 country code, set at sign-up
    language                  TEXT,                      -- active heritage language code, e.g. 'bn','hi','ar'
    parent_id                 UUID REFERENCES users(id) ON DELETE CASCADE,  -- set on child rows only
    usage_minutes_this_month  INT NOT NULL DEFAULT 0,     -- heartbeat-tracked, resets when usage_month rolls over
    usage_month               TEXT,                       -- 'YYYY-MM', compared each heartbeat to detect rollover
    created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login                TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_users_parent_id ON users(parent_id);

-- ── Activity log — every attempt at every stop, for the parent dashboard ──
CREATE TABLE IF NOT EXISTS activity_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    child_id    UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    language    TEXT NOT NULL,
    stop        TEXT NOT NULL CHECK (stop IN ('alphabet','words','lines','customs','story')),
    item_key    TEXT NOT NULL,      -- which letter / word / line / custom / story was shown
    item_shown  TEXT NOT NULL,      -- the actual text shown, in script
    transcript  TEXT,               -- what the child said (browser speech-to-text), NULL for customs/story reads
    score       INT,                -- 0-100, NULL for stops with no spoken check
    feedback    TEXT,               -- short encouraging note from Gemini
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_activity_child_id   ON activity_log(child_id);
CREATE INDEX IF NOT EXISTS idx_activity_created_at ON activity_log(created_at);

-- ── Feedback / "tell us what's missing" form on the landing page ────
CREATE TABLE IF NOT EXISTS feedback_messages (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name                TEXT,
    email               TEXT,
    requested_language  TEXT,
    message             TEXT NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
