# Abarrotes Yamessi - Base ligera (FastAPI)

Aplicación base para este hito: tienda pública + gestión de inventario + placeholders de PoS/reportes.

## Requisitos

```bash
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Rutas principales

- Tienda: `/`, `/catalog`, `/about-contact`, `/policies`
- Gestión: `/admin`, `/products`, `/suppliers`, `/movements`, `/admin/pos`, `/admin/reports`
- API docs: `/docs`

## Contratos y endpoints iniciales

- `GET /api/contracts/bootstrap`
- `GET/POST /api/sales/tickets`
- `GET/POST /api/orders`

Estos endpoints funcionan con servicio en memoria para iniciar captura estructurada sin depender todavía de backend transaccional completo.
