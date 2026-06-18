#!/usr/bin/env python3
"""
scripts/create_admin.py — Run once on your server to create the first admin account.

Usage:
  python3 scripts/create_admin.py admin@yourdomain.com yourpassword
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from dotenv import load_dotenv
load_dotenv()

import bcrypt
from models.db import init_db, get_cur

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/create_admin.py <email> <password>")
        sys.exit(1)

    email    = sys.argv[1].strip().lower()
    password = sys.argv[2].strip()

    if len(password) < 8:
        print("Password must be at least 8 characters.")
        sys.exit(1)

    init_db()
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12)).decode()

    try:
        with get_cur() as cur:
            cur.execute("""
                INSERT INTO users (username, password_hash, role, display_name)
                VALUES (%s, %s, 'admin', %s)
            """, (email, pw_hash, email.split("@")[0]))
        print(f"✓ Admin account created: {email}")
        print(f"  Log in at /auth/login")
    except Exception as e:
        if "unique" in str(e).lower():
            print(f"An account with {email} already exists.")
        else:
            print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
