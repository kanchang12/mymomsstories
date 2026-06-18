"""
models/db.py — Per-request PostgreSQL connections (no pool)
Same pattern as aitutor/models/db.py — avoids SSL stale-connection errors
on Neon/Supabase with idle timeouts.
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager

_DB_URL = None


def init_db():
    global _DB_URL
    _DB_URL = os.environ.get("DATABASE_URL")
    if not _DB_URL:
        print("[DB] WARNING: DATABASE_URL not set.")
        return
    _run_migrations()
    print("[DB] Ready.")


def _new_conn():
    return psycopg2.connect(
        _DB_URL,
        cursor_factory=RealDictCursor,
        keepalives=1,
        keepalives_idle=30,
        keepalives_interval=10,
        keepalives_count=5,
        connect_timeout=10,
    )


@contextmanager
def get_conn():
    conn = _new_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass


@contextmanager
def get_cur():
    with get_conn() as conn:
        cur = conn.cursor()
        try:
            yield cur
        finally:
            try:
                cur.close()
            except Exception:
                pass


def _run_migrations():
    mdir = os.path.join(os.path.dirname(__file__), "..", "migrations")
    with get_conn() as conn:
        cur = conn.cursor()
        _ensure_migrations_table(cur)
        conn.commit()
        for fname in sorted(os.listdir(mdir)):
            if not fname.endswith(".sql"):
                continue
            _ensure_migrations_table(cur)
            cur.execute("SELECT 1 FROM _migrations WHERE filename = %s", (fname,))
            if cur.fetchone():
                continue
            with open(os.path.join(mdir, fname)) as f:
                cur.execute(f.read())
            _ensure_migrations_table(cur)
            cur.execute("INSERT INTO _migrations (filename) VALUES (%s)", (fname,))
            conn.commit()
            print(f"[DB] Applied: {fname}")


def _ensure_migrations_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS _migrations (
            filename TEXT PRIMARY KEY,
            applied_at TIMESTAMPTZ DEFAULT NOW()
        )
    """)
