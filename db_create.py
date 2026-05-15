import sqlite3
import os

DB_NAME = "database.db"

def ensure_schema():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            age INTEGER,
            bio TEXT,
            avatar TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            edited_at TEXT,
            parent_id INTEGER DEFAULT NULL
        )
    """)

    # Add avatar column if missing (for existing databases)
    cur.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cur.fetchall()]
    if "avatar" not in columns:
        cur.execute("ALTER TABLE users ADD COLUMN avatar TEXT")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    ensure_schema()