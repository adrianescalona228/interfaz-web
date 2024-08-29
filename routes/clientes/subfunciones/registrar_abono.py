# routes/registrar_abono.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

registrar_abono_bp = Blueprint('registrar_abono', __name__)

@registrar_abono_bp.route('/template_abonos')
def template_abonos():
    return render_template('/clientes/registrar_abono.html')

@registrar_abono_bp.route('/registrar_abono', methods=['POST'])
def registrar_abono():
    try:
        data = request.get_json()
        cliente = data.get('cliente')
        monto_abono = float(data.get('monto'))
        fecha = data.get('fecha')

        if not cliente or not monto_abono or not fecha:
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400

        db = get_db()
        cursor = db.cursor()

        cliente_id = obtener_cliente_id(cursor, cliente)
        if not cliente_id:
            return jsonify({'success': False, 'message': 'Cliente no encontrado'}), 404

        registrar_abono_en_bd(cursor, cliente_id, monto_abono, fecha)
        aplicar_abono_a_facturas(cursor, cliente_id, monto_abono)
        actualizar_deuda_cliente(cursor, cliente_id, monto_abono)

        db.commit()
        return jsonify({'success': True, 'message': 'Abono registrado correctamente'})
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if db:
            db.close()

def obtener_cliente_id(cursor, cliente):
    cursor.execute('SELECT id FROM Clientes WHERE nombre_cliente = ?', (cliente,))
    result = cursor.fetchone()
    return result['id'] if result else None

def registrar_abono_en_bd(cursor, cliente_id, monto, fecha):
    cursor.execute('INSERT INTO Abonos (cliente_id, monto, fecha) VALUES (?, ?, ?)', 
                   (cliente_id, monto, fecha))

def aplicar_abono_a_facturas(cursor, cliente_id, monto_abono):
    # Obtener las facturas pendientes del cliente, ordenadas por fecha
    facturas = cursor.execute(
        "SELECT id, monto_total, monto_pagado, estado FROM Facturas WHERE cliente_id = ? AND estado = 'pendiente' ORDER BY fecha_emision",
        (cliente_id,)
    ).fetchall()

    for factura in facturas:
        monto_restante = factura['monto_total'] - factura['monto_pagado']

        if monto_abono >= monto_restante:
            # El abono cubre la factura completa
            monto_abono -= monto_restante
            cursor.execute(
                "UPDATE Facturas SET monto_pagado = monto_total, estado = 'PAGADO' WHERE id = ?",
                (factura['id'],)
            )
        else:
            # El abono cubre parte de la factura
            cursor.execute(
                "UPDATE Facturas SET monto_pagado = monto_pagado + ? WHERE id = ?",
                (monto_abono, factura['id'])
            )
            monto_abono = 0
            break  # El abono se ha agotado, salimos del bucle

def actualizar_deuda_cliente(cursor, cliente_id, monto):
    cursor.execute('''
        UPDATE Deudas 
        SET monto_total = monto_total - ?
        WHERE cliente_id = ?
    ''', (monto, cliente_id))
