import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

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

    # Verificar si el abono existe
    cursor.execute('SELECT * FROM Abonos WHERE id = ?', (abono_id,))
    abono = cursor.fetchone()

    if abono:
        # Obtener el monto del abono
        monto_abono = abono['monto']

        # Obtener el id del cliente asociado con el abono
        cliente_id = abono['cliente_id']

        # Eliminar el abono
        cursor.execute('DELETE FROM Abonos WHERE id = ?', (abono_id,))
        db.commit()  # Hacer commit después de eliminar el abono

        # Actualizar la deuda del cliente
        cursor.execute('UPDATE Deudas SET monto_total = monto_total + ? WHERE cliente_id = ?', (monto_abono, cliente_id))
        db.commit()  # Hacer commit después de actualizar la deuda

        flash('Abono eliminado correctamente y deuda actualizada', 'success')
    else:
        flash('El abono no existe', 'error')

    cursor.close()  # Cerrar el cursor después de la operación

    return '', 200
