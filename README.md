# My Mom's Stories — backend

Flask + PostgreSQL + Gemini. Same architecture as your aitutor app: per-request
psycopg2 connections, auto-applied SQL migrations, one `users` table for both
parents and children, bcrypt passwords, session-based auth.

## Run it

```
pip install -r requirements.txt --break-system-packages
cp .env.example .env   # fill in DATABASE_URL, GEMINI_API_KEY, SECRET_KEY
python3 app.py
```

This has been run for real against a live PostgreSQL 16 database in
testing — not just read over. Tested and confirmed working: landing page,
register → auto-generated child credentials, parent login, child login,
wrong-password rejection, child dashboard item fetch (alphabet/words/lines/
customs/story), attempt scoring with graceful fallback when no Gemini key is
set, activity logging, usage heartbeat incrementing correctly, parent
dashboard showing records, clear-data deleting only the right child's rows,
and the cross-parent ownership check (parent A can't clear parent B's child's
data — confirmed 404).

## How the reading/pronunciation check works

Same pattern as `aitutor/services/language_reader.py`: the **browser** does
speech-to-text via the Web Speech API (`SpeechRecognition`), which already
covers bn-IN, hi-IN, mr-IN, ta-IN, te-IN, kn-IN, ml-IN, ar-SA, es-ES,
ja-JP, ru-RU, uk-UA and ro-RO in Chrome. The transcript — plain text — gets sent to Gemini for a
short scoring call. No audio ever leaves the browser, no audio tokens, no
ElevenLabs. This is the cheap path from our cost discussion, even cheaper
than estimated since it's pure text in/out.

## A bug worth checking in aitutor too

`gemini_client.py` originally built the `genai.Client()` at import time —
same as `language_reader.py` does today. If `GEMINI_API_KEY` isn't set, that
raises immediately and **crashes the whole app on startup**, before a single
page can load. Caught this by actually running the app without a key
configured. Fixed here by making the client lazy (built on first real use,
inside a try/except that already existed for the Gemini call itself). Worth
porting the same fix into `aitutor/services/language_reader.py` since it has
the identical line.

## What's real vs. what's seed/stub

- **Real and working**: every route, the DB schema, the credential
  generator, the usage/overage tracking, the clear-data flow, the landing
  page (SEO/AEO schema, mobile-hardened, light-brown theme, an illustrated
  "open passport" hero in place of the plain paper-texture look, the school-
  worksheet ruled-line background swapped for a subtler dot-grain texture).
- **13 languages**: Bengali, Hindi, Marathi, Tamil, Telugu, Kannada,
  Malayalam, Arabic, Spanish, Japanese, Russian, Ukrainian, Romanian.
  `services/content.py` has alphabet/words/lines/customs/two-stories for
  all 13, written carefully but **not reviewed by a native speaker per
  language**. Tamil, Telugu, Kannada and Malayalam are where I'd trust this
  least without someone fluent checking it; the same caution applies to the
  Cyrillic content (Russian/Ukrainian) and Romanian's diacritics. The two
  stories per language are a title plus a short original synopsis, not a
  proper retelling — swap those in before this goes near real families.
- **Billing: the £15/month base subscription is wired up via Stripe Checkout**
  — `services/payments.py` auto-provisions its own product+price, caches the
  price_id in `app_config`. `/parent/stripe/subscribe` → Stripe Checkout
  → `/parent/stripe/success` activates it (fast-path), `/webhooks/stripe`
  keeps status in sync on renew/cancel/payment-failed (source of truth).
  Needs real `STRIPE_SECRET_KEY` in `.env` to actually create the price —
  it'll throw on first subscribe attempt without it, not fail silently.
  **What's still NOT wired:** the £1.50/hr overage past 15 included
  hours/month. It's tracked (`users.usage_minutes_this_month`) and shown on
  the parent dashboard, but not auto-charged — that needs Stripe metered
  billing wired in separately. Don't read the dashboard number as money
  already collected.

## Structure

Mirrors aitutor: `app.py`, `Procfile`, `models/db.py`, `migrations/*.sql`,
`routes/{auth,public,child,parent,webhooks}.py`, `services/{content,scoring,
credentials,gemini_client,payments}.py`, `templates/*.html`,
`static/img/hero.jpg`.
