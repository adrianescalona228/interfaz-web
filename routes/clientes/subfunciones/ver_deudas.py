# routes/manejar_credito.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

deudas_bp = Blueprint('deudas', __name__)

@deudas_bp.route('/ver_deudas')
def ver_deudas():
    db = get_db()   
    cursor = db.execute('''SELECT c.nombre_cliente, d.monto_total
                        FROM Clientes c
                        JOIN Deudas d ON c.id = d.cliente_id''')
    deudas = cursor.fetchall()
    return render_template('/clientes/ver_deudas.html', deudas=deudas)
