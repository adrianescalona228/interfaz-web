# routes/compras/historial_compras.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database2 import get_db
import logging

logger = logging.getLogger(__name__)

historial_compras_bp = Blueprint('historial_compras', __name__)

@historial_compras_bp.route('/historial_compras')
def historial_compras():
    try:
        db = get_db()

        cursor = db.execute('''SELECT c.id AS compra_id, c.numero_compra, c.fecha, p.nombre AS proveedor 
                            FROM Compras c 
                            JOIN Proveedores p ON c.proveedor_id = p.id 
                            ORDER BY c.numero_compra''')
        compras = cursor.fetchall()

        logging.info(f"Se cargaron {len(compras)} compras en el historial.")

        cursor.execute('''SELECT cp.compra_id, cp.producto_id, i.PRODUCTO AS producto, cp.cantidad, cp.costo 
                       FROM Productos_compras cp 
                       JOIN Inventario i ON cp.producto_id = i.id''')
        productos = cursor.fetchall()

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

        compras_agrupadas = []
        for compra in compras:
            compra_id = int(compra['numero_compra'])
            productos = productos_por_compra.get(compra_id, [])
            total_compra = sum(float(p['cantidad']) * float(p['costo']) for p in productos)

            compras_agrupadas.append({
                'numero_compra': compra['numero_compra'],
                'proveedor': compra['proveedor'],
                'fecha': compra['fecha'],
                'productos': productos,
                'total_compra': total_compra
            })

        logging.info("Historial de compras procesado correctamente.")
        return render_template('/compras/historial_compras.html', compras=compras_agrupadas)
    
    except Exception as e:
        logging.error(f"Error en la función historial_compras: {e}")
        logging.error(f"Detalles al momento del error: {compras}")
        return jsonify({'status': 'error', 'message': 'Hubo un problema al cargar el historial de compras.'}), 500
    
    finally:
        db.close()

@historial_compras_bp.route('/eliminar_compra/<int:numero_compra>', methods=['POST'])
def eliminar_venta(numero_compra):
    db = get_db()
    cursor = db.cursor()

    try:
        # Verificar si la compra existe en la tabla Compras
        cursor.execute('SELECT * FROM Compras WHERE numero_compra = ?', (numero_compra,))
        compra = cursor.fetchone()

        if compra:
            # Obtener los productos asociados a la compra
            cursor.execute('SELECT producto_id, cantidad FROM Productos_Compras WHERE compra_id = ?', (numero_compra,))
            productos = cursor.fetchall()

            # Eliminar la compra
            cursor.execute('DELETE FROM Compras WHERE numero_compra = ?', (numero_compra,))

            # Actualizar el inventario
            for producto in productos:
                producto_id = producto['producto_id']
                cantidad = producto['cantidad']
                logging.info(f'Producto id: {producto_id}, cantidad: {cantidad}')

                # Aumentar la cantidad del producto en el inventario
                cursor.execute('UPDATE Inventario SET cantidad = cantidad - ? WHERE id = ?', (cantidad, producto_id))  # Ajustado a + en lugar de -
                cursor.execute('DELETE FROM Productos_Compras WHERE compra_id = ?', (numero_compra,))

            db.commit()  # Hacer commit después de eliminar la compra

            flash('Compra y productos asociados eliminados correctamente', 'success')
        else:
            flash('La compra no existe', 'error')

    except Exception as e:
        logging.error(f'Error al eliminar compra {numero_compra}: {str(e)}')
        flash('Ocurrió un error al intentar eliminar la compra', 'error')

    finally:
        cursor.close()  # Cerrar el cursor después de la operación

    return '', 200

@historial_compras_bp.route('/eliminar_producto/<int:compra_id>/<int:producto_id>', methods=['POST'])
def eliminar_producto(compra_id, producto_id):
    db = get_db()
    cursor = db.cursor()

    try:
        # Obtener el costo y la cantidad del producto antes de eliminarlo
        cursor.execute('SELECT cantidad, costo FROM Productos_Compras WHERE compra_id = ? AND producto_id = ?', (compra_id, producto_id))
        producto = cursor.fetchone()

        if producto:
            cantidad = producto['cantidad']
            costo = producto['costo']
            total_restar = float(cantidad) * float(costo)

            # Registrar el estado del inventario antes de la actualización
            cursor.execute('SELECT cantidad FROM Inventario WHERE id = ?', (producto_id,))
            inventario_before = cursor.fetchone()
            cantidad_inventario_before = inventario_before['cantidad'] if inventario_before else 'No disponible'

            # Eliminar el producto de Productos_Compras
            cursor.execute('DELETE FROM Productos_Compras WHERE compra_id = ? AND producto_id = ?', (compra_id, producto_id))

            # Restar el costo del producto al total de la compra en la tabla Compras
            cursor.execute('UPDATE Compras SET total_compra = total_compra - ? WHERE id = ?', (total_restar, compra_id))

            # Actualizar el inventario
            cursor.execute('UPDATE Inventario SET cantidad = cantidad - ? WHERE id = ?', (cantidad, producto_id))

            # Registrar el estado del inventario después de la actualización
            cursor.execute('SELECT cantidad FROM Inventario WHERE id = ?', (producto_id,))
            inventario_after = cursor.fetchone()
            cantidad_inventario_after = inventario_after['cantidad'] if inventario_after else 'No disponible'

            db.commit()  # Hacer commit para guardar los cambios

            logging.info(f'Producto eliminado: Compra ID {compra_id}, Producto ID {producto_id}. '
                         f'Total restado: {total_restar}. Cantidad restada: {cantidad}. '
                         f'Inventario antes: {cantidad_inventario_before}. Inventario después: {cantidad_inventario_after}.')
        else:
            flash('El producto no existe en esta compra.', 'error')

    except Exception as e:
        logging.error(f'Error al eliminar producto: Compra ID {compra_id}, Producto ID {producto_id}. Error: {str(e)}')
        flash('Ocurrió un error al intentar eliminar el producto.', 'error')

    finally:
        cursor.close()  # Cerrar el cursor después de la operación

    return '', 200