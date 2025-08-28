from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.user import User
from app.schemas.user import UserOut


router = APIRouter(tags=["account"]) 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/sign-in")
JWT_SECRET = "dev-secret"
JWT_ALG = "HS256"


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        user_id = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="Inactive user")
    return user


@router.get("/account/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


