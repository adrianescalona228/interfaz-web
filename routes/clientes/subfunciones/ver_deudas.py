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
from flask import session

@deudas_bp.route('/actualizar_deuda', methods=['POST'])
def actualizar_deuda():
    data = request.json
    nombre = data.get('nombre')
    valor = data.get('value')

    try:
        db = get_db()
        cursor = db.cursor()

        # Obtener el ID del cliente
        cursor.execute('SELECT id FROM Clientes WHERE nombre_cliente = ?', (nombre,))
        id = cursor.fetchone()['id']

        # Obtener el valor actual de la deuda antes de actualizar
        cursor.execute('SELECT monto_total FROM Deudas WHERE cliente_id = ?', (id,))
        valor_original = cursor.fetchone()['monto_total']

        # Almacenar el valor original en la sesión para el rollback
        session['valor_original'] = valor_original
        session['cliente_id'] = id

        # Actualizar la deuda
        cursor.execute('''
            UPDATE Deudas
            SET monto_total = ?
            WHERE cliente_id = ?
        ''', (valor, id))
        db.commit()

        return jsonify({'success': True, 'message': 'Deuda actualizada exitosamente'}), 200

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'success': False, 'message': 'Error al actualizar la deuda'}), 500

@deudas_bp.route('/rollback_deuda', methods=['POST'])
def rollback_deuda():
    try:
        db = get_db()
        cursor = db.cursor()

        # Recuperar el valor original y el ID del cliente desde la sesión
        valor_original = session.get('valor_original')
        id = session.get('cliente_id')

        if valor_original is not None and id is not None:
            # Revertir la deuda al valor original
            cursor.execute('''
                UPDATE Deudas
                SET monto_total = ?
                WHERE cliente_id = ?
            ''', (valor_original, id))
            db.commit()

            return jsonify({'success': True, 'message': 'Rollback exitoso'}), 200
        else:
            return jsonify({'success': False, 'message': 'No hay cambios para deshacer'}), 400

    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'success': False, 'message': 'Error al realizar el rollback'}), 500
