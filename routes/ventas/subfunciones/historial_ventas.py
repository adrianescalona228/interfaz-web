# routes/historial_ventas.py
import sqlite3
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database2 import get_db
from urllib.parse import quote, unquote
import os
from openpyxl import load_workbook
import win32com.client as win32
import pythoncom
import logging
from config_global import config_global

logger = logging.getLogger(__name__)
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
            try:
                fecha_objeto = datetime.strptime(venta_actual['fecha'], '%Y-%m-%d') #YYYY-MM-DD
                venta_actual['fecha'] = fecha_objeto.strftime('%d-%m-%Y') #DD-MM-YYYY
            except ValueError:
            # Manejar el error si la fecha no tiene el formato esperado
                print(f"Error: Formato de fecha incorrecto encontrado: {venta_actual['fecha']}")
            # Puedes dejar la fecha sin cambios o asignarle un valor por defecto
            # venta_actual['fecha'] = 'Fecha Inválida'
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
    cliente = request.form.get('cliente')
    logger = logging.getLogger(__name__)  # Obtén el logger para esta ruta
    db = get_db()
    cursor = db.cursor()
    
    try:
        logger.info(f'Intentando eliminar la venta con número {numero_venta}')
        
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

                try:
                    # Obtener los productos y cantidades de la venta antes de eliminarla
                    cursor.execute('SELECT producto, cantidad FROM Ventas WHERE numero_venta = ?', (numero_venta,))
                    detalles_venta = cursor.fetchall()
                    print(detalles_venta)

                    # Eliminar la venta
                    cursor.execute('DELETE FROM Ventas WHERE numero_venta = ?', (numero_venta,))
                    logger.info(f'Venta con número {numero_venta} eliminada.')

                    # Eliminar la factura
                    cursor.execute('DELETE FROM Facturas WHERE numero_venta = ?', (numero_venta,))
                    logger.info(f'Factura asociada a la venta {numero_venta} eliminada.')

                    # Actualizar la deuda del cliente
                    cursor.execute('SELECT monto_total FROM Deudas WHERE cliente_id = ?', (cliente_id,))
                    deuda_actual = cursor.fetchone()

                    if deuda_actual:
                        monto_total_deuda = deuda_actual[0]
                        monto_final_deuda = monto_total_deuda - monto_factura

                        if monto_final_deuda >= 0:
                            cursor.execute('UPDATE Deudas SET monto_total = ? WHERE cliente_id = ?', (monto_final_deuda, cliente_id))
                            logger.info(f'Deuda del cliente {cliente} actualizada a {monto_final_deuda}.')
                        else:
                            logger.info(f'Deuda del cliente {cliente} tiene saldo negativo.')
                    else:
                        logger.warning(f'No se encontró deuda para el cliente {cliente_id}.')

                    for producto, cantidad in detalles_venta:
                        # Actualiza el inventario sumando de nuevo las cantidades que se vendieron
                        cursor.execute('UPDATE Inventario SET CANTIDAD = CANTIDAD + ? WHERE PRODUCTO = ?', (cantidad, producto))
                        logger.info(f'Inventario actualizado: Producto {producto}, cantidad restituida {cantidad}')

                except Exception as e:
                    db.rollback()  # Deshacer cualquier cambio en caso de error
                    logger.error(f'Error al eliminar la venta o actualizar la deuda: {e}')
                    flash('Ocurrió un error al eliminar la venta o actualizar la deuda', 'error')
                    return '', 500

                db.commit()
                flash('Venta y factura eliminadas correctamente', 'success')
            else:
                flash('Factura no encontrada para la venta', 'error')
                logger.error(f'Factura no encontrada para la venta {numero_venta}.')
        else:
            flash('La venta no existe', 'error')
            logger.error(f'La venta con número {numero_venta} no existe.')

    except Exception as e:
        logger.error(f'Ocurrió un error general al intentar eliminar la venta: {e}')
        flash('Ocurrió un error al eliminar la venta', 'error')
    
    finally:
        db.close()

    return '', 200

