
import pytest
from database.models import Product, Inventory

@pytest.mark.integration
def test_save_product_success(client, session):
    payload = {
        "product": "Fanta Naranja",
        "price": 150.0,
        "cost": 100.0,
        "product_type": 1,
        "brand_name": "MarcaX"
    }

    response = client.post("/register_new_product/save_product", json=payload)
    assert response.status_code == 201

    data = response.get_json()
    assert data["success"] is True
    assert "saved successfully" in data["message"].lower()

    # Confirm product created
    product = session.query(Product).filter_by(name="FANTA NARANJA").first()
    assert product is not None
    assert product.product_typed == 1
    assert product.brand_name == "MarcaX"

    # Confirm inventory created
    inventory = session.query(Inventory).filter_by(product_id=product.id).first()
    assert inventory is not None
    assert inventory.quantity == 0
    assert inventory.product.price == 150.0
    assert inventory.product.cost == 100.0


@pytest.mark.integration
def test_save_product_missing_fields(client):
    payload = {
        "product": "",  # invalid name
        "price": 150.0,
        "cost": 100.0,
        "product_type": 1,
        "brand_name": "MarcaX"
    }

    response = client.post("/register_new_product/save_product", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "missing or invalid fields" in data["message"].lower()


@pytest.mark.integration
def test_save_product_invalid_price_cost(client):
    payload = {
        "product": "Fernet Branca",
        "price": 0.0,  # invalid
        "cost": -10.0,  # invalid
        "product_type": 2,
        "brand_name": "MarcaX"
    }

    response = client.post("/register_new_product/save_product", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "missing or invalid fields" in data["message"].lower()


@pytest.mark.integration
def test_save_product_db_exception(client, monkeypatch):
    def raise_exception(*args, **kwargs):
        raise Exception("DB error")

    # Monkeypatch db.session.commit para simular error
    from database import db
    monkeypatch.setattr(db.session, "commit", raise_exception)

    payload = {
        "product": "Sprite",
        "price": 100.0,
        "cost": 70.0,
        "product_type": 3,
        "brand_name": "MarcaX"
    }

    response = client.post("/register_new_product/save_product", json=payload)
    assert response.status_code == 500
    data = response.get_json()
    assert data["success"] is False
    assert "error saving product" in data["message"].lower()
