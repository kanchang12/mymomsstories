"""
routes/public.py — landing page, sign-up (parent + child account in one
flow), and the feedback form from the landing page.
"""
import bcrypt
from flask import Blueprint, render_template, request, redirect, url_for, session
from models.db import get_cur
from services.content import list_languages
from services.credentials import generate_child_credentials
from services.videos import get_videos

public_bp = Blueprint("public", __name__)

# Common diaspora destinations + common heritage-language home countries.
# Not an exhaustive ISO list — extend freely.
COUNTRIES = [
    "United Kingdom", "United States", "Canada", "Australia", "New Zealand",
    "Ireland", "United Arab Emirates", "Saudi Arabia", "Qatar", "Kuwait",
    "Singapore", "Germany", "Netherlands", "France", "Spain", "Italy",
    "Poland", "Russia", "Ukraine", "Romania", "Moldova",
    "India", "Bangladesh", "Pakistan", "Sri Lanka", "Nepal",
    "Egypt", "Jordan", "Lebanon", "Morocco",
    "Mexico", "Argentina", "Colombia", "Japan", "Other",
]


@public_bp.route("/")
def landing():
    return render_template("landing.html")


@public_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")


@public_bp.route("/terms")
def terms():
    return render_template("terms.html")


@public_bp.route("/videos")
def videos():
    """Free public video library — no login required. Each video can carry
    multiple language audio tracks (set up per-video in YouTube Studio) —
    the viewer picks their language from the player's own settings gear
    (⚙ → Audio), so there's no language sorting needed on our side.
    See services/videos.py for setup."""
    video_list = get_videos()
    return render_template("videos.html", videos=video_list)


@public_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template(
            "register.html", error=None,
            countries=COUNTRIES, languages=list_languages(),
        )

    email        = (request.form.get("email") or "").strip().lower()
    password     = (request.form.get("password") or "").strip()
    country      = (request.form.get("country") or "").strip()
    language     = (request.form.get("language") or "").strip()
    child_nick   = (request.form.get("child_nickname") or "").strip()

    if not email or not password or len(password) < 8:
        return render_template("register.html", error="Email and a password of at least 8 characters are required.",
                                countries=COUNTRIES, languages=list_languages())
    if not country or not language:
        return render_template("register.html", error="Please choose a country and a language.",
                                countries=COUNTRIES, languages=list_languages())
    if not child_nick:
        return render_template("register.html", error="Give your child a nickname — not their real name.",
                                countries=COUNTRIES, languages=list_languages())

    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

    try:
        with get_cur() as cur:
            cur.execute("""
                INSERT INTO users (username, password_hash, role, display_name, country, language)
                VALUES (%s, %s, 'parent', %s, %s, %s) RETURNING id
            """, (email, pw_hash, email.split("@")[0], country, language))
            parent_id = str(cur.fetchone()["id"])
    except Exception as e:
        if "unique" in str(e).lower():
            return render_template("register.html", error="That email is already registered — try logging in instead.",
                                    countries=COUNTRIES, languages=list_languages())
        return render_template("register.html", error="Something went wrong, please try again.",
                                countries=COUNTRIES, languages=list_languages())

    child_username, child_password = generate_child_credentials()
    child_pw_hash = bcrypt.hashpw(child_password.encode(), bcrypt.gensalt(12)).decode()

    with get_cur() as cur:
        cur.execute("""
            INSERT INTO users (username, password_hash, role, display_name, country, language, parent_id)
            VALUES (%s, %s, 'child', %s, %s, %s, %s)
        """, (child_username, child_pw_hash, child_nick, country, language, parent_id))

    # Shown once, on the parent's dashboard after they log in — not stored
    # anywhere in plain text after that.
    session["new_child_creds"] = {
        "nickname": child_nick, "username": child_username, "password": child_password,
    }
    return redirect(url_for("auth.login", registered=1))


@public_bp.route("/feedback", methods=["POST"])
def feedback():
    name     = (request.form.get("name") or "").strip()
    email    = (request.form.get("email") or "").strip()
    req_lang = (request.form.get("requested_language") or "").strip()
    message  = (request.form.get("message") or "").strip()

    if message:
        with get_cur() as cur:
            cur.execute("""
                INSERT INTO feedback_messages (name, email, requested_language, message)
                VALUES (%s, %s, %s, %s)
            """, (name or None, email or None, req_lang or None, message))

    return render_template("feedback_thanks.html")