@historial_ventas_bp.route('/eliminar_producto/<int:numero_venta>/<int:id>', methods=['POST'])
def eliminar_producto(numero_venta, id):
    try:
        logger.info(f'Intentando eliminar producto con id {id} de la venta {numero_venta}')
        
        db = get_db()
        cursor = db.cursor()

        # Verificar si el producto existe dentro de la venta
        cursor.execute('SELECT * FROM Ventas WHERE numero_venta = ? AND id = ?', (numero_venta, id))
        producto = cursor.fetchone()

        if producto:
            precio = producto[5]
            cantidad = producto[4]
            nombre_producto = producto[3]
            monto_total_producto = precio * cantidad

            # Obtener datos de la factura
            cursor.execute('SELECT cliente_id, monto_total FROM Facturas WHERE numero_venta = ?', (numero_venta,))
            factura = cursor.fetchone()

            if factura:
                monto_total_factura = factura[1]
                cliente_id = int(factura[0])
                monto_final_factura = monto_total_factura - monto_total_producto

                # Obtener datos de la deuda
                cursor.execute('SELECT monto_total FROM Deudas WHERE cliente_id = ?', (cliente_id,))
                monto_total_deuda = cursor.fetchone()[0]
                monto_final_deuda = monto_total_deuda - monto_total_producto

                # Eliminar el producto de la venta y actualizar factura y deuda
                cursor.execute('DELETE FROM Ventas WHERE numero_venta = ? AND id = ?', (numero_venta, id))
                cursor.execute('UPDATE Deudas SET monto_total = ? WHERE cliente_id = ?', (monto_final_deuda, cliente_id))
                
                if monto_final_factura != 0:
                    cursor.execute('UPDATE Facturas SET monto_total = ? WHERE numero_venta = ?', (monto_final_factura, numero_venta))
                else:
                    cursor.execute('DELETE FROM Facturas WHERE numero_venta = ?', (numero_venta,))

                # Actualizar el inventario sumando de nuevo la cantidad eliminada
                cursor.execute('UPDATE Inventario SET CANTIDAD = CANTIDAD + ? WHERE PRODUCTO = ?', (cantidad, nombre_producto))
                logger.info(f'Inventario actualizado: Producto {nombre_producto}, cantidad restituida {cantidad}')

                
                db.commit()
                logger.info(f'Producto con id {id} eliminado de la venta {numero_venta}.')
                flash('Producto eliminado correctamente', 'success')
            else:
                logger.error(f'Factura no encontrada para el número de venta {numero_venta}.')
                flash('Factura no encontrada', 'error')
        else:
            logger.error(f'Producto con id {id} no encontrado en la venta {numero_venta}.')
            flash('El producto no existe', 'error')
    
    except Exception as e:
        logger.error(f'Ocurrió un error al eliminar el producto: {e}')
        flash('Ocurrió un error al eliminar el producto', 'error')
    
    return '', 200

@historial_ventas_bp.route('/actualizar_monto_pagado', methods=['POST'])
def actualizar_monto_pagado():
    logger = logging.getLogger(__name__)
    db = get_db()
    cursor = db.cursor()

    try:
        data = request.get_json()
        numero_venta = data['numero_venta']
        nuevo_monto_pagado = data['monto_pagado']

        # Validar que los datos sean correctos
        if not numero_venta or not isinstance(numero_venta, str):
            logger.error(f"Error: Número de venta inválido: {numero_venta}")
            return jsonify({'success': False, 'message': 'Número de venta inválido'}), 400

        if not isinstance(nuevo_monto_pagado, (int, float)):
            logger.error(f"Error: Monto pagado inválido: {nuevo_monto_pagado}")
            return jsonify({'success': False, 'message': 'Monto pagado inválido'}), 400

        # Convertir a float si es necesario
        nuevo_monto_pagado = float(nuevo_monto_pagado)

        # Verificar si la venta existe
        cursor.execute('SELECT * FROM Facturas WHERE numero_venta = ?', (numero_venta,))
        factura = cursor.fetchone()

        if not factura:
            logger.error(f"Error: No se encontró la factura con número de venta: {numero_venta}")
            return jsonify({'success': False, 'message': 'Factura no encontrada'}), 404

        # Actualizar el monto pagado en la base de datos
        cursor.execute('UPDATE Facturas SET monto_pagado = ? WHERE numero_venta = ?', (nuevo_monto_pagado, numero_venta))
        db.commit()
        logger.info(f"Monto pagado actualizado correctamente para la venta: {numero_venta}, nuevo monto: {nuevo_monto_pagado}")

        return jsonify({
            'success': True,
            'message': 'Monto pagado actualizado correctamente',
            'nuevo_monto_pagado': nuevo_monto_pagado
        }), 200

    except Exception as e:
        db.rollback()
        logger.error(f"Error al actualizar el monto pagado: {e}")
        return jsonify({'success': False, 'message': f'Error al actualizar el monto pagado: {str(e)}'}), 500

@historial_ventas_bp.route('/generar_nota_entrega', methods=['POST'])
def generar_nota_entrega():
    try:
        data = request.json
        numero_venta = data.get('numero_venta')

        datos_cliente = obtener_datos_cliente_y_venta(numero_venta)
        if not datos_cliente:
            logging.error('Cliente o venta no encontrado para el número de venta: %s', numero_venta)
            return jsonify({'mensaje': 'Cliente o venta no encontrado'}), 404

        ruta_nota = crear_nota_entrega(datos_cliente)
        return jsonify({"message": "Nota de entrega generada", "ruta": ruta_nota}), 200

    except Exception as e:
        logging.error('Error al generar la nota de entrega: %s', e, exc_info=True)
        return jsonify({'error': 'Error interno del servidor'}), 500

def abrir_libro_excel(ruta_archivo):
    try:
        return load_workbook(ruta_archivo)
    except Exception as e:
        logging.error('Error al abrir el libro de Excel: %s', e, exc_info=True)
        raise

