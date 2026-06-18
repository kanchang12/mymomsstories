"""
routes/auth.py — login/logout. One users table, role decides where you land.
Same pattern as aitutor/routes/auth.py.
"""
import bcrypt
from functools import wraps
from flask import Blueprint, request, session, redirect, url_for, render_template
from models.db import get_cur

auth_bp = Blueprint("auth", __name__)


def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.login"))
            if role and session.get("role") != role:
                return redirect(url_for("auth.login"))
            return f(*args, **kwargs)
        return wrapper
    return decorator


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None, registered=request.args.get("registered"))

    username = (request.form.get("username") or "").strip().lower()
    password = (request.form.get("password") or "").encode()

    with get_cur() as cur:
        cur.execute(
            "SELECT id, password_hash, role, display_name, country, language, parent_id "
            "FROM users WHERE username = %s", (username,)
        )
        row = cur.fetchone()

    if not row or not bcrypt.checkpw(password, row["password_hash"].encode()):
        return render_template("login.html", error="Wrong username or password.", registered=None)

    with get_cur() as cur:
        cur.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (str(row["id"]),))

    session.permanent = True
    session["user_id"]      = str(row["id"])
    session["username"]     = username
    session["role"]         = row["role"]
    session["display_name"] = row["display_name"]
    session["country"]      = row["country"]
    session["language"]     = row["language"]
    session["parent_id"]    = str(row["parent_id"]) if row.get("parent_id") else None

    if row["role"] == "parent":
        return redirect(url_for("parent.dashboard"))
    return redirect(url_for("child.dashboard"))


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("public.landing"))
