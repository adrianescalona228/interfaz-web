# routes/ventas/subfunciones/nueva_venta.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db
from datetime import datetime, timedelta
import json 

nueva_venta_bp = Blueprint('nueva_venta', __name__)

# Ruta para renderizar el formulario de ventas
@nueva_venta_bp.route('/nueva_venta')
def nueva_venta():
    return render_template('/ventas/formulario_venta.html')

@nueva_venta_bp.route('/procesar_venta', methods=['POST'])
def procesar_venta():
    data = request.get_json()

    cliente = data.get('cliente')
    numero_venta = data.get('numero_venta')
    fecha = data.get('fecha')
    productos = data.get('productos')

    if not productos:
        return 'Error: No se recibieron productos'

    print(f'Datos recibidos: {productos}')

    if venta_existe(numero_venta):
        return 'Error: El número de venta ya existe en la base de datos. No se puede registrar.'

    db = get_db()
    cursor = db.cursor()

    for producto in productos:
        try:
            nombre_producto = producto['producto']
            cantidad = float(producto['cantidad'].replace(',', '.'))  # Convertir coma a punto
            precio = float(producto['precio'].replace(',', '.'))  # Asegurarse de que el precio sea correcto

            print(f'Procesando producto: {nombre_producto}, Cantidad: {cantidad}, Precio: {precio}')

            cursor.execute('SELECT costo FROM Inventario WHERE producto = ?', (nombre_producto,))
            result = cursor.fetchone()

            if result:
                costo = result['costo']
                print(f'Costo obtenido para {nombre_producto}: {costo}')
            else:
                print(f"Error: El producto {nombre_producto} no existe en el inventario")
                return f'Error: El producto {nombre_producto} no existe en el inventario'

            cursor.execute('INSERT INTO Ventas (numero_venta, cliente, producto, cantidad, precio, costo, fecha) VALUES (?, ?, ?, ?, ?, ?, ?)',
                           (numero_venta, cliente, nombre_producto, cantidad, precio, costo, fecha))
            print(f'Producto {nombre_producto} insertado correctamente en la tabla Ventas')

            if not actualizar_stock(nombre_producto, cantidad):
                print(f"Error: No se pudo actualizar el stock para el producto {nombre_producto}")
                return f'Error: No se pudo actualizar el stock para el producto {nombre_producto}'

        except Exception as e:
            print(f"Error al procesar el producto {nombre_producto}: {e}")
            return f"Error al procesar el producto {nombre_producto}: {e}"

    db.commit()
    db.close()

    return f'Venta procesada correctamente para el número de venta {numero_venta}'

@nueva_venta_bp.route('/actualizar_deuda', methods=['POST'])
def actualizar_deuda():
    data = request.json
    numero_venta = data['numero_venta']

    db = get_db()
    cursor = db.cursor()

    # Verificar si existe una factura para ese numero_venta
    cursor.execute('SELECT cliente_id, monto_total FROM Facturas WHERE numero_venta = ?', (numero_venta,))
    factura = cursor.fetchone()

    if factura:
        cliente_id = factura[0]
        monto_total = factura[1]

        print(cliente_id, monto_total)

        # Actualizar la tabla Deudas
        cursor.execute('SELECT monto_total FROM Deudas WHERE cliente_id = ?', (cliente_id,))
        deuda_actual = cursor.fetchone()['monto_total']
        # print(deuda_actual)

        nuevo_monto_total = deuda_actual + float(monto_total)
        # print(nuevo_monto_total)
        cursor.execute('UPDATE Deudas SET monto_total = ? WHERE cliente_id = ?', (nuevo_monto_total, cliente_id))

        db.commit()
    else:
        print('Factura no encontrada para el número de venta:', numero_venta)

    db.close()

    return "Deuda actualizada correctamente"

