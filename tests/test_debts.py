import pytest
from database.models import Client, Debt, Sale

@pytest.mark.integration
def test_view_debts_page(client, session):
    # Crear cliente
    client_obj = Client(client_name='Test Client')
    session.add(client_obj)
    session.commit()

    # Crear venta
    sale_obj = Sale(total_amount=100.0)
    session.add(sale_obj)
    session.commit()

    # Crear deuda asociada a la venta
    debt_obj = Debt(client_id=client_obj.id, paid_amount=0.0, status="pending", sale_id=sale_obj.id)
    session.add(debt_obj)
    session.commit()

    response = client.get('/debts/view_debts')
    assert response.status_code == 200
    assert b'Test Client' in response.data
    assert b'100.0' in response.data

@pytest.mark.integration
def test_update_debt_success(client, session):
    # Crear cliente
    client_obj = Client(client_name='Test Client')
    session.add(client_obj)
    session.commit()

    # Crear venta
    sale_obj = Sale(total_amount=100.0)
    session.add(sale_obj)
    session.commit()

    # Crear deuda asociada
    debt_obj = Debt(client_id=client_obj.id, paid_amount=0.0, status="pending", sale_id=sale_obj.id)
    session.add(debt_obj)
    session.commit()

    # Hacer el POST para actualizar la deuda
    response = client.post('/debts/update_debt', json={
        'name': client_obj.client_name,
        'value': 150.0
    })


    assert response.status_code == 200  # redirección
    session.refresh(debt_obj)

@pytest.mark.integration
def test_update_debt_client_not_found(client):
    response = client.post('/debts/update_debt', json={
        'name': 'Nonexistent Client',
        'value': 200.0
    })

    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert data['success'] is False
    assert 'Client not found' in data['message']

@pytest.mark.integration
def test_rollback_debt_success(client, session):
    # Crear cliente y deuda
    client_obj = Client(client_name='Test Client')
    session.add(client_obj)
    session.commit()

    # Crear venta con total_amount
    sale_obj = Sale(total_amount=100.0)
    session.add(sale_obj)
    session.commit()

    # Crear deuda asociada a la venta
    debt_obj = Debt(client_id=client_obj.id, paid_amount=0.0, status="pending", sale_id=sale_obj.id)
    session.add(debt_obj)
    session.commit()

    # Actualizar deuda y guardar en sesión (simular sesión)
    with client.session_transaction() as sess:
        sess['original_value'] = 100.0
        sess['client_id'] = client_obj.id

    # Actualizar deuda para simular cambio
    debt_obj.total_amount = 150.0
    session.commit()

    # Llamar rollback
    response = client.post('/debts/rollback_debt')

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'Rollback successful' in data['message']

    # Verificar que deuda fue revertida
    reverted_debt = session.query(Debt).filter_by(client_id=client_obj.id).first()
    assert reverted_debt.total_amount == 100.0

@pytest.mark.integration
def test_rollback_debt_no_session_data(client):
    # Sesión vacía, sin datos para rollback
    response = client.post('/debts/rollback_debt')

    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'No changes to rollback' in data['message']
