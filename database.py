import sqlite3
from collections import namedtuple
from datetime import datetime, timedelta

DATABASE_USER_PATH = 'users.db'

def create_user_db():
    conn = sqlite3.connect(DATABASE_USER_PATH)
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

def add_user(username: str, password: str):
    conn = sqlite3.connect(DATABASE_USER_PATH)
    c = conn.cursor()

    # setting subscription expiry as the time 10 minutes from the time of creation for testing
    subscription_expiry = datetime.now() + timedelta(minutes=10)
    formatted_expiry = subscription_expiry.isoformat()

    # setting current time as the start of subscription
    current_limits_start = datetime.now().isoformat()

    c.execute('INSERT INTO users (username, password, subscription, subscription_expiry, current_limits_start, limits_renewal) VALUES (?, ?, ?, ?, ?, ?)',
              (username, password, "free", formatted_expiry, current_limits_start, 7 * 24 * 60 * 60))
    conn.commit()
    conn.close()

def get_user(username: str):
    User = namedtuple('User', 'username password subscription subscription_expiry current_limits_start limits_renewal')
    conn = sqlite3.connect(DATABASE_USER_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return User(*result)
    return None
        
