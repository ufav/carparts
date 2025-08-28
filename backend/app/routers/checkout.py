from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime
import json
from app.db.session import get_db
from app.schemas.order import CheckoutIn, OrderOut
from app.db.models.order import Order as OrderModel, OrderItem as OrderItemModel
from app.db.models.product import Product
from app.schemas.product import ProductOut


router = APIRouter(tags=["checkout", "orders"])


def _generate_order_number(db: Session) -> str:
    # Простой генератор номера на основе количества заказов
    last_id = db.execute(select(OrderModel.id).order_by(OrderModel.id.desc())).scalars().first()
    next_seq = (last_id or 0) + 1
    return f"R-{next_seq:06d}"


@router.post("/checkout", response_model=OrderOut)
def checkout(data: CheckoutIn, db: Session = Depends(get_db)):
    # Получаем товары и считаем суммы
    product_ids = [it.productId for it in data.items]
    products = db.query(Product).filter(Product.id.in_(product_ids), Product.is_active == True).all()
    id_to_product = {p.id: p for p in products}

    if len(id_to_product) != len(set(product_ids)):
        raise HTTPException(status_code=400, detail="Some products not found or inactive")

    subtotal = 0.0
    item_rows: list[OrderItemModel] = []
    for it in data.items:
        p = id_to_product[it.productId]
        price = float(p.price)
        total = price * it.quantity
        subtotal += total
        item_rows.append(OrderItemModel(
            product_id=p.id,
            product_name=p.name,
            product_sku=p.sku,
            quantity=it.quantity,
            unit_price=price,
            total_price=total,
            options=json.dumps([{"name": o.name, "value": o.value} for o in it.options]) if it.options else None,
        ))

    shipping = 0.0
    tax = 0.0
    discount = 0.0
    total = subtotal + shipping + tax - discount

    order_number = _generate_order_number(db)

    order = OrderModel(
        order_number=order_number,
        subtotal=subtotal,
        tax_amount=tax,
        shipping_amount=shipping,
        discount_amount=discount,
        total_amount=total,
        notes=data.comment or None,
        currency_code="USD",
    )
    db.add(order)
    db.flush()  # получить order.id

    for row in item_rows:
        row.order_id = order.id
        db.add(row)

    db.commit()
    db.refresh(order)

    # Готовим ответ
    items_resp = []
    for row in db.query(OrderItemModel).filter(OrderItemModel.order_id == order.id).all():
        prod = id_to_product.get(row.product_id)
        product_payload: ProductOut | dict
        if prod:
            product_payload = ProductOut.model_validate(prod)
        else:
            product_payload = {
                "id": row.product_id or 0,
                "name": row.product_name,
                "slug": "",
                "sku": row.product_sku,
                "part_number": None,
                "excerpt": None,
                "description": None,
                "price": float(row.unit_price),
                "compare_at_price": None,
                "stock_quantity": 0,
                "stock_status": "in-stock",
                "brand_id": None,
            }
        items_resp.append({
            "product": product_payload,
            "options": json.loads(row.options) if row.options else [],
            "price": float(row.unit_price),
            "quantity": row.quantity,
            "total": float(row.total_price),
        })

    totals = [
        {"title": "Subtotal", "price": float(order.subtotal)},
        {"title": "Shipping", "price": float(order.shipping_amount)},
        {"title": "Tax", "price": float(order.tax_amount)},
    ]

    return {
        "id": order.id,
        "token": order.order_number,
        "number": order.order_number,
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "payment": data.payment,
        "status": "pending",
        "items": items_resp,
        "quantity": sum(i["quantity"] for i in items_resp),
        "subtotal": float(order.subtotal),
        "totals": totals,
        "total": float(order.total_amount),
        "shippingAddress": data.shippingAddress,
        "billingAddress": data.billingAddress,
    }


@router.get("/orders/{order_id}", response_model=OrderOut)
def get_order_by_id(order_id: int, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(order, db)


@router.get("/orders/by-token/{token}", response_model=OrderOut)
def get_order_by_token(token: str, db: Session = Depends(get_db)):
    order = db.query(OrderModel).filter(OrderModel.order_number == token).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(order, db)


def _serialize_order(order: OrderModel, db: Session) -> OrderOut:
    item_rows = db.query(OrderItemModel).filter(OrderItemModel.order_id == order.id).all()
    product_ids = [row.product_id for row in item_rows if row.product_id]
    products = db.query(Product).filter(Product.id.in_(product_ids)).all() if product_ids else []
    id_to_product = {p.id: p for p in products}

    items_resp = []
    for row in item_rows:
        prod = id_to_product.get(row.product_id)
        product_payload: ProductOut | dict
        if prod:
            product_payload = ProductOut.model_validate(prod)
        else:
            product_payload = {
                "id": row.product_id or 0,
                "name": row.product_name,
                "slug": "",
                "sku": row.product_sku,
                "part_number": None,
                "excerpt": None,
                "description": None,
                "price": float(row.unit_price),
                "compare_at_price": None,
                "stock_quantity": 0,
                "stock_status": "in-stock",
                "brand_id": None,
            }
        items_resp.append({
            "product": product_payload,
            "options": json.loads(row.options) if row.options else [],
            "price": float(row.unit_price),
            "quantity": row.quantity,
            "total": float(row.total_price),
        })

    totals = [
        {"title": "Subtotal", "price": float(order.subtotal)},
        {"title": "Shipping", "price": float(order.shipping_amount)},
        {"title": "Tax", "price": float(order.tax_amount)},
    ]

    return OrderOut.model_validate({
        "id": order.id,
        "token": order.order_number,
        "number": order.order_number,
        "createdAt": datetime.utcnow().isoformat() + "Z",
        "payment": "unknown",
        "status": "pending",
        "items": items_resp,
        "quantity": sum(i["quantity"] for i in items_resp),
        "subtotal": float(order.subtotal),
        "totals": totals,
        "total": float(order.total_amount),
        "shippingAddress": {
            "firstName": "",
            "lastName": "",
            "email": None,
            "phone": "",
            "company": None,
            "address1": "",
            "address2": None,
            "city": "",
            "state": None,
            "country": None,
            "postcode": None,
        },
        "billingAddress": {
            "firstName": "",
            "lastName": "",
            "email": None,
            "phone": "",
            "company": None,
            "address1": "",
            "address2": None,
            "city": "",
            "state": None,
            "country": None,
            "postcode": None,
        },
    })


