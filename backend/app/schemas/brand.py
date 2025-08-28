from pydantic import BaseModel

class BrandOut(BaseModel):
    id: int
    slug: str
    name: str
    image: str | None = None
    country_code: str | None = None
    website: str | None = None

    class Config:
        from_attributes = True 