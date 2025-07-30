# routes/clients/clients_list.py
from flask import Blueprint, render_template, request, jsonify
from database import db
from database.models import Client
import logging

clients_list_bp = Blueprint('clients_list', __name__)

@clients_list_bp.route('/clients')
def clients():
    clients = db.session.execute(db.select(Client)).scalars().all()
    print("prueba Clients from DB:", clients)  # o logging.info(...)
    return render_template('clients/clients_list.html', clients=clients)


@clients_list_bp.route('/update_client', methods=['POST'])
def update_client():
    data = request.json
    client_id = data.get('id')
    column = data.get('column')
    value = data.get('value')

    column_map = {
        'name': 'client_name',
        'legal_name': 'legal_name',
        'tax_id': 'tax_id',
        'address': 'address',
        'phone': 'phone'
    }

    column_db = column_map.get(column)
    if column_db is None:
        return jsonify({'success': False, 'message': 'Invalid column'}), 400

    try:
        
        client = db.session.get(Client, client_id)

        if not client:
            return jsonify({'success': False, 'message': 'Client not found'}), 404

        # Update the attribute dynamically
        setattr(client, column_db, value)
        db.session.commit()
        
        logging.info(f'Client with ID {client_id} updated. Column: {column_db.upper()}, New value: {value}')
        return jsonify({'success': True, 'message': 'Client updated successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logging.error(f'Error updating client. ID: {client_id}, Column: {column_db.upper()}, Value: {value} - Error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Error updating client'}), 500
