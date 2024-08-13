# routes/manejar_credito.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

registrar_abono_bp = Blueprint('registrar_abono', __name__)

@registrar_abono_bp.route('/template_abonos')
def template_abonos():
    return render_template('/clientes/registrar_abono.html')

@registrar_abono_bp.route('/registrar_abono', methods=['POST'])
def registrar_abono():
    cliente = request.form.get('cliente')
    monto = float(request.form.get('monto'))
    fecha = request.form.get('fecha')

    conn = get_db()
    cursor = conn.cursor()

    # Obtener el ID del cliente
    cursor.execute('SELECT id FROM Clientes WHERE nombre_cliente = ?', (cliente,))
    cliente_id = cursor.fetchone()['id']

    if cliente_id is None:
        return jsonify({'success': False, 'message': 'Cliente no encontrado'})


    # Registrar el abono en la tabla Abonos
    cursor.execute('INSERT INTO Abonos (cliente_id, monto, fecha) VALUES (?, ?, ?)', 
                   (cliente_id, monto, fecha))
    
        # Actualizar la deuda del cliente en la tabla Deudas
    cursor.execute('''
        UPDATE Deudas 
        SET total_deuda = total_deuda - ?
        WHERE cliente_id = ?
    ''', (monto, cliente_id))

    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Abono registrado correctamente'})

