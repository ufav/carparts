from pydantic import BaseModel, Field


class ReviewOut(BaseModel):
    id: int
    date: str = Field(alias="created_at")
    author: str | None = None
    avatar: str | None = None
    rating: int
    content: str | None = Field(default=None, alias="comment")

    class Config:
        from_attributes = True
        populate_by_name = True


class ReviewCreate(BaseModel):
    rating: int
    author: str | None = None
    email: str | None = None
    content: str


