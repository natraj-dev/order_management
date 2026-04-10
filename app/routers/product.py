from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import (
    create_product,
    get_products,   # ✅ FIXED
    get_product_by_id,
    update_product,
    delete_product,
)
from app.core.security import require_admin

router = APIRouter(prefix="/products", tags=["Products"])


#  Add Product (Admin only)
@router.post("/", response_model=ProductResponse)
def add_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    return create_product(db, data)


#  Get all products (Public - WITH CACHE)
@router.get("/")
def get_products_api(
    search: str = None,
    min_price: float = None,
    max_price: float = None,
    sort_by: str = None,
    db: Session = Depends(get_db)
):
    return get_products(db, search, min_price, max_price, sort_by)


#  Get product by ID
@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


#  Update (Admin only)
@router.put("/{product_id}", response_model=ProductResponse)
def update_product_api(
    product_id: int,
    data: ProductCreate,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return update_product(db, product, data)


#  Delete (Admin only)
@router.delete("/{product_id}")
def delete_product_api(
    product_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    product = get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    delete_product(db, product)
    return {"message": "Product deleted"}
