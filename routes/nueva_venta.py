# routes/nueva_venta.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from .database import get_db

nueva_venta_bp = Blueprint('nueva_venta', __name__)


# Ruta para procesar el formulario de ventas
@nueva_venta_bp.route('/procesar_venta', methods=['POST'])
def procesar_venta():
    cliente = request.form.get('cliente')
    producto = request.form.get('producto')
    cantidad = request.form.get('cantidad')
    fecha = request.form.get('fecha')
    numero_venta = request.form.get('numero_venta')
    
    # Validar si el número de venta ya existe en la base de datos
    if venta_existe(numero_venta):
        return 'Error: El número de venta ya existe en la base de datos. No se puede registrar.'

    # Lógica para obtener precio y costo desde el inventario
    db = get_db()
    cursor = db.cursor()
    
    # Obtener precio y costo del producto desde el inventario
    cursor.execute('SELECT precio, costo FROM Inventario WHERE producto = ?', (producto,))
    result = cursor.fetchone()
    
    if result:
        precio = result['precio']
        costo = result['costo']
    else:
        # Manejo de errores si el producto no existe en el inventario
        return 'Error: El producto no existe en el inventario'
    
    # Obtener el ID del cliente
    cursor.execute('SELECT id FROM Clientes WHERE nombre_cliente = ?', (cliente,))
    cliente_id = cursor.fetchone()['id']
    
    # Insertar datos en la tabla Ventas
    cursor.execute('INSERT INTO Ventas (numero_venta, cliente, producto, cantidad, precio, costo, fecha) VALUES (?, ?, ?, ?, ?, ?, ?)',
                (numero_venta, cliente, producto, cantidad, precio, costo, fecha))
    
    # Actualizar stock después de registrar la venta
    if not actualizar_stock(producto, cantidad):
        print("no se pudo, rey")
        return f'Error: No se pudo actualizar el stock para el producto {producto}'

    db.commit()

    return redirect(url_for('procesar_venta'))


# Ruta para renderizar el formulario de ventas
@nueva_venta_bp.route('/nueva_venta')
def nueva_venta():
    return render_template('formulario_venta.html')

@nueva_venta_bp.route('/autocomplete', methods=['GET'])
def autocomplete():
    term = request.args.get('term', '')
    db = get_db()
    cursor = db.execute('SELECT PRODUCTO FROM Inventario WHERE PRODUCTO LIKE ?', ('%' + term + '%',))
    products = [row['PRODUCTO'] for row in cursor.fetchall()]
    return jsonify(products)

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
    cursor = db.execute('SELECT PRODUCTO, PRECIO FROM Inventario WHERE PRODUCTO LIKE ?', ('%' + term + '%',))
    
    # Recoger resultados y formatearlos en un formato JSON adecuado
    productos = [{'label': row['PRODUCTO'], 'value': row['PRODUCTO'], 'precio': row['PRECIO']} for row in cursor.fetchall()]
    
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

@nueva_venta_bp.route('/verificar_numero_venta', methods=['POST'])
def verificar_numero_venta():
    numero_venta = request.form.get('numero_venta')
    
    db = get_db()
    cursor = db.execute('SELECT COUNT(*) AS count FROM Ventas WHERE numero_venta = ?', (numero_venta,))
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
