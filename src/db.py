import sqlite3
from pathlib import Path

DB_PATH = Path("diabetes.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS glucose_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        value REAL NOT NULL,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS symptom_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        symptom TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


def save_glucose(user_id: str, value: float, note: str = ""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO glucose_log (user_id, value, note) VALUES (?, ?, ?)",
        (user_id, value, note)
    )

    conn.commit()
    conn.close()


def get_recent_glucose(user_id: str, limit: int = 5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT value, note, created_at
        FROM glucose_log
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


def save_symptom(user_id: str, symptom: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO symptom_log (user_id, symptom) VALUES (?, ?)",
        (user_id, symptom)
    )

    conn.commit()
    conn.close()


def get_recent_symptoms(user_id: str, limit: int = 5):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT symptom, created_at
        FROM symptom_log
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit)
    )

    rows = cursor.fetchall()
    conn.close()
    return rows