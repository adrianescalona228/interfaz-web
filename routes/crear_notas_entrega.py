# routes/crear_notas_entrega.py
from flask import Blueprint, request, jsonify, send_file, render_template
import openpyxl
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
import io
from .database import get_db

crear_notas_entrega_bp = Blueprint('crear_notas_entrega', __name__)
ruta_archivo = r"\\wsl.localhost\Ubuntu\home\apolito\Programacion\Proyectos\interfaz_web\DATABASE\prueba.xlsx"

@crear_notas_entrega_bp.route('/generar_nota_entrega', methods=['POST'])
def generar_nota_entrega():

    return render_template('crear_notas_entrega.html')

# def abrir_libro_excel(ruta_archivo):
#     return load_workbook(ruta_archivo)

# def obtener_datos_cliente_y_venta(nombre_cliente):
#     db =get_db()
#     cursor = db.cursor()

#     # Obtener datos del cliente
#     cursor.execute("SELECT razon_social, rif_cedula, direccion, telefono FROM Clientes WHERE nombre_cliente = ?", (nombre_cliente,))
#     cliente = cursor.fetchone()
#     if not cliente:
#         return None
    
#     razon_social, rif_cedula, direccion, telefono = cliente
    
#     # Obtener ventas asociadas
#     cursor.execute("SELECT numero_venta, producto, cantidad, precio, fecha FROM Ventas WHERE cliente = ?", (nombre_cliente,))
#     ventas = cursor.fetchall()
    
#     db.close()
    
#     return {
#         'nombre_cliente': nombre_cliente,
#         'razon_social': razon_social,
#         'rif_cedula': rif_cedula,
#         'direccion': direccion,
#         'telefono': telefono,
#         'ventas': [
#             {'numero_venta': numero_venta, 'producto': producto, 'cantidad': cantidad, 'precio': precio, 'fecha': fecha}
#             for numero_venta, producto, cantidad, precio, fecha in ventas
#         ]
#     }

# def crear_nota_entrega(libro, datos_cliente):
#     hoja = libro.active  # Supongamos que la plantilla usa la hoja activa
    
#     # Insertar datos del cliente
#     hoja['A1'] = datos_cliente['nombre_cliente']
#     hoja['A2'] = datos_cliente['razon_social']
#     hoja['A3'] = datos_cliente['rif_cedula']
#     hoja['A4'] = datos_cliente['direccion']
#     hoja['A5'] = datos_cliente['telefono']
    
#     # Insertar datos de las ventas
#     fila_inicio = 7  # Supongamos que comenzamos a escribir las ventas en la fila 7
#     for venta in datos_cliente['ventas']:
#         hoja[f'B{fila_inicio}'] = venta['numero_venta']
#         hoja[f'C{fila_inicio}'] = venta['producto']
#         hoja[f'D{fila_inicio}'] = venta['cantidad']
#         hoja[f'E{fila_inicio}'] = venta['precio']
#         hoja[f'F{fila_inicio}'] = venta['fecha']
#         fila_inicio += 1
    
#     # Guardar archivo
#     ruta_guardar = f"nota_entrega_{datos_cliente['nombre_cliente']}.xlsx"
#     libro.save(ruta_guardar)
#     return ruta_guardar
