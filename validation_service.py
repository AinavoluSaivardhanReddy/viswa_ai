from itsdangerous import URLSafeTimedSerializer as Serializer
from fastapi import HTTPException, Depends, Cookie
from datetime import datetime, timedelta
from database import get_user
from dotenv import load_dotenv
import os, sqlite3
from collections import namedtuple

load_dotenv()

SECRET_KEY = os.getenv("SECRET")
serializer = Serializer(SECRET_KEY, salt="session")

def get_user(username: str):
    User = namedtuple('User', 'username password subscription subscription_expiry current_limits_start limits_renewal')
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    result = c.fetchone()
    conn.close()
    if result:
        return User(*result)
    return None

def get_user_details(username: str):
    try:
        # get user from sqllite db
        user_details = get_user(username=username)._asdict()
        return user_details
    except Exception as e:
        raise Exception("Unable to fetch the user:", str(e))

def validate_user(session_token: str = Cookie(None)):
    if session_token is None:
        raise HTTPException(status_code=401, detail="Session token is required")
    try:
        # fetch the username from the cookie
        username = serializer.loads(session_token, max_age=3600)
        user_details = get_user_details(username)
        
        # We are checking if the subscirption of the user is not expired
        if user_details and datetime.strptime(user_details['subscription_expiry'], '%Y-%m-%dT%H:%M:%S.%f') > datetime.now():
            return user_details
        else:
            print(user_details['subscription_expiry'])
            raise Exception("Subscription expired or not found.")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))