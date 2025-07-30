
import pytest
from database.models import Supplier, Product, Inventory, Purchase, PurchaseItem
from datetime import date

@pytest.fixture
def supplier(session):
    s = Supplier(name="Test Supplier")
    session.add(s)
    session.commit()
    return s

@pytest.fixture
def product_and_inventory(session):
    p = Product(
        name="Test Product",
        product_typed=1,
        brand_name="MarcaX",
        price=5.0,
        cost=4.0
    )
    session.add(p)
    session.flush()

    inv = Inventory(product_id=p.id, quantity=10)
    session.add(inv)
    session.commit()

    return p, inv

@pytest.mark.integration
def test_purchase_stock_page(client):
    response = client.get('/purchase_stock/purchase_stock')
    assert response.status_code == 200
    # Ajusta el siguiente assert según tu contenido real en la plantilla
    assert b"purchase_stock" in response.data.lower() or b"purchase" in response.data.lower()

@pytest.mark.integration
def test_process_purchase_success(client, session, supplier, product_and_inventory):
    product, inventory = product_and_inventory

    payload = {
        "supplier": supplier.name,
        "purchase_id": 12345,
        "date": "2025-07-23",
        "products": [
            {"product": product.name, "quantity": 5, "cost": 10.5}
        ]
    }

    response = client.post('/purchase_stock/process_purchase', json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert data['status'] == 'success'
    assert "Purchase processed successfully" in data['message']

    # Check inventory updated
    inv = session.query(Inventory).filter_by(id=inventory.id).first()
    assert inv.quantity == 15  # 10 original + 5 new

@pytest.mark.integration
def test_process_purchase_invalid_data(client):
    payload = {
        # missing 'supplier'
        "purchase_id": 12345,
        "date": "2025-07-23",
        "products": []
    }
    response = client.post('/purchase_stock/process_purchase', json=payload)
    data = response.get_json()
    assert response.status_code == 400
    assert data['status'] == 'error'

@pytest.mark.integration
def test_process_purchase_duplicate_purchase_number(client, session, supplier):
    purchase = Purchase(supplier_id=supplier.id, purchase_number=54321, date=date(2025,7,23), total_amount=100)
    session.add(purchase)
    session.commit()

    payload = {
        "supplier": supplier.name,
        "purchase_id": 54321,  # Duplicate purchase number
        "date": "2025-07-23",
        "products": []
    }

    response = client.post('/purchase_stock/process_purchase', json=payload)
    data = response.get_json()
    assert response.status_code == 500
    assert data['status'] == 'error'
    assert "already been registered" in data['message']

@pytest.mark.integration
def test_process_purchase_supplier_not_found(client):
    payload = {
        "supplier": "Nonexistent Supplier",
        "purchase_id": 99999,
        "date": "2025-07-23",
        "products": []
    }
    response = client.post('/purchase_stock/process_purchase', json=payload)
    data = response.get_json()
    assert response.status_code == 500
    assert data['status'] == 'error'
    assert "Supplier not found" in data['message']

@pytest.mark.integration
def test_process_purchase_product_not_found_in_catalog(client, supplier):
    payload = {
        "supplier": supplier.name,
        "purchase_id": 12346,
        "date": "2025-07-23",
        "products": [
            {"product": "Unknown Product", "quantity": 5, "cost": 10.5}
        ]
    }
    response = client.post('/purchase_stock/process_purchase', json=payload)
    data = response.get_json()
    # Should succeed but skip unknown product
    assert response.status_code == 200
    assert data['status'] == 'success'

@pytest.mark.integration
def test_process_purchase_product_no_inventory(client, session, supplier):
    p = Product(name="Product No Inventory", product_typed=1, brand_name="MarcaX")
    session.add(p)
    session.commit()

    payload = {
        "supplier": supplier.name,
        "purchase_id": 12347,
        "date": "2025-07-23",
        "products": [
            {"product": p.name, "quantity": 5, "cost": 10.5}
        ]
    }
    response = client.post('/purchase_stock/process_purchase', json=payload)
    data = response.get_json()
    # Should succeed but skip due to no inventory record
    assert response.status_code == 200
    assert data['status'] == 'success'

@pytest.mark.integration
def test_autocomplete_suppliers(client, supplier):
    response = client.get('/purchase_stock/autocomplete_suppliers?term=Test')
    data = response.get_json()
    assert response.status_code == 200
    assert supplier.name in data

@pytest.mark.integration
def test_autocomplete_suppliers_no_term(client, supplier):
    response = client.get('/purchase_stock/autocomplete_suppliers')
    data = response.get_json()
    assert response.status_code == 200
    assert supplier.name in data
