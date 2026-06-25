from fastapi import HTTPException
from datetime import datetime, timedelta




def check_ai_request(payload):
    if not payload.question or not payload.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )
    
    if len(payload.question)>500:
        raise HTTPException(
            status_code=400,
            detail="Question is too large, this is a demo"
        )
    
user_log={}


user_request_log = {}


def check_rate_limit(user_id: int, limit: int = 5, window_minutes: int = 15):
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=window_minutes)

    if user_id not in user_request_log:
        user_request_log[user_id] = []

    user_request_log[user_id] = [
        timestamp
        for timestamp in user_request_log[user_id]
        if timestamp > window_start
    ]

    if len(user_request_log[user_id]) >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again later. Limit: {limit} requests per {window_minutes} minutes."
        )

    user_request_log[user_id].append(now)
    
    

