# routes/compras/agregar_stock.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database2 import get_db
import logging

logger = logging.getLogger(__name__)

comprar_stock_bp = Blueprint('comprar_stock', __name__)

@comprar_stock_bp.route('/comprar_stock')
def comprar_stock():
    return render_template('/compras/comprar_stock.html')

@comprar_stock_bp.route('/procesar_compra', methods=['POST'])
def procesar_compra():
    try:
        data = request.get_json()
        proveedor = data['proveedor']
        numero_compra = data['compra_id']
        fecha = data['fecha']
        productos = data['productos']
        
        logger.debug(f"Datos recibidos: {data}")
    except (KeyError, TypeError) as e:
        logger.error(f"Error al procesar los datos de la solicitud: {e}")
        return jsonify({'status': 'error', 'message': f"Datos de entrada inválidos: {e}"})

    db = get_db()
    cursor = db.cursor()

    try:
        db.execute('BEGIN TRANSACTION')
        logger.info(f"Transacción iniciada para la compra: {numero_compra}")

        # Verificar si el número de compra ya existe
        cursor.execute('SELECT 1 FROM compras WHERE numero_compra = ?', (numero_compra,))
        if cursor.fetchone():
            raise ValueError('Este número de factura ya ha sido registrado.')


        proveedor_id = obtener_proveedor_id(cursor, proveedor)
        if proveedor_id is None:
            raise ValueError('Proveedor no encontrado')
        logger.info(f"ID del proveedor obtenido: {proveedor_id} para el proveedor: {proveedor}")

        total_compra = calcular_total_compra(productos)
        logger.info(f"Total de la compra calculado: {total_compra}")

        insertar_compra(cursor, proveedor_id, numero_compra, fecha, total_compra)
        logger.info(f"Compra insertada: {numero_compra}, Fecha: {fecha}, Total: {total_compra}")

        insertar_productos_compra(cursor, productos, numero_compra)
        logger.info(f"Productos de la compra insertados: {productos}")

        actualizar_inventario(cursor, productos)
        logger.info(f"Inventario actualizado para los productos de la compra: {productos}")

        db.commit()
        logger.info(f"Transacción confirmada para la compra: {numero_compra}")
        return jsonify({'status': 'success', 'message': 'Compra procesada correctamente'})

    except Exception as e:
        # Revertir la transacción en caso de error
        db.rollback()
        logger.error(f"Error al procesar la compra: {numero_compra}. Transacción revertida. Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

    finally:
        db.close()
        logger.debug(f"Conexión a la base de datos cerrada para la compra: {numero_compra}")

def obtener_proveedor_id(cursor, proveedor):
    try:
        cursor.execute('SELECT id FROM Proveedores WHERE nombre = ?', (proveedor,))
        row = cursor.fetchone()
        if row:
            return row['id']
        else:
            logging.warning(f'Proveedor "{proveedor}" no encontrado')
            return None
    except Exception as e:
        logging.error(f'Error al obtener el ID del proveedor: {e}')
        raise
def calcular_total_compra(productos):
    try:
        total_compra = sum(float(producto['costo']) * int(producto['cantidad']) for producto in productos)
        return round(total_compra, 2)
    except (ValueError, KeyError) as e:
        logging.error(f'Error al calcular el total de la compra: {e}')
        raise

def insertar_compra(cursor, proveedor_id, numero_compra, fecha, total_compra):
    try:
        cursor.execute('INSERT INTO Compras (proveedor_id, numero_compra, fecha, total_compra) VALUES (?, ?, ?, ?)',
                       (proveedor_id, numero_compra, fecha, total_compra))
    except Exception as e:
        logging.error(f'Error al insertar la compra: {e}')
        raise

def insertar_productos_compra(cursor, productos, compra_id):
    for producto in productos:
        try:
            producto_id = obtener_producto_id(cursor, producto['producto'])
            if producto_id is None:
                logging.warning(f'Producto "{producto["producto"]}" no encontrado')
                continue
            
            cursor.execute('INSERT INTO Productos_Compras (compra_id, producto_id, cantidad, costo) VALUES (?, ?, ?, ?)',
                           (compra_id, producto_id, producto['cantidad'], producto['costo']))
        except Exception as e:
            logging.error(f'Error al insertar productos en la compra: {e}')
            raise

def obtener_producto_id(cursor, producto_nombre):
    try:
        cursor.execute('SELECT id FROM Inventario WHERE PRODUCTO = ?', (producto_nombre,))
        row = cursor.fetchone()
        if row:
            return row['id']
        else:
            logging.warning(f'Producto "{producto_nombre}" no encontrado')
            return None
    except Exception as e:
        logging.error(f'Error al obtener el ID del producto: {e}')
        raise

def actualizar_inventario(cursor, productos):
    for producto in productos:
        try:
            cursor.execute('UPDATE Inventario SET cantidad = cantidad + ? WHERE PRODUCTO = ?',
                           (producto['cantidad'], producto['producto']))
        except Exception as e:
            logging.error(f'Error al actualizar el inventario para el producto "{producto["producto"]}": {e}')
            raise
        
# Ruta para obtener datos de autocompletado de clientes
@comprar_stock_bp.route('/autocompletar_proveedores', methods=['GET'])
def autocompletar_proveedores():
    term = request.args.get('term', '')
    
    # Conexión a la base de datos y consulta
    db = get_db()
    cursor = db.execute('SELECT nombre FROM Proveedores WHERE nombre LIKE ?', ('%' + term + '%',))
    clientes = [row['nombre'] for row in cursor.fetchall()]
    
    return jsonify(clientes)


# @comprar_stock_bp.route('/obtener_ultimo_numero_venta', methods=['GET'])
# def obtener_ultimo_numero_venta():
#     db = get_db()
#     cursor = db.cursor()
#     cursor.execute('SELECT MAX(numero_compra) as ultimo_numero FROM Compras')
#     result = cursor.fetchone()
#     ultimo_numero = result['ultimo_numero']
    
#     if ultimo_numero is None:
#         return jsonify({'ultimo_numero': 1})  # Si no hay ventas, empezar desde 1
#     else:
#         return jsonify({'ultimo_numero': int(ultimo_numero) + 1})
