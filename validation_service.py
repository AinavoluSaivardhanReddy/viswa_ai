from itsdangerous import URLSafeTimedSerializer as Serializer
from fastapi import HTTPException, Depends, Cookie
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os, sqlite3
import redis
from collections import namedtuple

load_dotenv()

SECRET_KEY = os.getenv("SECRET")
serializer = Serializer(SECRET_KEY, salt="session")
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

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
        # Here we are caching the user details in redis to speed up the retrival
        cached_user_details = redis_client.get(f"user_details:{username}")
        if cached_user_details:
            return eval(cached_user_details)
        else:
            # in case of cache miss we read directly from the sqllite database and set the cache with 10 minutes ttl
            user_details = get_user(username=username)._asdict()
            if user_details:
                redis_client.setex(f"user_details:{username}", timedelta(minutes=10), str(user_details))
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