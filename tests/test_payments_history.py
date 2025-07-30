
import pytest
from datetime import date
from database import db
from database.models import Client, Payment, Debt, Sale

@pytest.mark.integration
def test_payment_history_page(client, app):
    # Arrange: crear un cliente y un pago
    with app.app_context():
        test_client = Client(client_name="Test Client")
        db.session.add(test_client)
        db.session.commit()

        payment = Payment(client_id=test_client.id, amount=100.0, date=date.today())
        db.session.add(payment)
        db.session.commit()

    # Act: hacer GET a /payment_history
    response = client.get('/payments_history/payment_history')

    # Assert
    assert response.status_code == 200
    assert b'Test Client' in response.data
    assert b'100.0' in response.data

@pytest.mark.integration
def test_delete_payment_and_reverse_debt(client, app):
    with app.app_context():
        # Crear cliente
        test_client = Client(client_name="Client X")
        db.session.add(test_client)
        db.session.commit()

        # Crear venta con total_amount
        sale_obj = Sale(total_amount=300.0, client_id=test_client.id)
        db.session.add(sale_obj)
        db.session.commit()

        # Crear deuda asociada a la venta, sin total_amount aquí
        debt = Debt(
            client_id=test_client.id,
            paid_amount=100.0,
            status="partial",
            sale_id=sale_obj.id
        )
        db.session.add(debt)
        db.session.commit()

        # Crear pago
        payment = Payment(client_id=test_client.id, amount=100.0, date=date.today())
        db.session.add(payment)
        db.session.commit()

        debt_id = debt.id
        payment_id = payment.id

    # Ejecutar la acción: eliminar pago
    response = client.post(f'/payments_history/delete_payment/{payment_id}')

    # Assert de la respuesta
    assert response.status_code == 200

    with app.app_context():
        # Verificar que el pago fue eliminado
        deleted_payment = db.session.get(Payment, payment_id)
        assert deleted_payment is None

        # Verificar que la deuda fue revertida
        updated_debt = db.session.get(Debt, debt_id)
        assert updated_debt.paid_amount == 0.0
        assert updated_debt.status == "pending"

