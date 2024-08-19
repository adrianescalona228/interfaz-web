# routes/compras/historial_compras.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

historial_compras_bp = Blueprint('historial_compras', __name__)

@historial_compras_bp.route('/historial_compras')
def historial_compras():
    db = get_db()
    
    # Consulta para obtener todas las compras
    cursor = db.execute('SELECT c.id AS compra_id, c.numero_compra, c.fecha, p.nombre AS proveedor FROM Compras c JOIN Proveedores p ON c.proveedor_id = p.id ORDER BY c.numero_compra')
    compras = cursor.fetchall()
    
    # Consulta para obtener los productos de cada compra
    cursor.execute('SELECT cp.compra_id, cp.producto_id, i.PRODUCTO AS producto, cp.cantidad, cp.costo FROM Productos_compras cp JOIN Inventario i ON cp.producto_id = i.id')
    productos = cursor.fetchall()

    # Crear un diccionario para agrupar productos por compra
    productos_por_compra = {}
    for producto in productos:
        compra_id = producto['compra_id']
        if compra_id not in productos_por_compra:
            productos_por_compra[compra_id] = []
        productos_por_compra[compra_id].append({
            'producto_id': producto['producto_id'],
            'producto': producto['producto'],
            'cantidad': producto['cantidad'],
            'costo': producto['costo']
        })
    
    # Lista para almacenar las compras agrupadas
    compras_agrupadas = []
    
    for compra in compras:
        compra_id = compra['compra_id']
        productos = productos_por_compra.get(compra_id, [])
        
        # Calcular el total de la compra
        total_compra = sum(float(p['cantidad']) * float(p['costo']) for p in productos)
        
        compras_agrupadas.append({
            'numero_compra': compra['numero_compra'],
            'proveedor': compra['proveedor'],
            'fecha': compra['fecha'],
            'productos': productos,
            'total_compra': total_compra
        })
    
    return render_template('/compras/historial_compras.html', compras=compras_agrupadas)

@historial_compras_bp.route('/eliminar_compra/<int:numero_compra>', methods=['POST'])
def eliminar_venta(numero_compra):
    db = get_db()
    cursor = db.cursor()

    # Verificar si la compra existe en la tabla Compras
    cursor.execute('SELECT * FROM Compras WHERE numero_compra = ?', (numero_compra,))
    compra = cursor.fetchone()

    if compra:
        # Eliminar los productos asociados a la compra
        cursor.execute('DELETE FROM Productos_Compras WHERE compra_id = ?', (compra['id'],))
        db.commit()  # Hacer commit después de eliminar los productos

        # Eliminar la compra
        cursor.execute('DELETE FROM Compras WHERE numero_compra = ?', (numero_compra,))
        db.commit()  # Hacer commit después de eliminar la compra

        flash('Compra y productos asociados eliminados correctamente', 'success')
    else:
        flash('La compra no existe', 'error')

    cursor.close()  # Cerrar el cursor después de la operación

    return '', 200

@historial_compras_bp.route('/eliminar_producto/<int:compra_id>/<int:producto_id>', methods=['POST'])
def eliminar_producto(compra_id, producto_id):
    db = get_db()
    cursor = db.cursor()

    # Obtener el costo del producto antes de eliminarlo
    cursor.execute('SELECT cantidad, costo FROM Productos_Compras WHERE compra_id = ? AND producto_id = ?', (compra_id, producto_id))
    producto = cursor.fetchone()

    if producto:
        # Eliminar el producto de Productos_Compras
        cursor.execute('DELETE FROM Productos_Compras WHERE compra_id = ? AND producto_id = ?', (compra_id, producto_id))
        
        # Restar el costo del producto al total de la compra en la tabla Compras
        total_restar = float(producto['cantidad']) * float(producto['costo'])
        cursor.execute('UPDATE Compras SET total_compra = total_compra - ? WHERE id = ?', (total_restar, compra_id))
        
        db.commit()  # Hacer commit para guardar los cambios
        flash('Producto eliminado y total actualizado correctamente.', 'success')
    else:
        flash('El producto no existe en esta compra.', 'error')

    cursor.close()
    return '', 200
