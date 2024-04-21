import redis
from functools import wraps
from fastapi import HTTPException, APIRouter, Query
from datetime import datetime, timedelta
import sqlite3

router = APIRouter()

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# update the date of limits reset(current_limits_start) as the given renewal date
def update_user_limits(username, renewal_date):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET current_limits_start = ? WHERE username = ?;
    ''', (renewal_date, username))
    conn.commit()
    conn.close()

def track_feature_usage(feature_name: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user = kwargs.get('user')
            if not user:
                raise HTTPException(status_code=401, detail="User not authenticated or session expired")
            username = user['username']
            subscription = user['subscription'] # the name of the subscription tier
            current_limits_start = user['current_limits_start'] # the date when the feature limtis were last reset
            limits_renewal = user['limits_renewal'] # the time period after which the feature limits are reset
            renewal_date = datetime.strptime(current_limits_start, '%Y-%m-%dT%H:%M:%S.%f') + timedelta(seconds=limits_renewal)

            # checking based on the last date of limits reset if we have to reset the limits again based on the renewal timeperiod
            if renewal_date < datetime.now():
                update_user_limits(username=username, renewal_date=renewal_date)
            limit = get_subscription_limits(feature_name=feature_name, subscription=subscription)
            usage_count = redis_client.hget(f"user:{username}:features", feature_name)
            if usage_count and int(usage_count) >= limit:
                raise HTTPException(status_code=429, detail="Feature limit exceeded")
            redis_client.hincrby(f"user:{username}:features", feature_name, 1)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


@router.get('/usage')
def get_feature_usage (feature_name: str = Query(..., description="The name of the feature to check usage for")
                       , username: str = Query(..., description="The username for which to check the feature usage")):
    try:
        usage_count = redis_client.hget(f"user:{username}:features", feature_name)
        if usage_count is None:
            return {"message": "No usage found for this feature or user."}
        return {"feature": feature_name, "usage": int(usage_count)}
    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {str(e)}")
    
# set different features limits for corresponding subscription tires
def get_subscription_limits(feature_name: str, subscription: str):
    if subscription == "free":
        if feature_name == "Summarize":
            return 5
        # you can add separate feature limits and subscription tiers here
    return 0