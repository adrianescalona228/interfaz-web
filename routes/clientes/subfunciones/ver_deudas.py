# routes/manejar_credito.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db
import logging
from flask import session


deudas_bp = Blueprint('deudas', __name__)

@deudas_bp.route('/ver_deudas')
def ver_deudas():
    db = get_db()   
    cursor = db.execute('''SELECT c.nombre_cliente, d.monto_total
                        FROM Clientes c
                        JOIN Deudas d ON c.id = d.cliente_id
                        ORDER BY c.nombre_cliente ASC''')
    deudas = cursor.fetchall()
    return render_template('/clientes/ver_deudas.html', deudas=deudas)

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
        cliente = cursor.fetchone()

        if cliente:
            id = cliente['id']

            # Obtener el valor actual de la deuda antes de actualizar
            cursor.execute('SELECT monto_total FROM Deudas WHERE cliente_id = ?', (id,))
            deuda = cursor.fetchone()

            if deuda:
                valor_original = deuda['monto_total']

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

                logging.info(f'Deuda actualizada: Cliente ID {id}. Valor original: {valor_original}. Nuevo valor: {valor}.')
                return jsonify({'success': True, 'message': 'Deuda actualizada exitosamente'}), 200
            else:
                logging.warning(f'No se encontró deuda para el Cliente ID {id}.')
                return jsonify({'success': False, 'message': 'Deuda no encontrada para el cliente'}), 404
        else:
            logging.warning(f'No se encontró cliente con nombre {nombre}.')
            return jsonify({'success': False, 'message': 'Cliente no encontrado'}), 404

    except Exception as e:
        logging.error(f'Error al actualizar la deuda: {str(e)}')
        return jsonify({'success': False, 'message': 'Error al actualizar la deuda'}), 500

    finally:
        cursor.close()  # Asegurarse de cerrar el cursor después de la operación

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

            logging.info(f'Rollback realizado: Cliente ID {id}. Valor revertido a: {valor_original}.')
            return jsonify({'success': True, 'message': 'Rollback exitoso'}), 200
        else:
            logging.warning('No hay cambios para deshacer. Valor original o ID del cliente no encontrados en la sesión.')
            return jsonify({'success': False, 'message': 'No hay cambios para deshacer'}), 400

    except Exception as e:
        logging.error(f'Error al realizar el rollback: {str(e)}')
        return jsonify({'success': False, 'message': 'Error al realizar el rollback'}), 500

    finally:
        cursor.close()  # Asegurarse de cerrar el cursor después de la operación