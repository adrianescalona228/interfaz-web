from flask import Blueprint, render_template, request, jsonify
from database import db
from database.models import Client, Payment, Debt
import logging
from datetime import datetime


payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/payment_template')
def payment_template():
    return render_template('clients/add_payment.html')

@payments_bp.route('/add_payment', methods=['POST'])
def add_payment():
    data = request.get_json()
    client_name = data.get('client').lower()
    amount = float(data.get('amount'))
    payment_date_str = data.get('date')
    # Convertir string a date
    payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()

    try:
        result = db.session.execute(
            db.select(Client).filter_by(client_name=client_name)
        )
        client = result.scalars().first()
        if not client:
            return jsonify({'success': False, 'message': 'Client not found'}), 404

        # Create payment record
        payment = Payment(client_id=client.id, amount=amount, date=payment_date)
        db.session.add(payment)

        # Get all pending debts ordered by id (or by sale.due_date if you want)
        
        result = db.session.execute(
            db.select(Debt)
            .filter_by(client_id=client.id, status='pending')
            .order_by(Debt.id)
        )
        debts = result.scalars().all()

        remaining_amount = amount

        for debt in debts:
            debt_remaining = debt.sale.total_amount - (debt.paid_amount or 0)

            if remaining_amount >= debt_remaining:
                # Full payment for this debt
                debt.paid_amount = debt.sale.total_amount
                debt.status = 'paid'
                remaining_amount -= debt_remaining
            else:
                # Partial payment
                debt.paid_amount = (debt.paid_amount or 0) + remaining_amount
                debt.status = 'partial'
                remaining_amount = 0
                break

        db.session.commit()
        return jsonify({'success': True, 'payment_id': payment.id})

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error adding payment: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
