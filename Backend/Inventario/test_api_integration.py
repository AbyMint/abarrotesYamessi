"""
Integration tests for the Abarrotes Yamessi Inventory API.
These tests start the FastAPI server and test it via HTTP requests.
"""
import pytest
import subprocess
import time
import requests
import os
import signal


@pytest.fixture(scope="module")
def server():
    """Start the FastAPI server for testing"""
    # Remove test database if it exists
    test_db = "test_inventory.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    # Set test database
    os.environ["DATABASE_URL"] = f"sqlite:///./{test_db}"
    
    # Start server
    process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8888"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:8888/api/products", timeout=1)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)
    else:
        process.kill()
        pytest.fail("Server failed to start")
    
    yield "http://127.0.0.1:8888"
    
    # Cleanup
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=5)
    if os.path.exists(test_db):
        os.remove(test_db)


class TestProductsAPI:
    """Test Product API endpoints"""
    
    def test_create_product(self, server):
        """Test creating a product"""
        response = requests.post(
            f"{server}/api/products",
            json={
                "sku": "TEST001",
                "name": "Test Product",
                "category": "Electronics",
                "cost_price": 100.0,
                "sale_price": 150.0
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sku"] == "TEST001"
        assert data["name"] == "Test Product"
        assert data["stock"] == 0
    
    def test_list_products(self, server):
        """Test listing products"""
        response = requests.get(f"{server}/api/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the one we created
    
    def test_get_product_by_id(self, server):
        """Test getting a specific product"""
        # Create a product first
        create_response = requests.post(
            f"{server}/api/products",
            json={"sku": "TEST002", "name": "Another Product"}
        )
        product_id = create_response.json()["id"]
        
        # Get the product
        response = requests.get(f"{server}/api/products/{product_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["sku"] == "TEST002"
    
    def test_update_product(self, server):
        """Test updating a product"""
        # Create a product
        create_response = requests.post(
            f"{server}/api/products",
            json={"sku": "TEST003", "name": "Original Name"}
        )
        product_id = create_response.json()["id"]
        
        # Update the product
        response = requests.put(
            f"{server}/api/products/{product_id}",
            json={"sku": "TEST003", "name": "Updated Name", "cost_price": 200.0}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["cost_price"] == 200.0
    
    def test_delete_product(self, server):
        """Test deleting a product"""
        # Create a product
        create_response = requests.post(
            f"{server}/api/products",
            json={"sku": "TEST004", "name": "To Delete"}
        )
        product_id = create_response.json()["id"]
        
        # Delete the product
        response = requests.delete(f"{server}/api/products/{product_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = requests.get(f"{server}/api/products/{product_id}")
        assert get_response.status_code == 404


class TestSuppliersAPI:
    """Test Supplier API endpoints"""
    
    def test_create_supplier(self, server):
        """Test creating a supplier"""
        response = requests.post(
            f"{server}/api/suppliers",
            json={"name": "Test Supplier", "phone": "1234567890"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Supplier"
    
    def test_list_suppliers(self, server):
        """Test listing suppliers"""
        response = requests.get(f"{server}/api/suppliers")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_supplier_by_id(self, server):
        """Test getting a specific supplier"""
        # Create a supplier
        create_response = requests.post(
            f"{server}/api/suppliers",
            json={"name": "Supplier 2"}
        )
        supplier_id = create_response.json()["id"]
        
        # Get the supplier
        response = requests.get(f"{server}/api/suppliers/{supplier_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == supplier_id
    
    def test_update_supplier(self, server):
        """Test updating a supplier"""
        # Create a supplier
        create_response = requests.post(
            f"{server}/api/suppliers",
            json={"name": "Original Supplier"}
        )
        supplier_id = create_response.json()["id"]
        
        # Update the supplier
        response = requests.put(
            f"{server}/api/suppliers/{supplier_id}",
            json={"name": "Updated Supplier", "phone": "9876543210"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Supplier"
    
    def test_delete_supplier(self, server):
        """Test deleting a supplier"""
        # Create a supplier
        create_response = requests.post(
            f"{server}/api/suppliers",
            json={"name": "To Delete"}
        )
        supplier_id = create_response.json()["id"]
        
        # Delete the supplier
        response = requests.delete(f"{server}/api/suppliers/{supplier_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = requests.get(f"{server}/api/suppliers/{supplier_id}")
        assert get_response.status_code == 404


class TestMovementsAPI:
    """Test Inventory Movement API endpoints"""
    
    def test_create_entry_movement(self, server):
        """Test creating an entry movement"""
        # Create a product first
        product_response = requests.post(
            f"{server}/api/products",
            json={"sku": "MVTEST001", "name": "Movement Test Product"}
        )
        product_id = product_response.json()["id"]
        
        # Create entry movement
        response = requests.post(
            f"{server}/api/movements",
            json={
                "product_id": product_id,
                "type": "entry",
                "quantity": 10,
                "notes": "Initial stock"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "entry"
        assert data["quantity"] == 10
        
        # Verify stock increased
        product = requests.get(f"{server}/api/products/{product_id}").json()
        assert product["stock"] == 10
    
    def test_create_sale_movement(self, server):
        """Test creating a sale movement"""
        # Create product and add stock
        product_response = requests.post(
            f"{server}/api/products",
            json={"sku": "MVTEST002", "name": "Sale Test Product"}
        )
        product_id = product_response.json()["id"]
        
        requests.post(
            f"{server}/api/movements",
            json={"product_id": product_id, "type": "entry", "quantity": 20}
        )
        
        # Create sale movement
        response = requests.post(
            f"{server}/api/movements",
            json={"product_id": product_id, "type": "sale", "quantity": 5}
        )
        assert response.status_code == 200
        
        # Verify stock decreased
        product = requests.get(f"{server}/api/products/{product_id}").json()
        assert product["stock"] == 15
    
    def test_insufficient_stock(self, server):
        """Test that sale fails with insufficient stock"""
        product_response = requests.post(
            f"{server}/api/products",
            json={"sku": "MVTEST003", "name": "No Stock Product"}
        )
        product_id = product_response.json()["id"]
        
        response = requests.post(
            f"{server}/api/movements",
            json={"product_id": product_id, "type": "sale", "quantity": 10}
        )
        assert response.status_code == 400
        assert "Insufficient stock" in response.json()["detail"]
    
    def test_list_movements(self, server):
        """Test listing movements"""
        response = requests.get(f"{server}/api/movements")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_movement_by_id(self, server):
        """Test getting a specific movement"""
        # Create product and movement
        product_response = requests.post(
            f"{server}/api/products",
            json={"sku": "MVTEST004", "name": "Get Movement Product"}
        )
        product_id = product_response.json()["id"]
        
        create_response = requests.post(
            f"{server}/api/movements",
            json={"product_id": product_id, "type": "entry", "quantity": 10}
        )
        movement_id = create_response.json()["id"]
        
        # Get the movement
        response = requests.get(f"{server}/api/movements/{movement_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == movement_id


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_complete_workflow(self, server):
        """Test complete workflow: supplier, product, and movements"""
        # Create supplier
        supplier_response = requests.post(
            f"{server}/api/suppliers",
            json={"name": "Main Supplier", "phone": "1234567890"}
        )
        supplier_id = supplier_response.json()["id"]
        
        # Create product
        product_response = requests.post(
            f"{server}/api/products",
            json={
                "sku": "WIDGET001",
                "name": "Widget",
                "cost_price": 10.0,
                "sale_price": 15.0
            }
        )
        product_id = product_response.json()["id"]
        
        # Add stock entry
        requests.post(
            f"{server}/api/movements",
            json={
                "product_id": product_id,
                "type": "entry",
                "quantity": 100,
                "supplier_id": supplier_id
            }
        )
        
        # Make sales
        requests.post(
            f"{server}/api/movements",
            json={"product_id": product_id, "type": "sale", "quantity": 20}
        )
        requests.post(
            f"{server}/api/movements",
            json={"product_id": product_id, "type": "sale", "quantity": 15}
        )
        
        # Check final stock
        product = requests.get(f"{server}/api/products/{product_id}").json()
        assert product["stock"] == 65
