# API Documentation

## Core inventory endpoints

- `GET /api/products`
- `POST /api/products`
- `GET /api/products/{product_id}`
- `PUT /api/products/{product_id}`
- `DELETE /api/products/{product_id}`

- `GET /api/suppliers`
- `POST /api/suppliers`
- `GET /api/suppliers/{supplier_id}`
- `PUT /api/suppliers/{supplier_id}`
- `DELETE /api/suppliers/{supplier_id}`

- `GET /api/movements`
- `POST /api/movements`
- `GET /api/movements/{movement_id}`

## New milestone contracts

- `GET /api/contracts/bootstrap`
  - Returns mandatory product fields and initial statuses for orders/tickets.

- `GET /api/sales/tickets`
- `POST /api/sales/tickets`
  - Structured sales ticket payload and totals (in-memory service).

- `GET /api/orders`
- `POST /api/orders`
  - Structured online order payload (in-memory service).

## Notes

- SQLite remains the persistence for products/suppliers/movements.
- Sales tickets and orders use in-memory placeholder storage in this milestone.
- Hardware integration and item recognition are intentionally deferred.
