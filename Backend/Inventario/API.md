# API Documentation

## Overview
The Abarrotes Yamessi Inventory API provides REST endpoints for managing products, suppliers, and inventory movements.

## Base URL
When running locally: `http://localhost:8000`

## Products API

### List All Products
```
GET /api/products
```
Returns a list of all products.

### Get Product by ID
```
GET /api/products/{product_id}
```
Returns details of a specific product.

### Create Product
```
POST /api/products
Content-Type: application/json

{
  "sku": "PROD001",
  "name": "Product Name",
  "category": "Category Name",
  "subcategory": "Subcategory Name",
  "cost_price": 100.0,
  "sale_price": 150.0
}
```

### Update Product
```
PUT /api/products/{product_id}
Content-Type: application/json

{
  "sku": "PROD001",
  "name": "Updated Name",
  "category": "Updated Category",
  "subcategory": "Updated Subcategory",
  "cost_price": 120.0,
  "sale_price": 180.0
}
```

### Delete Product
```
DELETE /api/products/{product_id}
```

## Suppliers API

### List All Suppliers
```
GET /api/suppliers
```

### Get Supplier by ID
```
GET /api/suppliers/{supplier_id}
```

### Create Supplier
```
POST /api/suppliers
Content-Type: application/json

{
  "name": "Supplier Name",
  "contact": "Contact Person",
  "phone": "1234567890",
  "address": "Supplier Address"
}
```

### Update Supplier
```
PUT /api/suppliers/{supplier_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "contact": "Updated Contact",
  "phone": "9876543210",
  "address": "Updated Address"
}
```

### Delete Supplier
```
DELETE /api/suppliers/{supplier_id}
```

## Inventory Movements API

### List All Movements
```
GET /api/movements
```

### Get Movement by ID
```
GET /api/movements/{movement_id}
```

### Create Movement
```
POST /api/movements
Content-Type: application/json

{
  "product_id": 1,
  "type": "entry",  // "entry", "sale", or "adjustment"
  "quantity": 10,
  "supplier_id": 1,  // Optional
  "notes": "Initial stock"  // Optional
}
```

**Note:** Movements cannot be updated or deleted to maintain inventory history integrity.

### Movement Types
- **entry**: Adds stock to inventory (quantity is positive)
- **sale**: Removes stock from inventory (quantity is positive, stock is decreased)
- **adjustment**: Adjusts stock (quantity can be positive or negative)

## Testing

Run the test suite:
```bash
cd Backend/Inventario
python3 -m pytest test_api_integration.py -v
```

## Examples

### Example: Complete Workflow
```bash
# Create a supplier
curl -X POST http://localhost:8000/api/suppliers \
  -H "Content-Type: application/json" \
  -d '{"name": "Main Supplier", "phone": "1234567890"}'

# Create a product
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -d '{"sku": "WIDGET001", "name": "Widget", "cost_price": 10.0, "sale_price": 15.0}'

# Add inventory entry
curl -X POST http://localhost:8000/api/movements \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "type": "entry", "quantity": 100, "supplier_id": 1}'

# Make a sale
curl -X POST http://localhost:8000/api/movements \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "type": "sale", "quantity": 20}'

# Check product stock
curl http://localhost:8000/api/products/1
```
