"""
My Mom's Stories — Main Flask App · LOVEUAD LTD
"""
import os
from datetime import timedelta
from flask import Flask, redirect, url_for, session
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "mymomsstories-dev-key-change-in-prod")
app.permanent_session_lifetime = timedelta(days=30)
CORS(app, supports_credentials=True)

from routes.auth   import auth_bp
from routes.child  import child_bp
from routes.parent import parent_bp
from routes.public import public_bp
from models.db     import init_db

init_db()

app.register_blueprint(public_bp, url_prefix="")
app.register_blueprint(auth_bp,   url_prefix="/auth")
app.register_blueprint(child_bp,  url_prefix="/child")
app.register_blueprint(parent_bp, url_prefix="/parent")


@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("public.landing"))
    if session.get("role") == "parent":
        return redirect(url_for("parent.dashboard"))
    return redirect(url_for("child.dashboard"))


@app.errorhandler(404)
def not_found(e):
    return "<h2>Page not found</h2><a href='/'>Home</a>", 404


@app.errorhandler(500)
def server_error(e):
    return f"<h2>Server error</h2><pre>{e}</pre><a href='/'>Home</a>", 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
