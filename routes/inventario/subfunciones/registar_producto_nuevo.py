# routes/registrar_producto_nuevo.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

registrar_producto_nuevo_bp = Blueprint('registrar_producto_nuevo', __name__)

@registrar_producto_nuevo_bp.route('/registrar_producto_nuevo')
def registrar_producto_nuevo():
    print('hola estoy dentro de reistrar producto nuevo')
    return render_template('/inventario/registrar_producto_nuevo.html')

@registrar_producto_nuevo_bp.route('/guardar_producto', methods=['POST'])
def guardar_producto():
    data = request.json 
    print(f'Datos recibidos: {data}')

    # Extraer los campos del producto desde el JSON recibido
    producto = data.get('producto')
    cantidad = 0
    precio = float(data.get('precio'))
    costo = float(data.get('costo'))
    tipo_de_producto = data.get('tipo_de_producto', '')
    marca = data.get('marca', '')

    print(f'Producto: {producto}')
    print(f'Cantidad: {cantidad}')
    print(f'Precio: {precio}')
    print(f'Costo: {costo}')
    print(f'Tipo de Producto: {tipo_de_producto}')
    print(f'Marca: {marca}')

    # Validación simple
    if precio <= 0 or costo <= 0:
        return jsonify({'success': False, 'message': 'Faltan campos obligatorios o valores incorrectos'}), 400

    try:
        db = get_db()
        cursor = db.cursor()

        # Insertar los datos en la tabla inventario
        cursor.execute('''
            INSERT INTO inventario (PRODUCTO, CANTIDAD, PRECIO, COSTO, TIPO_DE_PRODUCTO, MARCA)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (producto, cantidad, precio, costo, tipo_de_producto, marca))

        db.commit()  # Confirmar la transacción
        cursor.close()

        return jsonify({'success': True, 'message': 'Producto agregado exitosamente'}), 201
    except Exception as e:
        print(f'Error al intentar guardar el producto: {e}')
        return jsonify({'success': False, 'message': 'Error al agregar el producto'}), 500