@nueva_venta_bp.route('/crear_factura', methods=['POST'])
def crear_factura():
    data = request.json
    fecha = data['fecha']
    numero_venta = data['numero_venta']
    cliente = data['cliente']
    monto_total = data['monto_total']
    
    db = get_db()
    cursor = db.cursor()

    # Obtener el ID del cliente
    cursor.execute('SELECT id FROM Clientes WHERE nombre_cliente = ?', (cliente,))
    cliente_id = cursor.fetchone()['id']

    # Crear la factura solo si no existe para esa venta
    cursor.execute('SELECT id FROM Facturas WHERE numero_venta = ?', (numero_venta,))
    factura = cursor.fetchone()

    if not factura:
        # Insertar datos en la tabla Facturas
        fecha_emision = datetime.strptime(fecha, '%Y-%m-%d')
        fecha_vencimiento = fecha_emision + timedelta(days=15)
        
        cursor.execute('INSERT INTO Facturas (numero_venta, cliente_id, monto_total, fecha_emision, fecha_vencimiento) VALUES (?, ?, ?, ?, ?)',
                       (numero_venta, cliente_id, monto_total, fecha_emision.strftime('%Y-%m-%d'), fecha_vencimiento.strftime('%Y-%m-%d')))
        db.commit()  # Asegura que los cambios se guarden en la base de datos

    db.close()  # Cierra la conexión a la base de datos

    return 'Factura creada correctamente'

@nueva_venta_bp.route('/reset', methods=['POST'])
def reset():
    db = get_db()
    cursor = db.cursor()

    monto = 15
    id = 1
    cursor.execute('UPDATE Deudas SET monto_total = ? WHERE cliente_id = ?', (monto, id))

    # numero_venta = 1
    # cursor.execute('DELETE FROM Facturas WHERE numero_venta = ?', (numero_venta,))

    db.commit()
    db.close()

    return f'id del reset: {id}'

# Ruta para obtener datos de autocompletado de clientes
@nueva_venta_bp.route('/autocompletar_clientes', methods=['GET'])
def autocompletar_clientes():
    term = request.args.get('term', '')
    
    # Conexión a la base de datos y consulta
    db = get_db()
    cursor = db.execute('SELECT nombre_cliente FROM Clientes WHERE nombre_cliente LIKE ?', ('%' + term + '%',))
    clientes = [row['nombre_cliente'] for row in cursor.fetchall()]
    
    return jsonify(clientes)

# Ruta para obtener datos de autocompletado de productos
@nueva_venta_bp.route('/autocompletar_productos', methods=['GET'])
def autocompletar_productos():
    term = request.args.get('term', '')
    
    # Conexión a la base de datos y consulta
    db = get_db()
    cursor = db.execute('SELECT PRODUCTO, PRECIO, COSTO FROM Inventario WHERE PRODUCTO LIKE ?', ('%' + term + '%',))
    
    # Recoger resultados y formatearlos en un formato JSON adecuado
    productos = [{'label': row['PRODUCTO'], 'value': row['PRODUCTO'], 'precio': row['PRECIO'], 'costo': row['COSTO']} for row in cursor.fetchall()]
    
    return jsonify(productos)

def venta_existe(numero_venta):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM Ventas WHERE numero_venta = ?', (numero_venta,))
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
        return False

@nueva_venta_bp.route('/obtener_ultimo_numero_venta', methods=['GET'])
def obtener_ultimo_numero_venta():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT MAX(numero_venta) as ultimo_numero FROM Ventas')
    result = cursor.fetchone()
    ultimo_numero = result['ultimo_numero']
    
    if ultimo_numero is None:
        return jsonify({'ultimo_numero': 1})  # Si no hay ventas, empezar desde 1
    else:
        return jsonify({'ultimo_numero': ultimo_numero + 1})

from flask import request, jsonify

@nueva_venta_bp.route('/verificar_numero_venta', methods=['POST'])
def verificar_numero_venta():
    data = request.get_json()  # Obtiene los datos en formato JSON
    numero_venta = data.get('numero_venta')
    
    db = get_db()
    cursor = db.execute('SELECT COUNT(*) AS count FROM Facturas WHERE numero_venta = ?', (numero_venta,))

    result = cursor.fetchone()
    count = result['count']
    
    # Devolver si el número de venta existe o no
    return jsonify({'existe': count > 0})

def actualizar_stock(producto, cantidad_vendida):
    db = get_db()
    cursor = db.cursor()

    cursor.execute('SELECT cantidad FROM Inventario WHERE producto = ?', (producto,))
    result = cursor.fetchone()

    if result:

        cantidad_actual = result['cantidad']

        # Intentar convertir las cantidades a enteros
        try:
            cantidad_actual = float(cantidad_actual)
            cantidad_vendida = float(cantidad_vendida)
        except ValueError:
            # Manejo de error si la conversión falla
            return False

        nueva_cantidad = cantidad_actual - cantidad_vendida
        cursor.execute('UPDATE Inventario SET cantidad = ? WHERE producto = ?', (nueva_cantidad, producto))
        db.commit()
        return True
    else:
        return False
