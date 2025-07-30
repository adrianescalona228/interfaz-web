import pytest
from database.models import Product, Inventory

@pytest.fixture
def inventory_item(session):
    # Crear un producto con price y cost
    product = Product(name="Test Product", product_typed=1, brand_name="MarcaX", price=10.0, cost=7.0)
    session.add(product)
    session.flush()  # para que product.id esté disponible

    inventory = Inventory(product_id=product.id, quantity=20)
    session.add(inventory)
    session.commit()

    return inventory

@pytest.mark.integration
def test_view_inventory_page(client, inventory_item):
    response = client.get('/view_inventory/view_inventory')
    assert response.status_code == 200
    assert b'Test Product' in response.data

@pytest.mark.integration
def test_update_inventory_price(client, session, inventory_item):
    inventory_id = inventory_item.id
    new_price = 15.5

    response = client.post('/view_inventory/update_product', json={
        'id': inventory_id,
        'column': 'price',
        'value': new_price
    })

    assert response.status_code == 200
    assert response.json['success'] is True

    updated_inventory = session.get(Inventory, inventory_id)
    assert updated_inventory.price == new_price

@pytest.mark.integration
def test_update_invalid_column(client, inventory_item):
    response = client.post('/view_inventory/update_product', json={
        'id': inventory_item.id,
        'column': 'invalid_column',
        'value': 'something'
    })

    assert response.status_code == 400
    assert response.json['success'] is False
    assert 'Invalid column' in response.json['message']

@pytest.mark.integration
def test_update_nonexistent_product(client):
    response = client.post('/view_inventory/update_product', json={
        'id': 9999,
        'column': 'price',
        'value': 22.0
    })

    assert response.status_code == 404
    assert response.json['success'] is False
    assert 'not found' in response.json['message'].lower()

@pytest.mark.integration
def test_update_quantity_and_validate(client, session, inventory_item):
    new_quantity = 42

    response = client.post('/view_inventory/update_product', json={
        'id': inventory_item.id,
        'column': 'quantity',
        'value': new_quantity
    })

    assert response.status_code == 200
    assert response.json['success'] is True

    updated_inventory = session.get(Inventory, inventory_item.id)
    assert updated_inventory.quantity == new_quantity
