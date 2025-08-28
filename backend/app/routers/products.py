from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.db.models.product import Product, ProductCategory
from app.db.models.category import Category
from app.schemas.product import ProductOut
from app.db.models.review import Review
from app.schemas.review import ReviewOut, ReviewCreate

router = APIRouter(tags=["products"])

@router.get("/products", response_model=List[ProductOut])
def list_products(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Поиск по названию"),
    brand_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    query = db.query(Product).filter(Product.is_active == True)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    # category_id фильтрация потребует join к product_categories, опустим пока

    return query.order_by(Product.id.desc()).offset(offset).limit(limit).all() 


## NOTE: Маршруты с фиксированными путями должны идти выше динамического /products/{slug}


def _apply_category_slug_filter(query, db: Session, category_slug: Optional[str]):
    if not category_slug:
        return query
    return (
        query.join(ProductCategory, ProductCategory.product_id == Product.id)
        .join(Category, Category.id == ProductCategory.category_id)
        .filter(Category.slug == category_slug)
    )


@router.get("/products/featured", response_model=List[ProductOut])
def get_featured_products(
    category_slug: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active == True)
    query = _apply_category_slug_filter(query, db, category_slug)
    # Placeholder сортировка для featured
    return query.order_by(Product.id.desc()).limit(limit).all()


@router.get("/products/{product_id}/reviews", response_model=List[ReviewOut])
def get_product_reviews(
    product_id: int,
    limit: int = Query(8, ge=1, le=100),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    q = (
        db.query(Review)
        .filter(Review.product_id == product_id)
        .order_by(Review.id.desc())
    )
    offset = (page - 1) * limit
    return q.offset(offset).limit(limit).all()


@router.post("/products/{product_id}/reviews", response_model=ReviewOut, status_code=201)
def add_product_review(
    product_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    review = Review(
        product_id=product_id,
        rating=data.rating,
        comment=data.content,
        is_approved=True,
        is_verified_purchase=False,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/products/popular", response_model=List[ProductOut])
def get_popular_products(
    category_slug: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active == True)
    query = _apply_category_slug_filter(query, db, category_slug)
    # Proxy: популярные по количеству на складе
    return query.order_by(Product.stock_quantity.desc(), Product.id.desc()).limit(limit).all()


@router.get("/products/top-rated", response_model=List[ProductOut])
def get_top_rated_products(
    category_slug: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active == True)
    query = _apply_category_slug_filter(query, db, category_slug)
    # Нет поля рейтинга — используем стабильную сортировку по id
    return query.order_by(Product.id.asc()).limit(limit).all()


@router.get("/products/latest", response_model=List[ProductOut])
def get_latest_products(
    category_slug: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Product).filter(Product.is_active == True)
    query = _apply_category_slug_filter(query, db, category_slug)
    return query.order_by(Product.id.desc()).limit(limit).all()


@router.get("/products/special-offers", response_model=List[ProductOut])
def get_special_offers(
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    # Предложения со скидкой: compare_at_price задана и больше текущей цены
    query = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.compare_at_price.isnot(None))
    )
    return query.order_by(Product.id.desc()).limit(limit).all()


@router.get("/products/{slug}", response_model=ProductOut)
def get_product_by_slug(slug: str, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .filter(Product.is_active == True)
        .filter(Product.slug == slug)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product