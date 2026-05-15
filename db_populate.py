import sqlite3
import random
from datetime import datetime, timedelta

DB_NAME = "database.db"

USERNAMES = [
    "Brandy", "Heather", "Channing", "Brianna", "Amber",
    "Serena", "Melody", "Dakota", "Sierra", "Bambi",
    "Crystal", "Samantha", "Autumn", "Ruby", "Taylor",
    "Tara", "Tammy", "Lauren", "Charlene", "Chantelle",
    "Courtney", "Misty", "Jenny", "Krista", "Mindy",
    "Noel", "Shelby", "Trina", "Reba", "Cassandra",
    "Nikki", "Kelsey", "Shawna", "Jolene", "Urleen",
    "Claudia", "Savannah", "Casey", "Dolly", "Kendra",
    "Kylie", "Chloe", "Devon", "Emmalou", "Becky"
]

TEMPLATES = [
    "Why so serious?",
    "To infinity and beyond!",
    "Just keep swimming, just keep swimming.",
    "You can't handle the truth!",
    "I am your father.",
    "Life is like a box of chocolates, you never know what you're gonna get.",
    "Why do I smell toast? I always smell toast before something bad happens.",
    "Elementary, my dear Watson.",
    "Here's looking at you, kid.",
    "You had me at hello.",
    "I'll be back.",
    "May the Force be with you.",
    "There's no place like home.",
    "Just when I thought I was out, they pull me back in.",
    "Why are you running?!",
    "You is kind, you is smart, you is important.",
    "Nobody puts Baby in a corner.",
    "I see dead people.",
    "We're gonna need a bigger boat.",
    "My precious."
]

def random_time():
    start = datetime(2025, 1, 1)
    end = datetime(2026, 5, 11)
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # SPEED BOOST (important even for 40k)
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=OFF;")
    cursor.execute("PRAGMA temp_store=MEMORY;")

    # Clear old messages
    cursor.execute("DELETE FROM messages")

    ########################
    # Ensure users exist

    cursor.execute("SELECT id, username FROM users")
    user_map = {row[1]: row[0] for row in cursor.fetchall()}

    for name in USERNAMES:
        if name not in user_map:
            cursor.execute(
                "INSERT INTO users (username, password, age, avatar) VALUES (?, ?, ?, ?)",
                (name, "test", random.randint(18, 30), f"https://robohash.org/{name}.png?size=200x200")
            )
            user_map[name] = cursor.lastrowid
            
    conn.commit()
    print("Users ready.")

    ######################
    # Generate messages

    TOTAL = 40_000
    BATCH_SIZE = 5_000

    batch = []

    print("Generating 40,000 messages...")

    for i in range(TOTAL):
        username = random.choice(USERNAMES)
        user_id = user_map[username]

        content = random.choice(TEMPLATES)
        timestamp = random_time().strftime("%Y-%m-%d %H:%M:%S")

        batch.append((user_id, content, timestamp))

        if len(batch) >= BATCH_SIZE:
            cursor.executemany("""
                INSERT INTO messages (user_id, content, timestamp)
                VALUES (?, ?, ?)
            """, batch)

            conn.commit()
            batch = []

            print(f"Inserted {i+1}/{TOTAL}")

    # insert leftover rows
    if batch:
        cursor.executemany("""
            INSERT INTO messages (user_id, content, timestamp)
            VALUES (?, ?, ?)
        """, batch)

    conn.commit()
    conn.close()

    print("DONE: 40,000 messages inserted.")

if __name__ == "__main__":
    main()