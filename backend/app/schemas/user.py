from pydantic import BaseModel, EmailStr


class UserOut(BaseModel):
    email: EmailStr
    phone: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    avatar: str | None = None

    class Config:
        from_attributes = True


class SignInIn(BaseModel):
    email: EmailStr
    password: str


class SignUpIn(BaseModel):
    email: EmailStr
    password: str
    firstName: str | None = None
    lastName: str | None = None
    phone: str | None = None


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