def obtener_datos_cliente_y_venta(numero_venta):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT cliente FROM Ventas WHERE numero_venta = ?", (numero_venta,))
        cliente = cursor.fetchone()
        if not cliente:
            return None
        
        nombre_cliente = cliente[0]

        cursor.execute("SELECT razon_social, rif_cedula, direccion, telefono FROM Clientes WHERE nombre_cliente = ?", (nombre_cliente,))
        cliente = cursor.fetchone()
        if not cliente:
            return None
        
        razon_social, rif_cedula, direccion, telefono = cliente
        
        cursor.execute("SELECT numero_venta, producto, cantidad, precio, fecha FROM Ventas WHERE numero_venta = ?", (numero_venta,))
        productos = cursor.fetchall()  # Obtener todas las ventas asociadas

        if productos:
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
                'ventas': ventas_list
            }
        else:
            return {'error': 'No se encontró la venta'}

    except Exception as e:
        logging.error('Error al obtener datos del cliente y la venta: %s', e, exc_info=True)
        raise
    finally:
        db.close()

def insertar_direccion(sheet, direccion, fila_inicial):
    try:
        ancho_maximo = 80

        if len(direccion) > ancho_maximo:
            punto_corte = direccion.rfind(' ', 0, ancho_maximo)
            if punto_corte == -1:
                punto_corte = ancho_maximo

            direccion_1 = direccion[:punto_corte]
            direccion_2 = direccion[punto_corte + 1:]

            rango_celda_1 = sheet.Cells(fila_inicial, 6).MergeArea
            rango_celda_1.Cells(1, 1).Value = direccion_1

            rango_celda_2 = sheet.Cells(fila_inicial + 1, 6).MergeArea
            rango_celda_2.Cells(1, 1).Value = direccion_2
        else:
            rango_celda_1 = sheet.Cells(fila_inicial, 6).MergeArea
            rango_celda_1.Cells(1, 1).Value = direccion
    except Exception as e:
        logging.error('Error al insertar dirección en la hoja de Excel: %s', e, exc_info=True)
        raise

def crear_nota_entrega(datos_cliente):
    logging.info("Iniciando la creación de la nota de entrega...")

    ruta_plantilla, ruta_guardar = config_global()

    try:
        pythoncom.CoInitialize()
        logging.info("COM de Python inicializada correctamente.")

        if not os.path.exists(ruta_plantilla):
            raise FileNotFoundError(f"La plantilla no se encontró en la ruta: {ruta_plantilla}")

        try:
            excel = win32.DispatchEx('Excel.Application')
            logging.info("Excel iniciado correctamente.")
        except Exception as e:
            logging.error('Error al iniciar Excel: %s', e, exc_info=True)
            raise

        if excel is None:
            raise RuntimeError("No se pudo iniciar Excel. Asegúrate de que esté instalado correctamente.")

        try:
            workbook = excel.Workbooks.Open(ruta_plantilla)
            logging.info("Plantilla de Excel abierta correctamente.")
        except Exception as e:
            logging.error('Error al abrir la plantilla de Excel: %s', e, exc_info=True)
            raise

        try:
            sheet = workbook.ActiveSheet
            logging.info("Hoja activa seleccionada correctamente.")

            sheet.Cells(3, 9).Value = datos_cliente['razon_social']
            sheet.Cells(3, 29).Value = datos_cliente['rif_cedula']
            logging.info("Datos del cliente (razón social y RIF/Cédula) insertados correctamente.")
            
            insertar_direccion(sheet, datos_cliente['direccion'], 5)
            logging.info("Dirección del cliente insertada correctamente.")
            
            sheet.Cells(7, 29).Value = datos_cliente['telefono']
            logging.info("Teléfono del cliente insertado correctamente.")

            if datos_cliente['ventas']:
                primer_producto = datos_cliente['ventas'][0]
                sheet.Cells(7, 7).Value = primer_producto['fecha']
                sheet.Cells(1, 32).Value = primer_producto['numero_venta']

            fila_inicio = 12
            for producto in datos_cliente['ventas']:
                sheet.Cells(fila_inicio, 1).Value = producto['cantidad']
                sheet.Cells(fila_inicio, 4).Value = producto['producto']
                sheet.Cells(fila_inicio, 25).Value = producto['precio']
                fila_inicio += 1
            logging.info("Datos de todos los productos insertados correctamente.")

        except Exception as e:
            logging.error('Error al modificar la hoja activa: %s', e, exc_info=True)
            raise

        try:
            nombre_archivo = f"NDE.{primer_producto['numero_venta']}_{datos_cliente['nombre_cliente']}.xlsx"
            ruta_completa = os.path.join(ruta_guardar, nombre_archivo)
            workbook.SaveAs(ruta_completa)
            workbook.Close()
            logging.info("Archivo guardado correctamente en: %s", ruta_completa)
        except Exception as e:
            logging.error('Error al guardar el archivo: %s', e, exc_info=True)
            raise

        try:
            os.startfile(ruta_completa)
            logging.info("Archivo %s abierto correctamente.", nombre_archivo)
        except Exception as e:
            logging.error('Error al abrir el archivo guardado: %s', e, exc_info=True)
            raise

        logging.info("Proceso de creación de la nota de entrega completado.")
        return ruta_completa

    except Exception as e:
        logging.error('Se encontró un error: %s', e, exc_info=True)
        raise