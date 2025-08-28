from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional, TypedDict
from app.db.session import get_db
from app.db.models.product import Product
from app.db.models.category import Category
from app.schemas.product import ProductOut
from app.schemas.category import CategoryOut


router = APIRouter(tags=["search"])


class SearchSuggestionsResponse(TypedDict):
    products: List[ProductOut]
    categories: List[CategoryOut]


@router.get("/search/suggestions", response_model=SearchSuggestionsResponse)
def get_search_suggestions(
    q: str = Query(..., min_length=1),
    limitProducts: int = Query(4, ge=1, le=50),
    limitCategories: int = Query(4, ge=1, le=50),
    db: Session = Depends(get_db),
):
    products_query = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.name.ilike(f"%{q}%"))
        .order_by(Product.id.desc())
        .limit(limitProducts)
    )
    categories_query = (
        db.query(Category)
        .filter(Category.is_active == True)
        .filter(Category.name.ilike(f"%{q}%"))
        .order_by(Category.id.desc())
        .limit(limitCategories)
    )

    return {
        "products": products_query.all(),
        "categories": categories_query.all(),
    }


