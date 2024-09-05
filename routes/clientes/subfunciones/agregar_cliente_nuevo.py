# routes/agregar_stock.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db
import logging

agregar_clientes_nuevos_bp = Blueprint('agregar_clientes_nuevos', __name__)

@agregar_clientes_nuevos_bp.route('/agregar_clientes_nuevos')
def agregar_clientes_nuevos():
    return render_template('/clientes/agregar_clientes_nuevos.html')

@agregar_clientes_nuevos_bp.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    db = get_db()
    cursor = db.cursor()

    try:
        nombre = request.json.get('nombre').upper()
        razon_social = request.json.get('razon_social').upper()
        rif_cedula = request.json.get('rif_cedula')
        direccion = request.json.get('direccion').upper()
        telefono = request.json.get('telefono')

        logging.info(f'Guardando cliente: {nombre}, {razon_social}, {rif_cedula}, {direccion}, {telefono}')

        # Insertar los datos en la tabla Clientes
        cursor.execute('''
            INSERT INTO Clientes (nombre_cliente, razon_social, rif_cedula, direccion, telefono)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, razon_social, rif_cedula, direccion, telefono))

        # Obtener el ID del cliente recién insertado
        cliente_id = cursor.lastrowid

        # Insertar la nueva entrada en la tabla Deudas con monto 0
        cursor.execute('''
            INSERT INTO Deudas (cliente_id, monto_total)
            VALUES (?, ?)
        ''', (cliente_id, 0))

        db.commit()
        logging.info(f'Cliente con ID {cliente_id} agregado correctamente.')

        response_data = {
            'success': True,
            'message': 'Cliente agregado correctamente',
            'data': {
                'nombre': nombre,
                'razon_social': razon_social,
                'rif_cedula': rif_cedula,
                'direccion': direccion,
                'telefono': telefono
            }
        }
        return jsonify(response_data), 201

    except Exception as e:
        logging.error(f'Error al agregar el cliente: {e}', exc_info=True)
        db.rollback()  # Deshacer cambios en caso de error

        response_data = {
            'success': False,
            'message': 'Ocurrió un error al agregar el cliente'
        }
        return jsonify(response_data), 500

    finally:
        cursor.close()  # Asegurarse de cerrar el cursor
        db.close()  # Asegurarse de cerrar la conexión