# tests/test_add_payment.py

import pytest
from database.models import Client, Sale, Debt, Payment
from datetime import date

@pytest.mark.integration
def test_payment_template_page(client):
    response = client.get('/payments/payment_template')
    assert response.status_code == 200
    assert b"Credit Management" in response.data

@pytest.mark.integration
def test_add_payment_integration(session, client):
    # Crear cliente
    client_obj = Client(
        client_name="testclient",
        legal_name="Test Client S.A.",
        tax_id="T123",
        address="test addr",
        phone="000"
    )
    session.add(client_obj)
    session.commit()

    # Crear venta asociada
    sale_obj = Sale(
        client_id=client_obj.id,
        total_amount=300.0,
        issue_date=date(2025, 1, 1),
        due_date=date(2025, 2, 1)
    )
    session.add(sale_obj)
    session.commit()

    # Crear deuda asociada
    debt_obj = Debt(
        sale_id=sale_obj.id,
        client_id=client_obj.id,
        paid_amount=0.0,
        status="pending"
    )
    session.add(debt_obj)
    session.commit()

    # Hacer POST
    response = client.post('/payments/add_payment', json={
        "client": "testclient",
        "amount": 150,
        "date": "2025-07-22",
    })

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True

    # Validar que el pago se guardó
    payment = session.query(Payment).filter_by(client_id=client_obj.id, amount=150).first()
    assert payment is not None

    # Validar que la deuda se actualizó
    updated_debt = session.query(Debt).filter_by(client_id=client_obj.id).first()
    assert updated_debt.paid_amount == 150
    assert updated_debt.sale.total_amount == 300
    assert updated_debt.status == "partial"
