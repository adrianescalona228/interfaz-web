from flask import Blueprint, render_template, request, jsonify, session
from database.models import Client, Debt, Sale
from database import db
import logging

debts_bp = Blueprint('debts', __name__)

@debts_bp.route('/view_debts')
def view_debts():
    # Agrupar por cliente y calcular el total adeudado (sum(total_amount) - sum(paid_amount))
    results = db.session.query(
        Client.client_name,
        db.func.sum(Sale.total_amount).label('total_ventas'),
        db.func.sum(Debt.paid_amount).label('total_pagado')
    )\
    .join(Debt, Client.id == Debt.client_id)\
    .join(Sale, Sale.id == Debt.sale_id)\
    .group_by(Client.id)\
    .order_by(Client.client_name.asc())\
    .all()

    # Armar lista final con lo que realmente debe cada uno
    debts = []
    for client_name, total_ventas, total_pagado in results:
        monto_deuda = (total_ventas or 0) - (total_pagado or 0)
        if monto_deuda > 0:
            debts.append({
                "client_name": client_name,
                "amount_due": round(monto_deuda, 2)
            })

    return render_template('clients/view_debts.html', debts=debts)

@debts_bp.route('/update_debt', methods=['POST'])
def update_debt():
    data = request.get_json()
    client_name = data.get('name')
    new_value = data.get('value')

    try:
        # Find client by client_name
        client = db.session.query(Client).filter_by(client_name=client_name).first()

        if not client:
            logging.warning(f'Client not found with name {client_name}')
            return jsonify({'success': False, 'message': 'Client not found'}), 404

        # Find debt by client_id
        debt = db.session.query(Debt).filter_by(client_id=client.id).first()

        if not debt:
            logging.warning(f'Debt not found for client ID {client.id}')
            return jsonify({'success': False, 'message': 'Debt not found for client'}), 404

        if not debt.sale:
            logging.warning(f'Sale not found for debt ID {debt.id}')
            return jsonify({'success': False, 'message': 'No sale associated with debt'}), 404

        # Store original total_amount from the sale
        session['original_value'] = debt.sale.total_amount
        session['client_id'] = client.id

        # ✅ Update the sale's total_amount instead
        debt.sale.total_amount = new_value
        db.session.commit()

        logging.info(f'Debt updated: Client ID {client.id}. Original value: {session["original_value"]}. New value: {new_value}.')
        return jsonify({'success': True, 'message': 'Debt updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f'Error updating debt: {str(e)}')
        return jsonify({'success': False, 'message': 'Error updating debt'}), 500

@debts_bp.route('/rollback_debt', methods=['POST'])
def rollback_debt():
    try:
        original_value = session.get('original_value')
        client_id = session.get('client_id')

        if original_value is None or client_id is None:
            logging.warning('No changes to rollback. Original value or client ID not found in session.')
            return jsonify({'success': False, 'message': 'No changes to rollback'}), 400

        # Find debt by client_id
        debt = db.session.query(Debt).filter_by(client_id=client_id).first()

        if not debt:
            logging.warning(f'Debt not found for client ID {client_id} during rollback')
            return jsonify({'success': False, 'message': 'Debt not found for client'}), 404

        # Rollback to original value
        debt.total_amount = original_value
        db.session.commit()

        logging.info(f'Rollback performed: Client ID {client_id}. Value reverted to: {original_value}.')
        return jsonify({'success': True, 'message': 'Rollback successful'}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f'Error performing rollback: {str(e)}')
        return jsonify({'success': False, 'message': 'Error performing rollback'}), 500
