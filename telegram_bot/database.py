import sqlite3

DB_PATH = "users.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                language TEXT,
                level TEXT
            )
        ''')
        conn.commit()

def get_user(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return c.fetchone()

def set_user(user_id, language, level):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO users (user_id, language, level)
            VALUES (?, ?, ?)
        """, (user_id, language, level))
        conn.commit()

def update_language(user_id, language):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        conn.commit()

def update_level(user_id, level):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET level = ? WHERE user_id = ?", (level, user_id))
        conn.commit()
