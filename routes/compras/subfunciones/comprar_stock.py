# routes/agregar_stock.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

comprar_stock_bp = Blueprint('comprar_stock', __name__)

@comprar_stock_bp.route('/comprar_stock', methods=['GET', 'POST'])
def comprar_stock():
    # if request.method == 'POST':
    #     producto = request.form.get('producto')
    #     cantidad = float(request.form.get('cantidad', 0))  # Convertir cantidad a float
        
    #     db = get_db()
    #     cursor = db.execute('SELECT * FROM Inventario WHERE PRODUCTO LIKE ?', ('%' + producto + '%',))
    #     existing_product = cursor.fetchone()

    #     if existing_product:
    #         new_cantidad = float(existing_product['CANTIDAD']) + cantidad
    #         db.execute('UPDATE Inventario SET CANTIDAD = ? WHERE PRODUCTO = ?', (new_cantidad, existing_product['PRODUCTO']))
    #         db.commit()
    #         flash('Stock actualizado correctamente', 'success')
    #     else:
    #         flash('El producto no existe en el inventario', 'error')

    #     return redirect(url_for('/compras/comprar_stock'))

    return render_template('/compras/comprar_stock.html')

@comprar_stock_bp.route('/comprar_stock/procesar_compra', methods=['POST'])
def procesar_compra():
    data = request.get_json()
    proveedor_id = data.get('proveedor_id')
    numero_compra = data.get('numero_compra')
    fecha = data.get('fecha')
    productos = data.get('productos')
   
    db = get_db()
   
    try:
        db.execute('BEGIN')

        # Calcular el total de la compra
        total_compra = sum([producto['cantidad'] * producto['costo'] for producto in productos])

        # Insertar la compra en la tabla Compras con el total
        cursor = db.execute('INSERT INTO Compras (proveedor_id, numero_compra, fecha, total_compra) VALUES (?, ?, ?, ?)',
                            (proveedor_id, numero_compra, fecha, total_compra))
        compra_id = cursor.lastrowid

        # Insertar los productos en la tabla Productos_Compras
        for producto in productos:
            producto_id = obtener_id_producto(producto['nombre'])
            cantidad = producto['cantidad']
            costo = producto['costo']
            db.execute('INSERT INTO Productos_Compras (compra_id, producto_id, cantidad, costo) VALUES (?, ?, ?, ?)',
                       (compra_id, producto_id, cantidad, costo))

        db.execute('COMMIT')

        return jsonify({'success': True, 'message': 'Compra registrada exitosamente'})

    except Exception as e:
        db.execute('ROLLBACK')
        return jsonify({'success': False, 'message': str(e)})
    
def obtener_id_producto(nombre_producto):
    db = get_db()
    cursor = db.execute('SELECT id FROM Inventario WHERE PRODUCTO = ?', (nombre_producto,))
    return cursor.fetchone()['id']