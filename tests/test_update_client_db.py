
# tests/test_client_list.py
import pytest
from database.models import Client

@pytest.mark.integration
def test_get_clients_page(client, session):
    # Crear cliente para tener datos
    client_obj = Client(client_name="john", legal_name="John Inc", tax_id="J123", address="123 St", phone="123456")
    session.add(client_obj)
    session.commit()

    response = client.get('/clients_list/clients')
    assert response.status_code == 200
    assert b"john" in response.data.lower()  # Asumiendo que aparece el nombre en el HTML


@pytest.mark.integration
def test_update_client_endpoint(client, session):
    # Crear cliente inicial
    client_obj = Client(client_name="jane", legal_name="Jane LLC", tax_id="J456", address="456 Ave", phone="654321")
    session.add(client_obj)
    session.commit()

    new_phone = "999999999"

    response = client.post('/clients_list/update_client', json={
        "id": client_obj.id,
        "column": "phone",
        "value": new_phone
    })

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success'] is True

    # Refrescar el objeto en la sesión para verificar el cambio
    session.refresh(client_obj)
    assert client_obj.phone == new_phone
