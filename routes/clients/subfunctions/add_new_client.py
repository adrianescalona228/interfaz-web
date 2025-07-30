from flask import Blueprint, render_template, request, jsonify
from database import db
from database.models import Client, Debt
import logging

new_clients_bp = Blueprint('new_clients', __name__)

@new_clients_bp.route('/add_new_clients')
def add_new_clients():
    return render_template('clients/add_new_clients.html')

@new_clients_bp.route('/save_client', methods=['POST'])
def save_client():
    client_data = {
        "client_name": request.json.get('client_name', '').upper(),
        "legal_name": request.json.get('legal_name', '').upper(),
        "tax_id": request.json.get('tax_id'),
        "address": request.json.get('address', '').upper(),
        "phone": request.json.get('phone'),
    }
    print("Datos JSON recibidos:", request.json)

    try:
        # Create new client instance
        client = Client(**client_data)
        db.session.add(client)
        db.session.commit()  # Assigns client.id here

        return jsonify({"status": "success", "client_id": client.id}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error saving client: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
