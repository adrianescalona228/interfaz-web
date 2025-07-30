
import pytest
from database.models import Client, Product, Inventory, Sale, SaleItem, Debt
from datetime import date

@pytest.mark.integration
def test_sales_history(client, session):
    response = client.get("/sales_history/sales_history")
    assert response.status_code == 200
    assert b"Sales History" in response.data

@pytest.mark.integration
def test_delete_sale_endpoint(client, session):
    # Setup: crear cliente, producto, inventario, venta, sale_items y deuda
    client_obj = Client(client_name="Test Client")
    product = Product(name="Test Product", price=10.0)
    inventory = Inventory(product=product, quantity=100)

    sale = Sale(
        sale_number=1,
        client=client_obj,
        issue_date=date.today(),
        due_date=date.today(),
        total_amount=50.0  # <-- total_amount ahora va en Sale
    )

    sale_item = SaleItem(sale=sale, product=product, quantity=5, price_unit=10.0)

    debt = Debt(
        sale=sale,
        paid_amount=20.0,
        status="pending"  # o el estado que corresponda
    )

    session.add_all([client_obj, product, inventory, sale, sale_item, debt])
    session.commit()

    # Confirmar inventario antes
    assert inventory.quantity == 100

    # Ejecutar el POST para borrar la venta
    response = client.post(f"/sales_history/delete_sale/{sale.sale_number}")
    assert response.status_code == 200

    # Verificar que la venta ya no existe
    assert session.get(Sale, sale.id) is None

    # Verificar que el sale_item se eliminó
    sale_item_from_db = session.query(SaleItem).filter_by(sale_id=sale.id).first()
    assert sale_item_from_db is None

    # Verificar que la deuda se eliminó
    debt_from_db = session.query(Debt).filter_by(sale_id=sale.id).first()
    assert debt_from_db is None

    # Verificar que el inventario se actualizó correctamente
    updated_inventory = session.query(Inventory).filter_by(product_id=product.id).first()
    assert updated_inventory.quantity == 105  # 100 + 5 vendidos

    # Confirmar que el cliente y el producto siguen existiendo
    assert session.get(Client, client_obj.id) is not None
    assert session.get(Product, product.id) is not None

@pytest.mark.integration
def test_remove_product_from_sale(client, session):
    # Setup: crear cliente, producto, inventario, venta, sale_items y deuda
    client_obj = Client(client_name="Test Client")
    product1 = Product(name="Test Product 1")
    product2 = Product(name="Test Product 2")
    inventory1 = Inventory(product=product1, quantity=50)
    inventory2 = Inventory(product=product2, quantity=30)

    sale = Sale(
        sale_number=1,
        client=client_obj,
        issue_date=date.today(),
        due_date=date.today(),
        total_amount=150.0
    )

    sale_item1 = SaleItem(sale=sale, product=product1, quantity=5, price_unit=10.0)  # total 50
    sale_item2 = SaleItem(sale=sale, product=product2, quantity=10, price_unit=10.0) # total 100
    debt = Debt(sale=sale, paid_amount=50.0, status="pending")


    session.add_all([client_obj, product1, product2, inventory1, inventory2, sale, sale_item1, sale_item2, debt])
    session.commit()

    # Confirm initial inventory quantities
    assert inventory1.quantity == 50
    assert inventory2.quantity == 30

    # Call endpoint to remove sale_item1 from sale 1
    response = client.post(f"/sales_history/remove_product/{sale.sale_number}/{sale_item1.id}")
    assert response.status_code == 200

    # Refresh from DB
    updated_inventory1 = session.get(Inventory, inventory1.id)
    updated_inventory2 = session.get(Inventory, inventory2.id)
    updated_sale = session.query(Sale).filter_by(sale_number=sale.sale_number).first()
    deleted_sale_item = session.get(SaleItem, sale_item1.id)

    # SaleItem should be deleted
    assert deleted_sale_item is None

    # Inventory for product1 should increase by quantity of deleted item
    assert updated_inventory1.quantity == 55  # 50 + 5 returned

    # Inventory for product2 remains the same
    assert updated_inventory2.quantity == 30

    # Debt total_amount should also decrease accordingly
    assert updated_sale.total_amount == 100.0

    # SaleItem2 should still exist
    remaining_item = session.get(SaleItem, sale_item2.id)
    assert remaining_item is not None

@pytest.mark.integration
def test_remove_last_product_removes_sale_and_debt(client, session):
    # Setup a sale with only one product
    client_obj = Client(client_name="Solo Client")
    product = Product(name="Solo Product")
    inventory = Inventory(product=product, quantity=20)

    sale = Sale(
        sale_number=2,
        client=client_obj,
        issue_date=date.today(),
        due_date=date.today(),
        total_amount=100.0  # Total amount in Sale, not in Debt
    )

    sale_item = SaleItem(sale=sale, product=product, quantity=10, price_unit=10.0)
    debt = Debt(sale=sale, paid_amount=0.0)  # No total_amount here

    session.add_all([client_obj, product, inventory, sale, sale_item, debt])
    session.commit()

    # Confirm initial inventory quantity
    assert inventory.quantity == 20

    # Call endpoint or logic to remove the last product (you'll have this implemented)
    response = client.post(f"/sales_history/remove_product/{sale.sale_number}/{sale_item.id}")
    assert response.status_code == 200

    # After removing last product, the sale and debt should be deleted
    assert session.get(Sale, sale.id) is None
    assert session.query(Debt).filter_by(sale_id=sale.id).first() is None

    # Inventory should be restored
    updated_inventory = session.get(Inventory, inventory.id)
    assert updated_inventory.quantity == 30  # 20 + 10 returned

@pytest.mark.integration
def test_update_paid_amount_success(client, session):
    # Setup initial data
    client_obj = Client(client_name="Test Client")
    product = Product(name="Test Product", price=10.0)
    inventory = Inventory(product=product, quantity=100)
    sale = Sale(
        sale_number=123,
        client=client_obj,
        issue_date=date.today(),
        due_date=date.today(),
        total_amount=50.0
    )
    sale_item = SaleItem(sale=sale, product=product, quantity=5, price_unit=10.0)
    debt = Debt(sale=sale, paid_amount=10.0, status="pending")

    session.add_all([client_obj, product, inventory, sale, sale_item, debt])
    session.commit()

    # New paid amount to update
    new_paid_amount = 25.5

    # Call the endpoint
    response = client.post("/sales_history/update_paid_amount", json={
        "sale_number": 123,
        "paid_amount": new_paid_amount
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["new_paid_amount"] == new_paid_amount

    # Confirm DB was updated
    updated_debt = session.query(Debt).filter_by(sale_id=sale.id).first()
    assert updated_debt.paid_amount == new_paid_amount


@pytest.mark.integration
def test_update_paid_amount_sale_not_found(client):
    response = client.post("/sales_history/update_paid_amount", json={
        "sale_number": 9999,
        "paid_amount": 10.0
    })

    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert "not found" in data["message"].lower()


@pytest.mark.integration
@pytest.mark.parametrize("payload", [
    {"sale_number": None, "paid_amount": 10},
    {"sale_number": "abc", "paid_amount": 10},
    {"sale_number": 123, "paid_amount": "not-a-number"},
    {"paid_amount": 10},  # missing sale_number
    {"sale_number": 123}, # missing paid_amount
])
def test_update_paid_amount_invalid_payload(client, payload):
    response = client.post("/sales_history/update_paid_amount", json=payload)

    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "invalid" in data["message"].lower()
