from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.db.models.brand import Brand
from app.schemas.brand import BrandOut

router = APIRouter(tags=["brands"])

@router.get("/brands", response_model=List[BrandOut])
def list_brands(db: Session = Depends(get_db)):
    return db.query(Brand).filter(Brand.is_active == True).order_by(Brand.name).all() 