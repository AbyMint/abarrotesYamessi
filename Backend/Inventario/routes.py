from datetime import datetime
from typing import List, Optional
from urllib.parse import urlencode

import models
from contracts import (
    BootstrapContractsResponse,
    Order,
    OrderCreate,
    SalesTicket,
    SalesTicketCreate,
)
from database import SessionLocal, init_db
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from i18n import get_translator
from schemas import Movement, MovementCreate, Product, ProductCreate, Supplier, SupplierCreate
from services import InMemorySalesOrderService
from sqlalchemy.orm import Session

templates = Jinja2Templates(directory="templates")
router = APIRouter()
sales_order_service = InMemorySalesOrderService()



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.on_event("startup")
def startup_event():
    init_db()



def get_preferences(request: Request) -> tuple[str, str]:
    lang = request.query_params.get("lang", "es")
    contrast_mode = request.query_params.get("contrast", "high")
    if lang not in {"es", "en"}:
        lang = "es"
    if contrast_mode not in {"high", "standard"}:
        contrast_mode = "high"
    return lang, contrast_mode



def build_url(path: str, lang: str, contrast_mode: str) -> str:
    params = {}
    if lang != "es":
        params["lang"] = lang
    if contrast_mode != "high":
        params["contrast"] = contrast_mode
    return f"{path}?{urlencode(params)}" if params else path



def render_with_preferences(template_name: str, request: Request, **context):
    lang, contrast_mode = get_preferences(request)
    translator = get_translator(lang)
    current_path = request.url.path
    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            "lang": lang,
            "contrast_mode": contrast_mode,
            "t": translator,
            "url_with_prefs": lambda path: build_url(path, lang, contrast_mode),
            "lang_es_url": build_url(current_path, "es", contrast_mode),
            "lang_en_url": build_url(current_path, "en", contrast_mode),
            "contrast_high_url": build_url(current_path, lang, "high"),
            "contrast_standard_url": build_url(current_path, lang, "standard"),
            **context,
        },
    )



def get_sales_service() -> InMemorySalesOrderService:
    return sales_order_service


@router.get("/", include_in_schema=False)
def storefront_home(request: Request):
    return render_with_preferences("storefront_home.html", request)


@router.get("/catalog", include_in_schema=False)
def storefront_catalog(request: Request):
    return render_with_preferences("catalog.html", request)


@router.get("/about-contact", include_in_schema=False)
def storefront_about_contact(request: Request):
    return render_with_preferences("about_contact.html", request)


@router.get("/policies", include_in_schema=False)
def storefront_policies(request: Request):
    return render_with_preferences("policies.html", request)


@router.get("/admin", include_in_schema=False)
def admin_dashboard(request: Request):
    return render_with_preferences("admin_dashboard.html", request)


@router.get("/admin/pos", include_in_schema=False)
def admin_pos_dashboard(request: Request):
    return render_with_preferences("pos_dashboard.html", request)


@router.get("/admin/reports", include_in_schema=False)
def admin_reports_dashboard(request: Request):
    return render_with_preferences("reports_overview.html", request)


@router.get("/products")
def product_list(request: Request, q: str = "", db: Session = Depends(get_db)):
    query = db.query(models.Product)
    if q:
        qlike = f"%{q}%"
        query = query.filter((models.Product.name.ilike(qlike)) | (models.Product.sku.ilike(qlike)))
    products = query.order_by(models.Product.name).all()
    return render_with_preferences("products.html", request, products=products, q=q)


@router.get("/products/add")
def product_add_form(request: Request):
    return render_with_preferences("product_form.html", request, product=None)


@router.post("/products/add")
def product_add(
    request: Request,
    sku: str = Form(...),
    name: str = Form(...),
    category: str = Form(""),
    subcategory: str = Form(""),
    cost_price: float = Form(0.0),
    sale_price: float = Form(0.0),
):
    db = SessionLocal()
    existing = db.query(models.Product).filter_by(sku=sku).first()
    if existing:
        db.close()
        raise HTTPException(status_code=400, detail="SKU already exists")
    p = models.Product(
        sku=sku,
        name=name,
        category=category,
        subcategory=subcategory,
        cost_price=cost_price,
        sale_price=sale_price,
    )
    db.add(p)
    db.commit()
    db.close()
    return RedirectResponse(url=str(request.url_for("product_list")), status_code=303)


@router.get("/products/edit/{product_id}")
def product_edit_form(request: Request, product_id: int):
    db = SessionLocal()
    p = db.query(models.Product).get(product_id)
    db.close()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return render_with_preferences("product_form.html", request, product=p)


@router.post("/products/edit/{product_id}")
def product_edit(
    request: Request,
    product_id: int,
    sku: str = Form(...),
    name: str = Form(...),
    category: str = Form(""),
    subcategory: str = Form(""),
    cost_price: float = Form(0.0),
    sale_price: float = Form(0.0),
):
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
    return RedirectResponse(url=str(request.url_for("product_list")), status_code=303)


