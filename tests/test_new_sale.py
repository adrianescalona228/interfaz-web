
# tests/test_new_sale.py

import pytest
from datetime import date, timedelta
from database.models import (
    Client, Product, Inventory,
    Sale, SaleItem, Debt
)

@pytest.fixture
def client_and_inventory(session):
    # Crear un cliente y un producto con inventario
    client = Client(
        client_name="Alice",
        legal_name="Alice Inc",
        tax_id="T123",
        address="Addr",
        phone="555"
    )
    product = Product(
        name="Widget",
        product_typed=1,
        brand_name="MarcaX",
        price=2.5,
        cost=1.5
    )
    session.add_all([client, product])
    session.flush()

    inv = Inventory(
        product_id=product.id,
        quantity=10.0
    )
    session.add(inv)
    session.commit()

    return client, product, inv

@pytest.mark.integration
def test_render_new_sale_form(client):
    resp = client.get('/new_sale/new_sale')
    assert resp.status_code == 200
    assert b"<form" in resp.data.lower()

@pytest.mark.integration
def test_process_sale_missing_products(client):
    resp = client.post('/new_sale/process_sale', json={
        "client": "Alice",
        "sale_number": 1,
        "date": "2025-01-01",
        "products": [],
        "total_amount": 0
    })
    assert resp.status_code == 400
    assert resp.get_json()['error'] == 'No products provided'

@pytest.mark.integration
def test_process_sale_invalid_date(client):
    resp = client.post('/new_sale/process_sale', json={
        "client": "Alice",
        "sale_number": 1,
        "date": "bad-date",
        "products": [{"product":"Widget","quantity":1,"price":2.5}],
        "total_amount": 2.5
    })
    assert resp.status_code == 400
    assert 'Invalid date' in resp.get_json()['error']

@pytest.mark.integration
def test_process_sale_client_not_found(client_and_inventory, client):
    _, product, _ = client_and_inventory
    resp = client.post('/new_sale/process_sale', json={
        "client": "Nonexistent",
        "sale_number": 1,
        "date": "2025-01-01",
        "products":[{"product":product.name,"quantity":1,"price":2.5}],
        "total_amount":2.5
    })
    assert resp.status_code == 400
    assert 'Client not found' in resp.get_json()['error']

@pytest.mark.integration
def test_process_sale_duplicate_sale_number(client_and_inventory, session, client):
    client_obj, product, _ = client_and_inventory
    # insert a Sale with sale_number=1
    sale = Sale(
        client_id=client_obj.id,
        issue_date=date.today(),
        due_date=date.today()+timedelta(days=15),
        sale_number=1  # if your model uses purchase_number field, adjust accordingly
    )
    session.add(sale)
    session.commit()

    resp = client.post('/new_sale/process_sale', json={
        "client": client_obj.client_name,
        "sale_number": 1,
        "date": date.today().strftime("%Y-%m-%d"),
        "products":[{"product":product.name,"quantity":1,"price":2.5}],
        "total_amount":2.5
    })
    assert resp.status_code == 400
    assert 'already exists' in resp.get_json()['error']

@pytest.mark.integration
def test_process_sale_product_not_in_inventory(client_and_inventory, client):
    client_obj, _, _ = client_and_inventory
    resp = client.post('/new_sale/process_sale', json={
        "client": client_obj.client_name,
        "sale_number": 2,
        "date": date.today().strftime("%Y-%m-%d"),
        "products":[{"product":"Unknown","quantity":1,"price":2.5}],
        "total_amount":2.5
    })
    assert resp.status_code == 400
    assert 'not in inventory' in resp.get_json()['error']

@pytest.mark.integration
def test_process_sale_insufficient_stock(client_and_inventory, client):
    client_obj, product, inv = client_and_inventory
    resp = client.post('/new_sale/process_sale', json={
        "client": client_obj.client_name,
        "sale_number": 3,
        "date": date.today().strftime("%Y-%m-%d"),
        "products":[{"product":product.name,"quantity":inv.quantity+1,"price":2.5}],
        "total_amount":(inv.quantity+1)*2.5
    })
    assert resp.status_code == 400
    assert 'Insufficient stock' in resp.get_json()['error']

@pytest.mark.integration
def test_process_sale_success(client_and_inventory, session, client):
    client_obj, product, inv = client_and_inventory
    qty = 3
    price = 2.5
    total = qty * price

    # Guarda la cantidad antes del POST
    initial_quantity = inv.quantity

    resp = client.post('/new_sale/process_sale', json={
        "client": client_obj.client_name,
        "sale_number": 4,
        "date": date.today().strftime("%Y-%m-%d"),
        "products":[{"product":product.name, "quantity":qty, "price":price}],
        "total_amount": total
    })

    j = resp.get_json()
    assert resp.status_code == 200
    assert 'processed successfully' in j['message']

    # Refresca desde la base
    updated = session.get(Inventory, inv.id)
    assert updated is not None
    assert updated.quantity == pytest.approx(initial_quantity - qty)

@pytest.mark.integration
def test_autocomplete_clients(session, client):
    for name in ["Ann", "Andy", "Bob"]:
        session.add(Client(client_name=name))
    session.commit()

    resp = client.get('/new_sale/autocomplete_clients?term=An')
    data = resp.get_json()
    assert "Ann" in data and "Andy" in data and "Bob" not in data

@pytest.mark.integration
def test_autocomplete_products(client_and_inventory, client):
    _, product, inv = client_and_inventory
    resp = client.get(f'/new_sale/autocomplete_products?term={product.name[:2]}')
    data = resp.get_json()
    assert any(d['label']==product.name for d in data)
    assert data[0]['quantity'] == inv.quantity

@pytest.mark.integration
def test_last_and_verify_sale_number(session, client):
    # no sales yet
    r1 = client.get('/new_sale/last_sale_number').get_json()
    assert r1['last_number'] == 1

    # insert sale #10
    s = Sale(
        client_id=None,
        issue_date=date.today(),
        due_date=date.today(),
        sale_number=10  # adjust field name if needed
    )
    session.add(s); session.commit()

    r2 = client.get('/new_sale/last_sale_number').get_json()
    assert r2['last_number'] == 11

    v1 = client.post('/new_sale/verify_sale_number', json={'sale_number':10}).get_json()
    assert v1['exists'] is True
    v2 = client.post('/new_sale/verify_sale_number', json={'sale_number':999}).get_json()
    assert v2['exists'] is False
