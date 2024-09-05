import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db
import logging

historial_abonos_bp = Blueprint('historial_abonos', __name__)

@historial_abonos_bp.route('/historial_abonos')
def historial_abonos():
    db = get_db()   
    cursor = db.execute('''SELECT a.id, c.nombre_cliente, a.monto, a.fecha 
                        FROM Clientes c
                        JOIN Abonos a ON c.id = a.cliente_id
                        ''')
    abonos = cursor.fetchall()
    return render_template('/clientes/historial_abonos.html', abonos=abonos)

@historial_abonos_bp.route('/eliminar_abono/<int:abono_id>', methods=['POST'])
def eliminar_abono(abono_id):
    db = get_db()
    cursor = db.cursor()

    try:
        logging.info(f'Intentando eliminar el abono con ID {abono_id}.')
        
        # Verificar si el abono existe
        cursor.execute('SELECT * FROM Abonos WHERE id = ?', (abono_id,))
        abono = cursor.fetchone()

        if abono:
            # Obtener el monto del abono
            monto_abono = abono['monto']
            cliente_id = abono['cliente_id']

            logging.info(f'Abono encontrado. Monto: {monto_abono}, Cliente ID: {cliente_id}.')

            # Eliminar el abono
            cursor.execute('DELETE FROM Abonos WHERE id = ?', (abono_id,))
            logging.info(f'Abono con ID {abono_id} eliminado de la base de datos.')

            # Actualizar la deuda del cliente
            cursor.execute('UPDATE Deudas SET monto_total = monto_total + ? WHERE cliente_id = ?', (monto_abono, cliente_id))
            db.commit()  # Hacer commit después de los cambios
            logging.info(f'Deuda del cliente con ID {cliente_id} actualizada con el monto {monto_abono}.')
            
            flash('Abono eliminado correctamente y deuda actualizada', 'success')
        else:
            logging.error(f'El abono con ID {abono_id} no existe en la base de datos.')
            flash('El abono no existe', 'error')

    except sqlite3.Error as e:
        logging.error(f'Error al procesar la solicitud para eliminar el abono con ID {abono_id}: {e}', exc_info=True)
        flash(f'Error al procesar la solicitud: {e}', 'error')
        db.rollback()  # Revertir en caso de error

    finally:
        cursor.close()  # Asegurarse de cerrar el cursor
        logging.info('Cursor cerrado.')

    return '', 200