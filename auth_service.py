from fastapi import APIRouter, HTTPException, status, Response
from itsdangerous import URLSafeTimedSerializer as Serializer
from pydantic import BaseModel
import sqlite3
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime, timedelta

router = APIRouter()

load_dotenv()
SECRET_KEY = os.getenv("SECRET")
serializer = Serializer(SECRET_KEY, salt="session")

class User(BaseModel):
    username: str
    password: str

def add_user(username: str, password: str):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # setting subscription expiry as the time 10 minutes from the time of creation for testing
    subscription_expiry = datetime.now() + timedelta(minutes=10)
    formatted_expiry = subscription_expiry.isoformat()

    # setting current time as the start of subscription
    current_limits_start = datetime.now().isoformat()

    # setting the default subscription tier to free and renewal of feature limits for a week i.e. feature limits will keep renewing every week until expiry
    c.execute('INSERT INTO users (username, password, subscription, subscription_expiry, current_limits_start, limits_renewal) VALUES (?, ?, ?, ?, ?, ?)',
              (username, password, "free", formatted_expiry, current_limits_start, 7 * 24 * 60 * 60))
    conn.commit()
    conn.close()

@router.post("/signup")
def sign_up(user: User):
    try:
        # generate a hash of the plain text password to store at rest securely
        hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt())
        add_user(username=user.username, password=hashed_password)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {"message": "User created successfully"}

@router.post("/login")
def login(user: User, response: Response):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (user.username,))
    result = cursor.fetchone()
    conn.close()
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    stored_hashed_password = result[0]

    # compare the plain text password with the hash of the password stored in the database to check if they are the same
    if not bcrypt.checkpw(user.password.encode(), stored_hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    # If the user is successfully authenticated we set the cookie with the username and a max age of 1 hour
    session_token = serializer.dumps(user.username)
    response.set_cookie(key="session_token", value=session_token, httponly=True, samesite='Lax', max_age=3600)
    return {"message": "Login successful"}
