#routes/compras/compras.py
from flask import Blueprint, render_template
from routes.clients.subfunctions.add_new_client import new_clients_bp
from routes.clients.subfunctions.clients_list import clients_list_bp
from routes.clients.subfunctions.add_payment import payments_bp
from routes.clients.subfunctions.debts import debts_bp
from routes.clients.subfunctions.payments_history import payment_history_bp

clients_bp = Blueprint('clients', __name__)
clients_bp.register_blueprint(new_clients_bp, url_prefix='/new_clients')
clients_bp.register_blueprint(clients_list_bp, url_prefix='/clients_list')
clients_bp.register_blueprint(payments_bp, url_prefix='/payments')
clients_bp.register_blueprint(debts_bp, url_prefix='/debts')
clients_bp.register_blueprint(payment_history_bp, url_prefix='/payments_history')

@clients_bp.route('/clients')
def clients():
    return render_template('/clients/clients.html')
