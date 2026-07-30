# Abarrotes Yamessi

Primer hito de una base práctica y ligera para **ventas en línea + inventario + PoS móvil**.

## Estado actual del repositorio (auditoría rápida)

- `Backend/Inventario`: ahora es la base activa (FastAPI + Jinja + SQLite).
- `homepage/`: contenido legado del sitio estático; se conserva por seguridad y referencia, pero ya **no es el flujo recomendado** para este hito.

## Alcance de este hito

- Estructura inicial separando **Tienda pública** y **Gestión**.
- Placeholders de módulos: catálogo, PoS y reportes.
- Inventario funcional (productos, proveedores, movimientos).
- Base de localización `es` / `en` (español por defecto).
- Tema de contraste alto por defecto y controles grandes.
- Contratos tipados para productos, transacciones de inventario, tickets de venta y órdenes.

## Ejecución local

```bash
cd Backend/Inventario
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Abrir:
- Sitio/tienda: `http://localhost:8000/`
- Gestión: `http://localhost:8000/admin`
- API docs: `http://localhost:8000/docs`

## Arquitectura inicial

- **Storefront**: `/`, `/catalog`, `/about-contact`, `/policies`
- **Gestión**: `/admin`, `/products`, `/suppliers`, `/movements`, `/admin/pos`, `/admin/reports`
- **API base**:
  - Inventario existente (`/api/products`, `/api/suppliers`, `/api/movements`)
  - Contratos y flujos iniciales (`/api/contracts/bootstrap`, `/api/sales/tickets`, `/api/orders`)

## Recomendaciones para dispositivos de gama baja

- Mantener servidor en red local cuando sea posible.
- Evitar imágenes pesadas en catálogo inicial.
- Preferir formularios simples y tablas paginadas en próximos pasos.
- Limitar scripts de terceros (este hito elimina dependencias visuales pesadas en la base activa).

## Roadmap por fases

1. **Hito 1 (actual)**: base ligera + estructura módulos + contratos.
2. **Hito 2**: flujo PoS operativo (carrito, pagos, cierre diario).
3. **Hito 3**: tienda en línea conectada a stock/reservas y reglas de entrega.
4. **Hito 4**: reportes clave y exportaciones.
5. **Hito 5**: hardware (impresora/escáner) y reconocimiento de productos (posterior).

## Open Questions (para el siguiente prompt)

1. ¿Cuáles son las categorías iniciales y los 20 productos prioritarios para precargar?
2. ¿Qué campos son obligatorios por producto (SKU, código de barras, unidad, costo, precio, impuesto)?
3. ¿Cuáles son horarios, zonas de entrega/retiro y reglas de cumplimiento de pedidos?
4. ¿Qué métodos de pago se requieren en el lanzamiento?
5. ¿Español será el idioma por defecto para todos los usuarios?
6. ¿Qué reportes son críticos en el mes 1 (ventas diarias, margen, alertas de inventario)?

### Plantilla repetible: “Preguntas para el siguiente prompt”

```md
## Preguntas para el siguiente prompt
- Datos de negocio pendientes:
- Decisiones de flujo PoS pendientes:
- Reglas de pedidos/entrega pendientes:
- Prioridades de reportes pendientes:
- Supuestos a confirmar:
```
