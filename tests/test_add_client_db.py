# tests/test_save_client.py

import pytest
from database.models import Client

@pytest.mark.integration
def test_add_new_clients_page(client):
    response = client.get('/new_clients/add_new_clients')
    assert response.status_code == 200
    assert b"Add Clients" in response.data  # Cambiar según contenido real de add_new_clients.html

@pytest.mark.integration
def test_save_client_endpoint(client, session):
    response = client.post('/new_clients/save_client', json={
        "client_name": "ana",
        "legal_name": "ana s.a.",
        "tax_id": "A123456789",
        "address": "calle 1",
        "phone": "555555"
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data['status'] == 'success'

    # También podrías verificar que el cliente quedó realmente guardado
    client_in_db = session.query(Client).filter_by(id=data['client_id']).first()
    assert client_in_db is not None
    assert client_in_db.client_name == "ANA"  # porque conviertes a mayúsculas en el endpoint