@router.post("/products/delete/{product_id}")
def product_delete(request: Request, product_id: int):
    db = SessionLocal()
    p = db.query(models.Product).get(product_id)
    if not p:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(p)
    db.commit()
    db.close()
    return RedirectResponse(url=str(request.url_for("product_list")), status_code=303)


@router.get("/suppliers")
def supplier_list(request: Request, db: Session = Depends(get_db)):
    suppliers = db.query(models.Supplier).order_by(models.Supplier.name).all()
    return render_with_preferences("suppliers.html", request, suppliers=suppliers)


@router.get("/suppliers/add")
def supplier_add_form(request: Request):
    return render_with_preferences("supplier_form.html", request, supplier=None)


@router.post("/suppliers/add")
def supplier_add(
    request: Request,
    name: str = Form(...),
    contact: str = Form(""),
    phone: str = Form(""),
    address: str = Form(""),
):
    db = SessionLocal()
    s = models.Supplier(name=name, contact=contact, phone=phone, address=address)
    db.add(s)
    db.commit()
    db.close()
    return RedirectResponse(url=str(request.url_for("supplier_list")), status_code=303)


@router.get("/movements")
def movement_list(
    request: Request,
    product_id: Optional[int] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.InventoryMovement)
    if product_id:
        query = query.filter(models.InventoryMovement.product_id == product_id)
    if from_date:
        try:
            fd = datetime.fromisoformat(from_date)
            query = query.filter(models.InventoryMovement.date >= fd)
        except ValueError:
            pass
    if to_date:
        try:
            td = datetime.fromisoformat(to_date)
            query = query.filter(models.InventoryMovement.date <= td)
        except ValueError:
            pass
    movements = query.order_by(models.InventoryMovement.date.desc()).all()
    products = db.query(models.Product).order_by(models.Product.name).all()
    return render_with_preferences("movements.html", request, movements=movements, products=products)


@router.get("/movements/add")
def movement_add_form(request: Request):
    db = SessionLocal()
    products = db.query(models.Product).order_by(models.Product.name).all()
    suppliers = db.query(models.Supplier).order_by(models.Supplier.name).all()
    db.close()
    return render_with_preferences("movement_form.html", request, products=products, suppliers=suppliers)


@router.post("/movements/add")
def movement_add(
    request: Request,
    product_id: int = Form(...),
    type: str = Form(...),
    quantity: int = Form(...),
    supplier_id: Optional[int] = Form(None),
    notes: str = Form(""),
):
    db = SessionLocal()
    p = db.query(models.Product).get(product_id)
    if not p:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")
    if type not in ("entry", "sale", "adjustment"):
        db.close()
        raise HTTPException(status_code=400, detail="Invalid movement type")

    if type == "entry":
        p.stock = p.stock + quantity
    elif type == "sale":
        if p.stock - quantity < 0:
            db.close()
            raise HTTPException(status_code=400, detail="Insufficient stock")
        p.stock = p.stock - quantity
    else:
        p.stock = p.stock + quantity

    mv = models.InventoryMovement(
        product_id=product_id,
        type=type,
        quantity=quantity,
        supplier_id=supplier_id,
        notes=notes,
    )
    db.add(mv)
    db.commit()
    db.close()
    return RedirectResponse(url=str(request.url_for("movement_list")), status_code=303)


@router.get("/api/contracts/bootstrap", response_model=BootstrapContractsResponse)
def api_contracts_bootstrap():
    return BootstrapContractsResponse(
        product_fields=["sku", "name", "barcode", "unit_type", "cost_price", "sale_price", "tax_rate"],
        mandatory_product_fields=["sku", "name", "sale_price"],
        order_statuses=["pending", "confirmed", "ready", "delivered", "cancelled"],
        ticket_statuses=["draft", "paid", "cancelled"],
    )


@router.get("/api/sales/tickets", response_model=List[SalesTicket])
def api_list_sales_tickets(service: InMemorySalesOrderService = Depends(get_sales_service)):
    return service.list_tickets()


@router.post("/api/sales/tickets", response_model=SalesTicket)
def api_create_sales_ticket(payload: SalesTicketCreate, service: InMemorySalesOrderService = Depends(get_sales_service)):
    return service.create_ticket(payload)


@router.get("/api/orders", response_model=List[Order])
def api_list_orders(service: InMemorySalesOrderService = Depends(get_sales_service)):
    return service.list_orders()


@router.post("/api/orders", response_model=Order)
def api_create_order(payload: OrderCreate, service: InMemorySalesOrderService = Depends(get_sales_service)):
    return service.create_order(payload)


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
