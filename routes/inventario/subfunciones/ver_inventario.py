# routes/mostrar_inventario.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database2 import get_db
import logging

ver_inventario_bp = Blueprint('ver_inventario', __name__)

@ver_inventario_bp.route('/ver_inventario')
def ver_inventario():
    db = get_db()   
    cursor = db.execute('SELECT * FROM inventario')
    inventario = cursor.fetchall()
    return render_template('/inventario/ver_inventario.html', inventario=inventario)

@ver_inventario_bp.route('/actualizar_producto', methods=['POST'])
def actualizar_producto():
    data = request.json
    producto_id = data.get('id')
    columna = data.get('column')
    valor = data.get('value')

    # Mapea la columna a los nombres reales de las columnas en la base de datos
    columnas_mapeadas = {
        'id': 'id',
        'producto': 'PRODUCTO',
        'cantidad': 'CANTIDAD',
        'precio': 'PRECIO',
        'costo': 'COSTO',
        'tipo_de_producto': 'TIPO_DE_PRODUCTO',
        'marca': 'MARCA'
    }

    columna_db = columnas_mapeadas.get(columna)
    if columna_db is None:
        return jsonify({'success': False, 'message': 'Columna no válida'}), 400

    try:
        # Aquí iría el código para actualizar la base de datos
        db = get_db()
        cursor = db.cursor()
        cursor.execute(f'''
            UPDATE inventario
            SET {columna_db} = ?
            WHERE id = ?
        ''', (valor, producto_id))
        db.commit()
        logging.info(f'Producto con ID {producto_id} actualizado. Columna: {columna_db.upper()}, Nuevo valor: {valor.upper()}')
        return jsonify({'success': True, 'message': 'Producto actualizado exitosamente'}), 200
    except Exception as e:
        logging.error(f'Error al actualizar el producto. ID: {producto_id}, Columna: {columna_db.upper()}, Valor: {valor.upper()} - Error: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'Error al actualizar el producto'}), 500

    finally:
        cursor.close()  # Asegurarse de cerrar el cursor
        db.close()  # Asegurarse de cerrar la conexión