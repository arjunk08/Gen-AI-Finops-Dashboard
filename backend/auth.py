from passlib.context import CryptContext
from jose import jwt,JWTError
from datetime import timedelta,datetime
import os

password_context=CryptContext(schemes=["bcrypt"],deprecated="auto")

secret=os.getenv("KEY")


def hashp(passw: str):
    pass_hash=password_context.hash(passw)
    return pass_hash

def verify_password(passw: str,pass_hash: str):
    is_match=password_context.verify(passw,pass_hash)
    return is_match

def create_token(data:dict):
    payload=data.copy()
    expire=datetime.utcnow()+timedelta(minutes=10)

    payload.update({"expiry": expire})
    return jwt.encode(data,secret,algorithm="HS256")



def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms="HS256"
        )

        return payload

    except JWTError:
        return None


#class AuthMiddleware(BaseHTTPMiddleware):
  #  async def dispatch(self, request: Request, call_next):
   #     token = extract_token(request)
    #    if not token:
     #       raise exceptions.HTTPException(status_code=401, detail="Missing token")
      #  return await call_next(request)
    

