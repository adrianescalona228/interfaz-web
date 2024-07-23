# routes/historial_ventas.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from .database import get_db
from urllib.parse import quote

historial_ventas_bp = Blueprint('historial_ventas', __name__)

@historial_ventas_bp.route('/historial_ventas')
def historial_ventas():
    db = get_db()
    
    # Consulta para obtener todas las ventas ordenadas por número de venta
    cursor = db.execute('SELECT numero_venta, cliente, fecha, producto, cantidad, precio FROM Ventas ORDER BY numero_venta')
    ventas = cursor.fetchall()
    
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

    return redirect(url_for('historial_ventas.historial_ventas'))

# Ruta para eliminar un producto de una venta específica
@historial_ventas_bp.route('/eliminar_producto/<int:numero_venta>/<nombre_producto>', methods=['POST'])
def eliminar_producto(numero_venta, nombre_producto):
    db = get_db()
    cursor = db.cursor()

    # Codificar el nombre del producto para asegurar la URL
    nombre_codificado = quote(nombre_producto)

    # Verificar si el producto existe dentro de la venta
    cursor.execute('SELECT * FROM Ventas WHERE numero_venta = ? AND producto = ?', (numero_venta, nombre_codificado))
    producto = cursor.fetchone()

    if producto:
        cursor.execute('DELETE FROM Ventas WHERE numero_venta = ? AND producto = ?', (numero_venta, nombre_codificado))
        db.commit()
        flash('Producto eliminado correctamente', 'success')
    else:
        flash('El producto no existe', 'error')

    return redirect(url_for('historial_ventas'))
