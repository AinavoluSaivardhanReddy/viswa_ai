import sqlite3

def create_user_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            subscription TEXT,
            subscription_expiry DATE,
            current_limits_start DATE,
            limits_renewal INT
        )
    ''')
    conn.commit()
    conn.close()