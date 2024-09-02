# routes/historial_ventas.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db
from urllib.parse import quote, unquote
import os
from openpyxl import load_workbook

historial_ventas_bp = Blueprint('historial_ventas', __name__)

ruta_libro = r"C:\Users\adria\Documents\programacion\interfaz-web\DATABASE\NDE_PLANTILLA.xlsx"

@historial_ventas_bp.route('/historial_ventas')
def historial_ventas():
    db = get_db()
    
    # Consulta para obtener todas las ventas ordenadas por número de venta
    cursor = db.execute('''SELECT v.id, v.numero_venta, v.cliente, v.fecha, v.producto, 
                        v.cantidad, v.precio, f.fecha_vencimiento, f.monto_pagado, f.estado
                        FROM Ventas v 
                        JOIN Facturas f ON v.numero_venta = f.numero_venta
                        ORDER BY v.numero_venta''')
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
                'productos': [],
                'fecha_vencimiento': venta['fecha_vencimiento'],
                'monto_pagado': venta['monto_pagado'],
                'estado': venta['estado']
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

    return render_template('/ventas/historial_ventas.html', ventas=ventas_agrupadas)

@historial_ventas_bp.route('/eliminar_venta/<int:numero_venta>', methods=['POST'])
def eliminar_venta(numero_venta):
    db = get_db()
    cursor = db.cursor()
    
    # Verificar si la venta existe
    cursor.execute('SELECT * FROM Ventas WHERE numero_venta = ?', (numero_venta,))
    venta = cursor.fetchone()

    if venta:
        # Seleccionar la factura asociada a la venta
        cursor.execute('SELECT monto_total, cliente_id FROM Facturas WHERE numero_venta = ?', (numero_venta,))
        factura = cursor.fetchone()

        if factura:
            monto_factura = factura[0]
            cliente_id = factura[1]

            # Eliminar la venta
            cursor.execute('DELETE FROM Ventas WHERE numero_venta = ?', (numero_venta,))

            # Eliminar la factura
            cursor.execute('DELETE FROM Facturas WHERE numero_venta = ?', (numero_venta,))

            # Actualizar la deuda del cliente
            cursor.execute('SELECT monto_total FROM Deudas WHERE cliente_id = ?', (cliente_id,))
            deuda_actual = cursor.fetchone()

            if deuda_actual:
                monto_total_deuda = deuda_actual[0]
                monto_final_deuda = monto_total_deuda - monto_factura

                # Solo actualizar si la deuda es positiva
                if monto_final_deuda >= 0:
                    cursor.execute('UPDATE Deudas SET monto_total = ? WHERE cliente_id = ?', (monto_final_deuda, cliente_id))
                else:
                    cursor.execute('DELETE FROM Deudas WHERE cliente_id = ?', (cliente_id,))
        else:
            flash('Factura no encontrada para la venta', 'error')

        db.commit()
        flash('Venta y factura eliminadas correctamente', 'success')
    else:
        flash('La venta no existe', 'error')

    db.close()
    return '', 200

# Ruta para eliminar un producto de una venta específica
@historial_ventas_bp.route('/eliminar_producto/<int:numero_venta>/<int:id>', methods=['POST'])
def eliminar_producto(numero_venta, id):
    print(numero_venta,id)
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

    return '', 200  


@historial_ventas_bp.route('/generar_nota_entrega', methods=['GET', 'POST'])
def generar_nota_entrega():
    print('llegaste correctamente a /generar_nota_entrega')
    data = request.json
    numero_venta= data.get('numero_venta')
    
    datos_cliente = obtener_datos_cliente_y_venta(numero_venta)
    print(datos_cliente)

    if not datos_cliente:
            return jsonify({'mensaje': 'Cliente o venta no encontrado'}), 404
    
    libro = abrir_libro_excel(ruta_libro)
    crear_nota_entrega(libro, datos_cliente)
    

    return jsonify({"message": "Nota de entrega generada"}), 200


    # if request.method == 'POST':
    #     numero_venta = request.form.get('numero_venta')
    #     datos_cliente = obtener_datos_cliente_y_venta(numero_venta)
        
    #     if not datos_cliente:
    #         return jsonify({'mensaje': 'Cliente o venta no encontrado'}), 404
           
    #     libro = abrir_libro_excel(ruta_libro)
    #     ruta_archivo = crear_nota_entrega(libro, datos_cliente)
        
    #     # Aquí puedes redirigir a una página de éxito o simplemente renderizar una plantilla de confirmación
    #     return render_template('crear_notas_entrega.html', ruta_archivo=ruta_archivo)
    # else:
    #     return render_template('crear_notas_entrega.html')
    
