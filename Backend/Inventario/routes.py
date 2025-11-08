from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
import models
from datetime import datetime
from typing import List
from schemas import ProductCreate, Product, SupplierCreate, Supplier, MovementCreate, Movement

templates = Jinja2Templates(directory="templates")
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.on_event("startup")
def startup_event():
    init_db()


@router.get("/products")
def product_list(request: Request, q: str = "", db: Session = Depends(get_db)):
    query = db.query(models.Product)
    if q:
        qlike = f"%{q}%"
        query = query.filter((models.Product.name.ilike(qlike)) | (models.Product.sku.ilike(qlike)))
    products = query.order_by(models.Product.name).all()
    return templates.TemplateResponse("products.html", {"request": request, "products": products, "q": q})


@router.get("/products/add")
def product_add_form(request: Request):
    return templates.TemplateResponse("product_form.html", {"request": request, "product": None})


@router.post("/products/add")
def product_add(request: Request, sku: str = Form(...), name: str = Form(...), category: str = Form(""), subcategory: str = Form(""), cost_price: float = Form(0.0), sale_price: float = Form(0.0)):
    db = SessionLocal()
    existing = db.query(models.Product).filter_by(sku=sku).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="SKU already exists")
    p = models.Product(sku=sku, name=name, category=category, subcategory=subcategory, cost_price=cost_price, sale_price=sale_price)
    db.add(p)
    db.commit()
    db.close()
    return RedirectResponse(url="/products", status_code=303)


@router.get("/products/edit/{product_id}")
def product_edit_form(request: Request, product_id: int):
    db = SessionLocal()
    p = db.query(models.Product).get(product_id)
    db.close()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return templates.TemplateResponse("product_form.html", {"request": request, "product": p})


@router.post("/products/edit/{product_id}")
def product_edit(request: Request, product_id: int, sku: str = Form(...), name: str = Form(...), category: str = Form(""), subcategory: str = Form(""), cost_price: float = Form(0.0), sale_price: float = Form(0.0)):
    db = SessionLocal()
    p = db.query(models.Product).get(product_id)
    if not p:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    p.sku = sku
    p.name = name
    p.category = category
    p.subcategory = subcategory
    p.cost_price = cost_price
    p.sale_price = sale_price
    db.commit()
    db.close()
    return RedirectResponse(url="/products", status_code=303)


@router.post("/products/delete/{product_id}")
def product_delete(product_id: int):
    db = SessionLocal()
    p = db.query(models.Product).get(product_id)
    if not p:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(p)
    db.commit()
    db.close()
    return RedirectResponse(url="/products", status_code=303)


# Suppliers
@router.get("/suppliers")
def supplier_list(request: Request, db: Session = Depends(get_db)):
    suppliers = db.query(models.Supplier).order_by(models.Supplier.name).all()
    return templates.TemplateResponse("suppliers.html", {"request": request, "suppliers": suppliers})


@router.get("/suppliers/add")
def supplier_add_form(request: Request):
    return templates.TemplateResponse("supplier_form.html", {"request": request, "supplier": None})


@router.post("/suppliers/add")
def supplier_add(request: Request, name: str = Form(...), contact: str = Form(""), phone: str = Form(""), address: str = Form("")):
    db = SessionLocal()
    s = models.Supplier(name=name, contact=contact, phone=phone, address=address)
    db.add(s)
    db.commit()
    db.close()
    return RedirectResponse(url="/suppliers", status_code=303)


# Inventory movements
@router.get("/movements")
def movement_list(request: Request, product_id: int = None, from_date: str = None, to_date: str = None, db: Session = Depends(get_db)):
    query = db.query(models.InventoryMovement)
    if product_id:
        query = query.filter(models.InventoryMovement.product_id == product_id)
    if from_date:
        try:
            fd = datetime.fromisoformat(from_date)
            query = query.filter(models.InventoryMovement.date >= fd)
        except Exception:
            pass
    if to_date:
        try:
            td = datetime.fromisoformat(to_date)
            query = query.filter(models.InventoryMovement.date <= td)
        except Exception:
            pass
    movements = query.order_by(models.InventoryMovement.date.desc()).all()
    products = db.query(models.Product).order_by(models.Product.name).all()
    return templates.TemplateResponse("movements.html", {"request": request, "movements": movements, "products": products})


@router.get("/movements/add")
def movement_add_form(request: Request):
    db = SessionLocal()
    products = db.query(models.Product).order_by(models.Product.name).all()
    suppliers = db.query(models.Supplier).order_by(models.Supplier.name).all()
    db.close()
    return templates.TemplateResponse("movement_form.html", {"request": request, "products": products, "suppliers": suppliers})


