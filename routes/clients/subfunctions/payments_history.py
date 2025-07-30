# routes/payments/history.py

from flask import Blueprint, render_template, flash, request
from database import db
from database.models import Payment, Client, Debt
from sqlalchemy.exc import SQLAlchemyError
import logging

payment_history_bp = Blueprint('payment_history', __name__)

@payment_history_bp.route('/payment_history')
def payment_history():
    payments = db.session.query(
        Payment.id,
        Client.client_name,
        Payment.amount,
        Payment.date
    ).join(Client).all()

    return render_template('clients/payment_history.html', payments=payments)

@payment_history_bp.route('/delete_payment/<int:payment_id>', methods=['POST'])
def delete_payment(payment_id):
    try:
        payment = db.session.get(Payment, payment_id)
        if not payment:
            flash('Payment not found.', 'error')
            return '', 404

        logging.info(f'Deleting payment ID {payment_id}: {payment.amount} from client ID {payment.client_id}')

        reverse_payment_from_debts(payment.client_id, payment.amount)

        db.session.delete(payment)
        db.session.commit()

        flash('Payment deleted and debts updated successfully.', 'success')
        return '', 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f'Error deleting payment: {e}', exc_info=True)
        flash(f'Error processing the request: {e}', 'error')
        return '', 500

def reverse_payment_from_debts(client_id, amount_to_reverse):
    debts = db.session.query(Debt).filter(
        Debt.client_id == client_id,
        (Debt.status == 'paid') | (Debt.paid_amount > 0)
    ).order_by(Debt.id.desc()).all()

    for debt in debts:
        if amount_to_reverse <= 0:
            break

        if amount_to_reverse >= debt.paid_amount:
            amount_to_reverse -= debt.paid_amount
            debt.paid_amount = 0
            debt.status = 'pending'
        else:
            debt.paid_amount -= amount_to_reverse
            debt.status = 'pending'
            amount_to_reverse = 0

        logging.info(f"Debt ID {debt.id} updated: paid_amount={debt.paid_amount}, status={debt.status}")

    if amount_to_reverse > 0:
        logging.warning(f'Remaining unapplied amount: {amount_to_reverse}')
