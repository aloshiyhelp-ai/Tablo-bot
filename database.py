import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ball.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

# ===== TABLES =====
cursor.execute("""
CREATE TABLE IF NOT EXISTS sessions (
    chat_id TEXT PRIMARY KEY,
    starter_id TEXT,
    starter_name TEXT,
    topic_name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS points (
    chat_id TEXT,
    target_id TEXT,
    target_name TEXT,
    points INTEGER,
    PRIMARY KEY (chat_id, target_id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS topics (
    chat_id TEXT,
    topic_name TEXT,
    target_id TEXT,
    target_name TEXT,
    points INTEGER,
    PRIMARY KEY (chat_id, topic_name, target_id)
)
""")

conn.commit()

# ===== SESSION =====
def start_session(chat_id, starter_id, starter_name, topic_name):
    cursor.execute(
        "INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?)",
        (chat_id, starter_id, starter_name, topic_name)
    )
    conn.commit()

def stop_session(chat_id):
    cursor.execute("DELETE FROM sessions WHERE chat_id=?", (chat_id,))
    conn.commit()

def get_session(chat_id):
    cursor.execute("SELECT * FROM sessions WHERE chat_id=?", (chat_id,))
    row = cursor.fetchone()
    if row:
        return {
            "chat_id": row[0],
            "starter_id": row[1],
            "starter_name": row[2],
            "topic_name": row[3],
        }
    return None

# ===== POINTS =====
def add_points(chat_id, target_id, target_name, points):
    cursor.execute("""
    INSERT INTO points (chat_id, target_id, target_name, points)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(chat_id, target_id)
    DO UPDATE SET points = points + ?, target_name = excluded.target_name
    """, (chat_id, target_id, target_name, points, points))
    conn.commit()

def get_user_points(chat_id, target_id):
    cursor.execute(
        "SELECT points FROM points WHERE chat_id=? AND target_id=?",
        (chat_id, target_id)
    )
    row = cursor.fetchone()
    return row[0] if row else 0

def get_user_total(target_id):
    cursor.execute("""
    SELECT SUM(points) FROM points WHERE target_id=?
    """, (target_id,))
    row = cursor.fetchone()
    return row[0] or 0

def get_user_topics(target_id):
    cursor.execute("""
    SELECT topic_name, SUM(points)
    FROM topics
    WHERE target_id=?
    GROUP BY topic_name
    """, (target_id,))
    return cursor.fetchall()

# ===== TOPIC =====
def add_topic_points(chat_id, topic_name, target_id, target_name, points):
    cursor.execute("""
    INSERT INTO topics (chat_id, topic_name, target_id, target_name, points)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(chat_id, topic_name, target_id)
    DO UPDATE SET points = points + ?, target_name = excluded.target_name
    """, (chat_id, topic_name, target_id, target_name, points, points))
    conn.commit()

def get_topic_top(chat_id, topic_name, limit=10):
    cursor.execute("""
    SELECT target_name, points
    FROM topics
    WHERE chat_id=? AND topic_name=?
    ORDER BY points DESC
    LIMIT ?
    """, (chat_id, topic_name, limit))
    return cursor.fetchall()

def get_all_topics(chat_id):
    cursor.execute("""
    SELECT DISTINCT topic_name FROM topics WHERE chat_id=?
    """, (chat_id,))
    return [r[0] for r in cursor.fetchall()]

# ===== UMUMIY REYTING =====
def get_overall_top(limit=10):
    cursor.execute("""
    SELECT target_name, SUM(points) as total
    FROM points
    GROUP BY target_id
    ORDER BY total DESC
    LIMIT ?
    """, (limit,))
    return cursor.fetchall()