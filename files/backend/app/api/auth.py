from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.models import Profile, User
from app.utils.database import get_db
from app.utils.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    fullName: str
    email: EmailStr
    password: str
    confirmPassword: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if not payload.fullName.strip():
        raise HTTPException(400, "Full name is required.")
    if len(payload.password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters.")
    if payload.password != payload.confirmPassword:
        raise HTTPException(400, "Passwords do not match.")

    email = payload.email.lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(409, "An account with this email already exists.")

    user = User(full_name=payload.fullName.strip(), email=email, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    db.add(Profile(user_id=user.id))
    db.commit()

    token = create_access_token(user.id)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "fullName": user.full_name,
            "email": user.email,
            "createdAt": user.created_at.isoformat(),
        },
    }


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Incorrect email or password.")

    token = create_access_token(user.id)
    return {
        "token": token,
        "user": {
            "id": user.id,
            "fullName": user.full_name,
            "email": user.email,
            "createdAt": user.created_at.isoformat(),
        },
    }


@router.post("/logout")
def logout():
    # JWTs are stateless -- nothing to invalidate server-side in this reference
    # build. The endpoint exists so the frontend has a symmetrical call, and is
    # the natural place to add token revocation/blacklisting in production.
    return {"ok": True}
