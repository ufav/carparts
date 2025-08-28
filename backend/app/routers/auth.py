from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import SignInIn, SignUpIn, TokenOut, UserOut
from app.core.config import settings


router = APIRouter(tags=["auth"]) 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/sign-in")

JWT_SECRET = "dev-secret"  # вынести в .env при необходимости
JWT_ALG = "HS256"
JWT_EXPIRES_MIN = 60 * 24


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRES_MIN)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


@router.post("/auth/sign-up", response_model=UserOut)
def sign_up(data: SignUpIn, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == data.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        first_name=data.firstName,
        last_name=data.lastName,
        phone=data.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/sign-in", response_model=TokenOut)
def sign_in(data: SignInIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(subject=str(user.id))
    return TokenOut(access_token=token)


