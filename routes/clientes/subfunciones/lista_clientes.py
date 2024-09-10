# routes/agregar_stock.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db
import logging

lista_clientes_bp = Blueprint('lista_clientes', __name__)

@lista_clientes_bp.route('/lista_clientes')
def lista_clientes():
    db = get_db()   
    cursor = db.execute('SELECT * FROM Clientes')
    clientes = cursor.fetchall()
    return render_template('/clientes/lista_clientes.html', clientes=clientes)

@lista_clientes_bp.route('/actualizar_cliente', methods=['POST'])
def actualizar_cliente():
    data = request.json
    cliente_id = data.get('id')
    columna = data.get('column')
    valor = data.get('value')

    # Mapea la columna a los nombres reales de las columnas en la base de datos
    columnas_mapeadas = {
        'nombre': 'nombre_cliente',
        'razon_social': 'razon_social',
        'rif': 'rif_cedula',
        'direccion': 'direccion',
        'telefono': 'telefono'
    }

    columna_db = columnas_mapeadas.get(columna)
    if columna_db is None:
        return jsonify({'success': False, 'message': 'Columna no válida'}), 400

    try:
        # Aquí va el código para actualizar la base de datos
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f'''
            UPDATE clientes
            SET {columna_db} = ?
            WHERE id = ?
        ''', (valor, cliente_id))
        db.commit()
        logging.info(f'Cliente con ID {cliente_id} actualizado. Columna: {columna_db.upper()}, Nuevo valor: {valor.upper()}')
        return jsonify({'success': True, 'message': 'Cliente actualizado exitosamente'}), 200
    except Exception as e:
        logging.error(f'Error al actualizar el cliente. ID: {cliente_id}, Columna: {columna_db.upper()}, Valor: {valor.upper()} - Error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Error al actualizar el cliente'}), 500

    finally:
        cursor.close()  # Asegurarse de cerrar el cursor
        db.close()  # Asegurarse de cerrar la conexión
