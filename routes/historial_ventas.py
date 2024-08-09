# routes/historial_ventas.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from .database import get_db
from urllib.parse import quote, unquote

historial_ventas_bp = Blueprint('historial_ventas', __name__)

@historial_ventas_bp.route('/historial_ventas')
def historial_ventas():
    db = get_db()
    
    # Consulta para obtener todas las ventas ordenadas por número de venta
    cursor = db.execute('SELECT id, numero_venta, cliente, fecha, producto, cantidad, precio FROM Ventas ORDER BY numero_venta')
    ventas = cursor.fetchall()

    for venta in ventas:
        id = venta['id']
    
    # Lista para almacenar las ventas agrupadas
    ventas_agrupadas = []
    current_numero_venta = None
    venta_actual = None
    
    # Procesar cada venta y agruparlas por número de venta
    for venta in ventas:
        if venta['numero_venta'] != current_numero_venta:
            if venta_actual:
                # Calcular el total de la venta actual
                total_venta = sum(producto['cantidad'] * producto['precio'] for producto in venta_actual['productos'])
                venta_actual['total_venta'] = total_venta
                ventas_agrupadas.append(venta_actual)
            venta_actual = {
                'numero_venta': venta['numero_venta'],
                'cliente': venta['cliente'],
                'fecha': venta['fecha'],
                'productos': []
            }
            current_numero_venta = venta['numero_venta']

                # Verificar y convertir cantidad y precio
        try:
            cantidad = float(venta['cantidad']) if venta['cantidad'] else 0.0
        except ValueError:
            cantidad = 0.0
        
        try:
            precio = float(venta['precio']) if venta['precio'] else 0.0
        except ValueError:
            precio = 0.0
        
        
        venta_actual['productos'].append({
            'id': venta['id'],
            'producto': venta['producto'],
            'cantidad': cantidad,  # Convertir a float
            'precio': precio  # Convertir a float
        })
    
    # Añadir la última venta agrupada
    if venta_actual:
        # Calcular el total de la última venta
        total_venta = sum(float(producto['cantidad']) * float(producto['precio']) for producto in venta_actual['productos'])
        venta_actual['total_venta'] = total_venta
        ventas_agrupadas.append(venta_actual)
    return render_template('historial_ventas.html', ventas=ventas_agrupadas)

@historial_ventas_bp.route('/eliminar_venta/<int:numero_venta>', methods=['POST'])
def eliminar_venta(numero_venta):
    db = get_db()
    cursor = db.cursor()
    
    # Verificar si la venta existe
    cursor.execute('SELECT * FROM Ventas WHERE numero_venta = ?', (numero_venta,))
    venta = cursor.fetchone()

    if venta:
        cursor.execute('DELETE FROM Ventas WHERE numero_venta = ?', (numero_venta,))
        db.commit()
        flash('Venta eliminada correctamente', 'success')
    else:
        flash('La venta no existe', 'error')

    # Seleccionar la factura en base al número de venta a eliminar
    cursor.execute('SELECT monto_total, cliente_id FROM Facturas WHERE numero_venta = ?', (numero_venta,))
    factura = cursor.fetchone()

    if factura:
        # Conseguir el valor del monto total de la factura y el cliente_id
        monto_factura = factura[0]  # Nota: usando índices porque fetchone() devuelve una tupla
        cliente_id = factura[1]

        # Seleccionar el monto total de deudas para hacer la resta con el monto de la factura
        cursor.execute('SELECT monto_total FROM Deudas WHERE cliente_id = ?', (cliente_id,))
        deuda = cursor.fetchone()

        if deuda:
            monto_total_deuda = deuda[0]
            monto_final_deuda = monto_total_deuda - monto_factura

            # Actualizar la deuda en la tabla Deudas
            cursor.execute('UPDATE Deudas SET monto_total = ? WHERE cliente_id = ?', (monto_final_deuda, cliente_id))

        # Aquí agregarías el código para eliminar la factura
        cursor.execute('DELETE FROM Facturas WHERE numero_venta = ?', (numero_venta,))

    # Recuerda hacer commit después de realizar cambios
    db.commit()

    return redirect(url_for('historial_ventas.historial_ventas'))

# Ruta para eliminar un producto de una venta específica
@historial_ventas_bp.route('/eliminar_producto/<int:numero_venta>/<int:id>', methods=['POST'])
def eliminar_producto(numero_venta, id):
    db = get_db()
    cursor = db.cursor()

    # Verificar si el producto existe dentro de la venta
    cursor.execute('SELECT * FROM Ventas WHERE numero_venta = ? AND id = ?', (numero_venta, id))
    producto = cursor.fetchone()
    precio = producto[5]

    cursor.execute('SELECT cliente_id, monto_total FROM Facturas WHERE numero_venta = ?', (numero_venta,))
    factura = cursor.fetchone()
    monto_total_factura = factura[1]
    cliente_id = int(factura[0])
    monto_final_factura = monto_total_factura - precio

    cursor.execute('SELECT monto_total FROM Deudas WHERE cliente_id = ?', (cliente_id,))
    monto_total_deuda = cursor.fetchone()[0]
    monto_final_deuda = monto_total_deuda - precio

    print(producto)
    print(f'precio producto: {precio}')
    print(f'total deuda: {monto_total_deuda}')
    print(f'monto final: {monto_final_deuda}')
    print(f'monto factura: {monto_total_factura}')
    print(f'monto final: {monto_final_factura}')

    # monto = 0
    # terminal = 120
    # cursor.execute('UPDATE Deudas SET monto_total = ? WHERE cliente_id = ?', (monto, terminal))
    # db.commit()

    if producto:
        cursor.execute('DELETE FROM Ventas WHERE numero_venta = ? AND id = ?', (numero_venta, id))
        cursor.execute('UPDATE Deudas SET monto_total = ? WHERE cliente_id = ?', (monto_final_deuda, cliente_id))
        if monto_final_factura != 0:
            cursor.execute('UPDATE Facturas SET monto_total = ? WHERE numero_venta = ?', (monto_final_factura, numero_venta))
        elif monto_final_factura == 0:
            cursor.execute('DELETE FROM Facturas WHERE numero_venta = ?', (numero_venta,))    
        db.commit()
        print('si llegaste aqui, tas fino mirei')
        flash('Producto eliminado correctamente', 'success')
    else:
        flash('El producto no existe', 'error')
        print('si llegaste hasta aqui, no tas fino mirei')

    return redirect(url_for('historial_ventas.historial_ventas'))
