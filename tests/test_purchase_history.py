
import pytest
from database.models import Supplier, Product, Inventory, Purchase, PurchaseItem
from datetime import date

@pytest.fixture
def full_purchase(session):
    supplier = Supplier(name="Supplier For History")
    product = Product(
        name="History Product",
        product_typed=1,
        brand_name="MarcaX",
        price=5.0,
        cost=3.0
    )
    session.add_all([supplier, product])
    session.flush()

    inventory = Inventory(product_id=product.id, quantity=10)

    purchase = Purchase(
        supplier_id=supplier.id,
        purchase_number=11111,
        date=date.today(),
        total_amount=15.0
    )
    session.add_all([inventory, purchase])
    session.flush()

    item = PurchaseItem(
        purchase_id=purchase.id,
        product_id=product.id,
        quantity=5,
        cost=3.0
    )
    session.add(item)
    session.commit()

    return {
        "supplier": supplier,
        "product": product,
        "inventory": inventory,
        "purchase": purchase,
        "item": item
    }

@pytest.mark.integration
def test_purchase_history_page(client, full_purchase):
    response = client.get('/purchase_history/purchase_history')
    assert response.status_code == 200
    assert b"History Product" in response.data
    assert b"Supplier For History" in response.data

@pytest.mark.integration
def test_delete_purchase_success(client, session, full_purchase):
    purchase_number = full_purchase["purchase"].purchase_number
    response = client.post(f'/purchase_history/delete_purchase/{purchase_number}')
    assert response.status_code == 200

    # Ensure purchase and item are deleted
    assert session.query(Purchase).filter_by(purchase_number=purchase_number).first() is None
    assert session.query(PurchaseItem).filter_by(purchase_id=full_purchase["purchase"].id).first() is None

    # Ensure inventory adjusted
    inventory = session.query(Inventory).filter_by(product_id=full_purchase["product"].id).first()
    assert inventory.quantity == 5  # original 10 - 5 from deleted item

@pytest.mark.integration
def test_delete_purchase_not_found(client):
    response = client.post('/purchase_history/delete_purchase/999999')
    assert response.status_code == 404

@pytest.mark.integration
def test_delete_product_from_purchase_success(client, session, full_purchase):
    purchase = full_purchase["purchase"]
    product = full_purchase["product"]
    inventory_before = full_purchase["inventory"].quantity

    response = client.post(f'/purchase_history/delete_product/{purchase.id}/{product.id}')
    assert response.status_code == 200

    # Check item is deleted
    item = session.query(PurchaseItem).filter_by(purchase_id=purchase.id, product_id=product.id).first()
    assert item is None

    # Check inventory updated
    inventory = session.query(Inventory).filter_by(product_id=product.id).first()
    assert inventory.quantity == inventory_before - full_purchase["item"].quantity

    # Check purchase total updated
    updated_purchase = session.get(Purchase, purchase.id)
    assert updated_purchase.total_amount == 0.0

@pytest.mark.integration
def test_delete_product_not_found(client, full_purchase):
    fake_product_id = 9999
    purchase = full_purchase["purchase"]

    response = client.post(f'/purchase_history/delete_product/{purchase.id}/{fake_product_id}')
    assert response.status_code == 404
