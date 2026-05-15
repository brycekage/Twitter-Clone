import sqlite3

DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        age INTEGER,
        bio TEXT,
        avatar TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        content TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        edited_at TEXT,
        parent_id INTEGER DEFAULT NULL
    )
    """)

    # Add missing columns to existing databases
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    for col, coltype in [("bio", "TEXT"), ("avatar", "TEXT")]:
        if col not in columns:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {coltype}")

    cursor.execute("PRAGMA table_info(messages)")
    columns = [row[1] for row in cursor.fetchall()]
    if "parent_id" not in columns:
        cursor.execute(
            "ALTER TABLE messages ADD COLUMN parent_id INTEGER DEFAULT NULL"
        )

    conn.commit()
    conn.close()