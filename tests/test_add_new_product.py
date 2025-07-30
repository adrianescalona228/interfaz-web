import pytest

@pytest.mark.integration
def test_add_new_product_page(client):
    response = client.get('/new_product/add_product')
    assert response.status_code == 200
    assert b'Add New Product' in response.data  # Asumiendo que el título o texto contenga esto