def abrir_libro_excel(ruta_archivo):
    return load_workbook(ruta_archivo)

def obtener_datos_cliente_y_venta(numero_venta):
    db = get_db()
    cursor = db.cursor()

    # Obtener el nombre del cliente basado en el número de venta
    cursor.execute("SELECT cliente FROM Ventas WHERE numero_venta = ?", (numero_venta,))
    cliente = cursor.fetchone()
    if not cliente:
        return None
    
    nombre_cliente = cliente[0]

    # Obtener datos del cliente
    cursor.execute("SELECT razon_social, rif_cedula, direccion, telefono FROM Clientes WHERE nombre_cliente = ?", (nombre_cliente,))
    cliente = cursor.fetchone()
    if not cliente:
        return None
    
    razon_social, rif_cedula, direccion, telefono = cliente
    
    # Obtener todas las ventas asociadas al número de venta específico
    cursor.execute("SELECT numero_venta, producto, cantidad, precio, fecha FROM Ventas WHERE numero_venta = ?", (numero_venta,))
    productos = cursor.fetchall()  # Obtener todas las ventas asociadas
    
    print(cliente)
    print(productos)

    db.close()
        
    if productos:
        # Organizar todas las ventas en una lista de diccionarios
        ventas_list = [
            {
                'numero_venta': producto[0],
                'producto': producto[1].strip(),
                'cantidad': producto[2],
                'precio': producto[3],
                'fecha': producto[4]
            }
            for producto in productos
        ]

        return {
            'nombre_cliente': nombre_cliente.strip(),
            'razon_social': razon_social.strip(),
            'rif_cedula': rif_cedula.strip(),
            'direccion': direccion.strip(),
            'telefono': telefono.strip(),
            'ventas': ventas_list  # Ahora es una lista de ventas
        }
    else:
        return {
            'error': 'No se encontró la venta'
        }
def crear_nota_entrega(libro, datos_cliente):
    hoja = libro.active  # Usar la hoja activa de la plantilla
    
    # Insertar datos del cliente
    hoja['I3'] = datos_cliente['razon_social']
    hoja['AC3'] = datos_cliente['rif_cedula']
    hoja['F5'] = datos_cliente['direccion']
    hoja['AC7'] = datos_cliente['telefono']

    # Obtener fecha y número de venta del primer elemento en las ventas
    if datos_cliente['ventas']:
        primer_producto = datos_cliente['ventas'][0]  # Corregido para obtener el primer producto
        hoja['G7'] = primer_producto['fecha']
        hoja['AF1'] = primer_producto['numero_venta']

    # Insertar datos de las ventas
    fila_inicio = 12  # Supongamos que comenzamos a escribir las ventas en la fila 12
    for producto in datos_cliente['ventas']:  # Corregido a 'ventas'
        hoja[f'D{fila_inicio}'] = producto['producto']
        hoja[f'A{fila_inicio}'] = producto['cantidad']
        hoja[f'Y{fila_inicio}'] = producto['precio']
        fila_inicio += 1
    
    # Definir la ruta de guardado
    ruta_guardar = r"C:\Users\adria\Documents\programacion\interfaz-web\DATABASE\NDE"
    if not os.path.exists(ruta_guardar):
        os.makedirs(ruta_guardar)
    
    # Crear el nombre del archivo
    nombre_archivo = f"NDE_{primer_producto['numero_venta']}_{datos_cliente['nombre_cliente']}.xlsx"
    
    # Ruta completa
    ruta_completa = os.path.join(ruta_guardar, nombre_archivo)
    
    # Guardar archivo
    libro.save(ruta_completa)
    
    return ruta_completa