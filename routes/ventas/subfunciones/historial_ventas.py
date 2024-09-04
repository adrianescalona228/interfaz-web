# routes/historial_ventas.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db
from urllib.parse import quote, unquote
import os
from openpyxl import load_workbook
import win32com.client as win32
import pythoncom

historial_ventas_bp = Blueprint('historial_ventas', __name__)

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

    data = request.json
    numero_venta= data.get('numero_venta')
    
    datos_cliente = obtener_datos_cliente_y_venta(numero_venta)
    crear_nota_entrega(datos_cliente)

    if not datos_cliente:
            return jsonify({'mensaje': 'Cliente o venta no encontrado'}), 404
    
    return jsonify({"message": "Nota de entrega generada"}), 200

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
    
def insertar_direccion(sheet, direccion, fila_inicial):
    ancho_maximo = 80

    if len(direccion) > ancho_maximo:
        punto_corte = direccion.rfind(' ', 0, ancho_maximo)
        if punto_corte == -1:
            punto_corte = ancho_maximo

        direccion_1 = direccion[:punto_corte]
        direccion_2 = direccion[punto_corte + 1:]

        # Insertar la primera parte en la primera celda
        rango_celda_1 = sheet.Cells(fila_inicial, 6).MergeArea
        rango_celda_1.Cells(1, 1).Value = direccion_1

        # Insertar la segunda parte en la celda de abajo
        rango_celda_2 = sheet.Cells(fila_inicial + 1, 6).MergeArea
        rango_celda_2.Cells(1, 1).Value = direccion_2
    else:
        rango_celda_1 = sheet.Cells(fila_inicial, 6).MergeArea
        rango_celda_1.Cells(1, 1).Value = direccion

def crear_nota_entrega(datos_cliente):
    print("Iniciando la creación de la nota de entrega...")
    try:
        # Inicializar la COM de Python
        pythoncom.CoInitialize()
        print("COM de Python inicializada correctamente.")

        # Rutas
        ruta_plantilla = r"C:\Users\arnaldo\Dropbox\TRABAJO\NOTA_DE_ENTREGA 2.0\NDE._PLANTILLA2.xlsx"
        ruta_guardar = r"C:\Users\arnaldo\Dropbox\TRABAJO\NOTA_DE_ENTREGA 2.0"
        #ruta_guardar = r"C:\Users\arnaldo\Desktop"
        print(f"Ruta de la plantilla: {ruta_plantilla}")
        print(f"Ruta para guardar: {ruta_guardar}")

        # Verificar que el archivo de plantilla existe
        if not os.path.exists(ruta_plantilla):
            raise FileNotFoundError(f"La plantilla no se encontró en la ruta: {ruta_plantilla}")

        # Iniciar Excel
        try:
            excel = win32.DispatchEx('Excel.Application')
            print("Excel iniciado correctamente.")
        except Exception as e:
            print(f"Error al iniciar Excel: {e}")
            raise

        # Verificar que Excel se inicializó correctamente
        if excel is None:
            raise RuntimeError("No se pudo iniciar Excel. Asegúrate de que esté instalado correctamente.")

        # Abrir la plantilla
        try:
            workbook = excel.Workbooks.Open(ruta_plantilla)
            print("Plantilla de Excel abierta correctamente.")
        except Exception as e:
            print(f"Error al abrir la plantilla de Excel: {e}")
            raise

        # Modificar la hoja activa con los datos del cliente
        try:
            sheet = workbook.ActiveSheet
            print("Hoja activa seleccionada correctamente.")

            sheet.Cells(3, 9).Value = datos_cliente['razon_social']  # I3
            sheet.Cells(3, 29).Value = datos_cliente['rif_cedula']  # AC3
            print("Datos del cliente (razón social y RIF/Cédula) insertados correctamente.")
            
            # Insertar la dirección con la función personalizada
            insertar_direccion(sheet, datos_cliente['direccion'], 5)  # F5 es la fila inicial
            print("Dirección del cliente insertada correctamente.")
            
            sheet.Cells(7, 29).Value = datos_cliente['telefono']  # AC7
            print("Teléfono del cliente insertado correctamente.")

            if datos_cliente['ventas']:
                primer_producto = datos_cliente['ventas'][0]
                sheet.Cells(7, 7).Value = primer_producto['fecha']  # G7
                sheet.Cells(1, 32).Value = primer_producto['numero_venta']  # AF1
                print("Datos de la primera venta insertados correctamente.")

            fila_inicio = 12
            for producto in datos_cliente['ventas']:
                sheet.Cells(fila_inicio, 1).Value = producto['cantidad']  # A
                sheet.Cells(fila_inicio, 4).Value = producto['producto']  # D
                sheet.Cells(fila_inicio, 25).Value = producto['precio']  # Y
                fila_inicio += 1
            print("Datos de todos los productos insertados correctamente.")

        except Exception as e:
            print(f"Error al modificar la hoja activa: {e}")
            raise

        # Guardar el archivo
        try:
            nombre_archivo = f"NDE.{primer_producto['numero_venta']}_{datos_cliente['nombre_cliente']}.xlsx"
            ruta_completa = os.path.join(ruta_guardar, nombre_archivo)
            workbook.SaveAs(ruta_completa)
            workbook.Close()
            print(f"Archivo guardado correctamente en: {ruta_completa}")
        except Exception as e:
            print(f"Error al guardar el archivo: {e}")
            raise

        # Abrir el archivo guardado
        try:
            os.startfile(ruta_completa)
            print(f"Archivo {nombre_archivo} abierto correctamente.")
        except Exception as e:
            print(f"Error al abrir el archivo guardado: {e}")
            raise

        print("Proceso de creación de la nota de entrega completado.")
        return ruta_completa

    except Exception as e:
        print(f"Se encontró un error: {e}")
