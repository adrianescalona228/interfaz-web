# routes/crear_notas_entrega.py
from flask import Blueprint, request, jsonify, send_file, render_template, redirect, url_for
import openpyxl
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import io
import os
from .database import get_db

crear_notas_entrega_bp = Blueprint('crear_notas_entrega', __name__)
ruta_libro = '/home/apolito/Programacion/Proyectos/interfaz_web/DATABASE/NDE_PLANTILLA.xlsx'
#ruta_libro = r"C:\Trabajo\Notas_de_entrega"


@crear_notas_entrega_bp.route('/generar_nota_entrega', methods=['GET', 'POST'])
def generar_nota_entrega():
    if request.method == 'POST':
        numero_venta = request.form.get('numero_venta')
        datos_cliente = obtener_datos_cliente_y_venta(numero_venta)
        
        if not datos_cliente:
            return jsonify({'mensaje': 'Cliente o venta no encontrado'}), 404
           
        libro = abrir_libro_excel(ruta_libro)
        ruta_archivo = crear_nota_entrega(libro, datos_cliente)
        
        # Aquí puedes redirigir a una página de éxito o simplemente renderizar una plantilla de confirmación
        return render_template('crear_notas_entrega.html', ruta_archivo=ruta_archivo)
    else:
        return render_template('crear_notas_entrega.html')
    
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
    
    # Obtener ventas asociadas al número de venta específico
    cursor.execute("SELECT numero_venta, producto, cantidad, precio, fecha FROM Ventas WHERE numero_venta = ?", (numero_venta,))
    ventas = cursor.fetchall()
    
    db.close()
    
    return {
        'nombre_cliente': nombre_cliente,
        'razon_social': razon_social,
        'rif_cedula': rif_cedula,
        'direccion': direccion,
        'telefono': telefono,
        'ventas': [
            {'numero_venta': numero_venta, 'producto': producto, 'cantidad': cantidad, 'precio': precio, 'fecha': fecha}
            for numero_venta, producto, cantidad, precio, fecha in ventas
        ]
    }

def crear_nota_entrega(libro, datos_cliente):
    hoja = libro.active  # Supongamos que la plantilla usa la hoja activa
    
    # Insertar datos del cliente
    hoja['I3'] = datos_cliente['razon_social']
    hoja['AC3'] = datos_cliente['rif_cedula']
    hoja['F5'] = datos_cliente['direccion']
    hoja['AC7'] = datos_cliente['telefono']

    # Obtener fecha y número de venta del primer elemento en las ventas
    if datos_cliente['ventas']:
        primer_venta = datos_cliente['ventas'][0]
        hoja['G7'] = primer_venta['fecha']
        hoja['AF1'] = primer_venta['numero_venta']

    # Insertar datos de las ventas
    fila_inicio = 12  # Supongamos que comenzamos a escribir las ventas en la fila 7
    for venta in datos_cliente['ventas']:   
            hoja[f'D{fila_inicio}'] = venta['producto']
            hoja[f'A{fila_inicio}'] = venta['cantidad']
            hoja[f'Y{fila_inicio}'] = venta['precio']
            fila_inicio += 1
    
    # Definir la ruta de guardado
    #ruta_guardar = "home/apolito/Programacion/Proyectos/interfaz_web/DATABASE/Notas_de_entrega"
    ruta_guardar = "/mnt/c/Trabajo/Notas_de_entrega"
    if not os.path.exists(ruta_guardar):
        os.makedirs(ruta_guardar)
    
    # Crear el nombre del archivo
    nombre_archivo = f"NDE_{primer_venta['numero_venta']}_{datos_cliente['nombre_cliente']}.xlsx"
    
    # Ruta completa
    ruta_completa = os.path.join(ruta_guardar, nombre_archivo)
    
    # Guardar archivo
    libro.save(ruta_completa)
    
    return ruta_completa