@router.post("/movements/add")
def movement_add(request: Request, product_id: int = Form(...), type: str = Form(...), quantity: int = Form(...), supplier_id: int = Form(None), notes: str = Form("")):
    db = SessionLocal()
    p = db.query(models.Product).get(product_id)
    if not p:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    if type not in ("entry", "sale", "adjustment"):
        db.close()
        raise HTTPException(status_code=400, detail="Invalid movement type")
    # Update stock according to type
    if type == "entry":
        p.stock = p.stock + quantity
    elif type == "sale":
        if p.stock - quantity < 0:
            db.close()
            raise HTTPException(status_code=400, detail="Insufficient stock")
        p.stock = p.stock - quantity
    else:  # adjustment
        # for adjustments, quantity can be positive or negative
        p.stock = p.stock + quantity

    mv = models.InventoryMovement(product_id=product_id, type=type, quantity=quantity, supplier_id=supplier_id, notes=notes)
    db.add(mv)
    db.commit()
    db.close()
    return RedirectResponse(url="/movements", status_code=303)


# JSON API endpoints
@router.post("/api/products", response_model=Product)
def api_create_product(payload: ProductCreate):
    db = SessionLocal()
    existing = db.query(models.Product).filter_by(sku=payload.sku).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="SKU exists")
    p = models.Product(**payload.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    db.close()
    return p


@router.get("/api/products", response_model=List[Product])
def api_list_products():
    db = SessionLocal()
    ps = db.query(models.Product).order_by(models.Product.name).all()
    db.close()
    return ps


@router.get("/api/products/{product_id}", response_model=Product)
def api_get_product(product_id: int):
    db = SessionLocal()
    p = db.query(models.Product).get(product_id)
    db.close()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@router.put("/api/products/{product_id}", response_model=Product)
def api_update_product(product_id: int, payload: ProductCreate):
    db = SessionLocal()
    p = db.query(models.Product).get(product_id)
    if not p:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    # Check if SKU is being changed and if it conflicts
    if payload.sku != p.sku:
        existing = db.query(models.Product).filter_by(sku=payload.sku).first()
        if existing:
            db.close()
            raise HTTPException(status_code=400, detail="SKU already exists")
    for key, value in payload.dict().items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    db.close()
    return p


@router.delete("/api/products/{product_id}")
def api_delete_product(product_id: int):
    db = SessionLocal()
    p = db.query(models.Product).get(product_id)
    if not p:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(p)
    db.commit()
    db.close()
    return {"message": "Product deleted successfully"}


@router.post("/api/suppliers", response_model=Supplier)
def api_create_supplier(payload: SupplierCreate):
    db = SessionLocal()
    s = models.Supplier(**payload.dict())
    db.add(s)
    db.commit()
    db.refresh(s)
    db.close()
    return s


@router.get("/api/suppliers", response_model=List[Supplier])
def api_list_suppliers():
    db = SessionLocal()
    suppliers = db.query(models.Supplier).order_by(models.Supplier.name).all()
    db.close()
    return suppliers


@router.get("/api/suppliers/{supplier_id}", response_model=Supplier)
def api_get_supplier(supplier_id: int):
    db = SessionLocal()
    s = db.query(models.Supplier).get(supplier_id)
    db.close()
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return s


@router.put("/api/suppliers/{supplier_id}", response_model=Supplier)
def api_update_supplier(supplier_id: int, payload: SupplierCreate):
    db = SessionLocal()
    s = db.query(models.Supplier).get(supplier_id)
    if not s:
        db.close()
        raise HTTPException(status_code=404, detail="Supplier not found")
    for key, value in payload.dict().items():
        setattr(s, key, value)
    db.commit()
    db.refresh(s)
    db.close()
    return s


@router.delete("/api/suppliers/{supplier_id}")
def api_delete_supplier(supplier_id: int):
    db = SessionLocal()
    s = db.query(models.Supplier).get(supplier_id)
    if not s:
        db.close()
        raise HTTPException(status_code=404, detail="Supplier not found")
    db.delete(s)
    db.commit()
    db.close()
    return {"message": "Supplier deleted successfully"}


@router.post("/api/movements", response_model=Movement)
def api_create_movement(payload: MovementCreate):
    db = SessionLocal()
    p = db.query(models.Product).get(payload.product_id)
    if not p:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    if payload.type not in ("entry", "sale", "adjustment"):
        db.close()
        raise HTTPException(status_code=400, detail="Invalid type")
    if payload.type == "entry":
        p.stock = p.stock + payload.quantity
    elif payload.type == "sale":
        if p.stock - payload.quantity < 0:
            db.close()
            raise HTTPException(status_code=400, detail="Insufficient stock")
        p.stock = p.stock - payload.quantity
    else:
        p.stock = p.stock + payload.quantity
    mv = models.InventoryMovement(**payload.dict())
    db.add(mv)
    db.commit()
    db.refresh(mv)
    db.close()
    return mv


@router.get("/api/movements", response_model=List[Movement])
def api_list_movements():
    db = SessionLocal()
    movements = db.query(models.InventoryMovement).order_by(models.InventoryMovement.date.desc()).all()
    db.close()
    return movements


@router.get("/api/movements/{movement_id}", response_model=Movement)
def api_get_movement(movement_id: int):
    db = SessionLocal()
    mv = db.query(models.InventoryMovement).get(movement_id)
    db.close()
    if not mv:
        raise HTTPException(status_code=404, detail="Movement not found")
    return mv

