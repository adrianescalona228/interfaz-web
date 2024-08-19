# routes/compras/agregar_stock.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

comprar_stock_bp = Blueprint('comprar_stock', __name__)

@comprar_stock_bp.route('/comprar_stock')
def comprar_stock():
    return render_template('/compras/comprar_stock.html')

@comprar_stock_bp.route('/procesar_compra', methods=['POST'])
def procesar_compra():
    data = request.get_json()
    
    proveedor = data['proveedor']
    numero_compra = data['compra_id']
    fecha = data['fecha']
    productos = data['productos']
    
    db = get_db()
    cursor = db.cursor()

    print(data)
    try:
        # Iniciar la transacción
        db.execute('BEGIN TRANSACTION')

        # Obtener el ID del proveedor
        proveedor_id = obtener_proveedor_id(cursor, proveedor)
        if proveedor_id is None:
            raise ValueError('Proveedor no encontrado')

        # Calcular el total de la compra
        total_compra = calcular_total_compra(productos)
        
        # Insertar la compra
        insertar_compra(cursor, proveedor_id, numero_compra, fecha, total_compra)
        
        # Insertar los productos de la compra
        insertar_productos_compra(cursor, productos, numero_compra)
        
        # Actualizar el inventario
        actualizar_inventario(cursor, productos)
        
        # Confirmar la transacción
        db.commit()
        return jsonify({'status': 'success', 'message': 'Compra procesada correctamente'})
    
    except Exception as e:
        # Revertir la transacción en caso de error
        db.rollback()
        return jsonify({'status': 'error', 'message': str(e)})
    
    finally:
        db.close()

def obtener_proveedor_id(cursor, proveedor):
    cursor.execute('SELECT id FROM Proveedores WHERE nombre = ?', (proveedor,))
    row = cursor.fetchone()
    return row['id'] if row else None

def calcular_total_compra(productos):
    return sum(float(producto['costo']) * int(producto['cantidad']) for producto in productos)

def insertar_compra(cursor, proveedor_id, numero_compra, fecha, total_compra):
    cursor.execute('INSERT INTO Compras (proveedor_id, numero_compra, fecha, total_compra) VALUES (?, ?, ?, ?)',
                   (proveedor_id, numero_compra, fecha, total_compra))

def insertar_productos_compra(cursor, productos, compra_id):
    for producto in productos:
        # Obtener el ID del producto desde Inventario
        producto_id = obtener_producto_id(cursor, producto['producto'])
        if producto_id is None:
            raise ValueError(f'Producto {producto["producto"]} no encontrado')
        
        cursor.execute('INSERT INTO Productos_Compras (compra_id, producto_id, cantidad, costo) VALUES (?, ?, ?, ?)',
                       (compra_id, producto_id, producto['cantidad'], producto['costo']))

def obtener_producto_id(cursor, producto_nombre):
    cursor.execute('SELECT id FROM Inventario WHERE PRODUCTO = ?', (producto_nombre,))
    row = cursor.fetchone()
    return row['id'] if row else None

def actualizar_inventario(cursor, productos):
    for producto in productos:
        cursor.execute('UPDATE Inventario SET cantidad = cantidad + ? WHERE PRODUCTO = ?',
                       (producto['cantidad'], producto['producto']))

# Ruta para obtener datos de autocompletado de clientes
@comprar_stock_bp.route('/autocompletar_proveedores', methods=['GET'])
def autocompletar_proveedores():
    term = request.args.get('term', '')
    
    # Conexión a la base de datos y consulta
    db = get_db()
    cursor = db.execute('SELECT nombre FROM Proveedores WHERE nombre LIKE ?', ('%' + term + '%',))
    clientes = [row['nombre'] for row in cursor.fetchall()]
    
    return jsonify(clientes)


@comprar_stock_bp.route('/obtener_ultimo_numero_venta', methods=['GET'])
def obtener_ultimo_numero_venta():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT MAX(numero_compra) as ultimo_numero FROM Compras')
    result = cursor.fetchone()
    ultimo_numero = result['ultimo_numero']
    
    if ultimo_numero is None:
        return jsonify({'ultimo_numero': 1})  # Si no hay ventas, empezar desde 1
    else:
        return jsonify({'ultimo_numero': int(ultimo_numero) + 1})
