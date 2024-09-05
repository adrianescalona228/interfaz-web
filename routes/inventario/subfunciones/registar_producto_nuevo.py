# routes/registrar_producto_nuevo.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db
import logging

registrar_producto_nuevo_bp = Blueprint('registrar_producto_nuevo', __name__)

@registrar_producto_nuevo_bp.route('/registrar_producto_nuevo')
def registrar_producto_nuevo():
    print('hola estoy dentro de reistrar producto nuevo')
    return render_template('/inventario/registrar_producto_nuevo.html')

@registrar_producto_nuevo_bp.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    data = request.json 
    logging.info(f'DATOS RECIBIDOS: {data}')

    # Extraer los campos del producto desde el JSON recibido
    producto = data.get('producto', '').upper()
    cantidad = 0
    precio = float(data.get('precio', 0))
    costo = float(data.get('costo', 0))
    tipo_de_producto = data.get('tipo_de_producto', '').upper()
    marca = data.get('marca', '').upper()

    logging.info(f'PRODUCTO: {producto}')
    logging.info(f'CANTIDAD: {cantidad}')
    logging.info(f'PRECIO: {precio}')
    logging.info(f'COSTO: {costo}')
    logging.info(f'TIPO DE PRODUCTO: {tipo_de_producto}')
    logging.info(f'MARCA: {marca}')

    # Validación simple
    if precio <= 0 or costo <= 0:
        logging.error('FALTAN CAMPOS O VALORES INCORRECTOS')
        return jsonify({'success': False, 'message': 'FALTAN CAMPOS O VALORES INCORRECTOS'}), 400

    try:
        db = get_db()
        cursor = db.cursor()

        # Insertar los datos en la tabla inventario
        cursor.execute('''
            INSERT INTO inventario (PRODUCTO, CANTIDAD, PRECIO, COSTO, TIPO_DE_PRODUCTO, MARCA)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (producto, cantidad, precio, costo, tipo_de_producto, marca))

        db.commit()  # Confirmar la transacción
        logging.info('PRODUCTO AGREGADO EXITOSAMENTE')
        
        return jsonify({'success': True, 'message': 'PRODUCTO AGREGADO EXITOSAMENTE'}), 201
    except Exception as e:
        logging.error(f'ERROR AL INTENTAR GUARDAR EL PRODUCTO: {e}', exc_info=True)
        return jsonify({'success': False, 'message': 'ERROR AL AGREGAR EL PRODUCTO'}), 500
    finally:
        cursor.close()
        db.close()
