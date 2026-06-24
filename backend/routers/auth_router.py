from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from db_end.models import userid
from backend.dependancies import get_db
from backend.auth import hashp, verify_password,create_token


router = APIRouter()


class RegisterRequest(BaseModel):
    email: str
    password: str
    username: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register_user(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(userid).filter(userid.email == payload.email).first()
    print("Password value:", payload.password)
    print("Password byte length:", len(payload.password.encode("utf-8")))


    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    if len(payload.password.encode("utf-8"))>72:
        raise HTTPException(
            status_code=400,
            detail="TOO LONG"
        )

    new_user = userid(
        email=payload.email,
        username=payload.username,
        hashed_password=hashp(payload.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully",
        "user_id": new_user.id
    }


@router.post("/login")
def login_user(
    payload: LoginRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(userid).filter(userid.email == payload.email).first()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(payload.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_token(
        data={"sub": str(existing_user.id)}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": existing_user.id,
            "email": existing_user.email,
            "username": existing_user.username
        }
    }

@router.post("/token")
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    existing_user = db.query(userid).filter(userid.email == form_data.username).first()

    if existing_user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(form_data.password, existing_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_token(
        data={"sub": str(existing_user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }