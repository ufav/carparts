from pydantic import BaseModel

class CategoryOut(BaseModel):
    id: int
    parent_id: int | None = None
    name: str
    slug: str
    description: str | None = None
    image: str | None = None
    layout: str

    class Config:
        from_attributes = True 