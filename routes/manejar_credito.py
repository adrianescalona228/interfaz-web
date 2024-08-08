# routes/manejar_credito.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from .database import get_db


manejar_credito_bp = Blueprint('manejar_credito', __name__)

@manejar_credito_bp.route('/manejar_credito')
def manejar_credito():
    return render_template('manejar_credito.html')

@manejar_credito_bp.route('/registrar_abono', methods=['POST'])
def registrar_abono():
    cliente = request.form.get('cliente')
    monto = float(request.form.get('monto'))
    fecha = request.form.get('fecha')

    conn = get_db()
    cursor = conn.cursor()

    # Actualizar o insertar la deuda del cliente
    cursor.execute('''
        INSERT INTO Deudas (cliente, total_deuda, fecha_actualizacion)
        VALUES (?, ?, ?)
        ON CONFLICT(cliente) DO UPDATE SET
            total_deuda = total_deuda - ?,
            fecha_actualizacion = ?
    ''', (cliente, monto, fecha, monto, fecha))

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Abono registrado correctamente'})

# Ruta para obtener datos de autocompletado de clientes
@manejar_credito_bp.route('/autocompletar_clientes', methods=['GET'])
def autocompletar_clientes():
    term = request.args.get('term', '')
    
    # Conexión a la base de datos y consulta
    db = get_db()
    cursor = db.execute('SELECT nombre_cliente FROM Clientes WHERE nombre_cliente LIKE ?', ('%' + term + '%',))
    clientes = [row['nombre_cliente'] for row in cursor.fetchall()]
    
    return jsonify(clientes)

@manejar_credito_bp.route('/manejar_credito/deudas')
def deudas():
    return render_template('deudas.html')

