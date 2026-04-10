from sqlalchemy.orm import Session
from app.models.product import Product

import json
from app.core.redis import redis_client


# ✅ GET PRODUCTS (SEARCH + FILTER + SORT + CACHE)
def get_products(
    db: Session,
    search: str = None,
    min_price: float = None,
    max_price: float = None,
    sort_by: str = None
):

    cache_key = f"products:{search}:{min_price}:{max_price}:{sort_by}"

    try:
        cached = redis_client.get(cache_key)
        if cached:
            print("⚡ CACHE HIT")
            return json.loads(cached)
    except Exception:
        pass

    query = db.query(Product)

    # 🔍 SEARCH
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    # 💰 PRICE FILTER
    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    # 🔽 SORTING
    if sort_by == "price_asc":
        query = query.order_by(Product.price.asc())

    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())

    elif sort_by == "newest":
        query = query.order_by(Product.created_at.desc())

    products = query.all()

    result = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "stock": p.stock,
            "description": p.description
        }
        for p in products
    ]

    try:
        redis_client.setex(cache_key, 60, json.dumps(result))
    except Exception:
        pass

    print("📦 DB HIT")

    return result


# ✅ CREATE PRODUCT
def create_product(db: Session, data):
    product = Product(**data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)

    invalidate_cache()

    return product


# ✅ GET ALL PRODUCTS
def get_all_products(db: Session):
    return db.query(Product).all()


# ✅ GET PRODUCT BY ID
def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()


# ✅ UPDATE PRODUCT
def update_product(db: Session, product, data):
    for key, value in data.dict().items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)

    invalidate_cache()

    return product


# ✅ DELETE PRODUCT
def delete_product(db: Session, product):
    db.delete(product)
    db.commit()

    invalidate_cache()


# ✅ CACHE INVALIDATION (GLOBAL)
def invalidate_cache():
    try:
        keys = redis_client.keys("products:*")
        for key in keys:
            redis_client.delete(key)
    except Exception:
        pass
