from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models.category import Category
from app.schemas.category import CategoryOut

router = APIRouter(tags=["categories"])

@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.is_active == True).order_by(Category.name).all() 


@router.get("/categories/{slug}", response_model=CategoryOut)
def get_category_by_slug(slug: str, db: Session = Depends(get_db)):
    category = (
        db.query(Category)
        .filter(Category.is_active == True)
        .filter(Category.slug == slug)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category