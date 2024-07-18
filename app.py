import sqlite3  
from flask import Flask, render_template, g, request, redirect, flash, url_for,jsonify
from urllib.parse import quote

DATABASE = '/home/apolito/Programacion/Proyectos/interfaz_web/DATABASE/inventory.db'
app = Flask(__name__)
def cargar_clave_secreta():
    clave_secreta = None
    with open('/home/apolito/.query.txt', 'r') as f:
        clave_secreta = f.read().strip()
    return clave_secreta

app.config['SECRET_KEY'] = cargar_clave_secreta()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row

    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agregar_stock')
def agregar_stock():
    return render_template('agregar_stock.html')

@app.route('/sumar_stock', methods=['GET', 'POST'])
def sumar_stock():
    if request.method == 'POST':
        producto = request.form.get('producto')
        cantidad = float(request.form.get('cantidad', 0))  # Convertir cantidad a float
        
        db = get_db()
        cursor = db.execute('SELECT * FROM Inventario WHERE PRODUCTO LIKE ?', ('%' + producto + '%',))
        existing_product = cursor.fetchone()

        if existing_product:
            new_cantidad = float(existing_product['CANTIDAD']) + cantidad
            db.execute('UPDATE Inventario SET CANTIDAD = ? WHERE PRODUCTO = ?', (new_cantidad, existing_product['PRODUCTO']))
            db.commit()
            flash('Stock actualizado correctamente', 'success')
        else:
            flash('El producto no existe en el inventario', 'error')

        return redirect(url_for('sumar_stock'))

    return render_template('sumar_stock.html')

@app.route('/autocomplete', methods=['GET'])
def autocomplete():
    term = request.args.get('term', '')
    db = get_db()
    cursor = db.execute('SELECT PRODUCTO FROM Inventario WHERE PRODUCTO LIKE ?', ('%' + term + '%',))
    products = [row['PRODUCTO'] for row in cursor.fetchall()]
    return jsonify(products)

# Ruta para renderizar el formulario de ventas
@app.route('/nueva_venta')
def nueva_venta():
    return render_template('formulario_venta.html')

# Ruta para obtener datos de autocompletado de clientes
@app.route('/autocompletar_clientes', methods=['GET'])
def autocompletar_clientes():
    term = request.args.get('term', '')
    
    # Conexión a la base de datos y consulta
    db = get_db()
    cursor = db.execute('SELECT nombre_cliente FROM Clientes WHERE nombre_cliente LIKE ?', ('%' + term + '%',))
    clientes = [row['nombre_cliente'] for row in cursor.fetchall()]
    
    return jsonify(clientes)

# Ruta para obtener datos de autocompletado de productos
@app.route('/autocompletar_productos', methods=['GET'])
def autocompletar_productos():
    term = request.args.get('term', '')
    
    # Conexión a la base de datos y consulta
    db = get_db()
    cursor = db.execute('SELECT PRODUCTO, PRECIO FROM Inventario WHERE PRODUCTO LIKE ?', ('%' + term + '%',))
    
    # Recoger resultados y formatearlos en un formato JSON adecuado
    productos = [{'label': row['PRODUCTO'], 'value': row['PRODUCTO'], 'precio': row['PRECIO']} for row in cursor.fetchall()]
    
    return jsonify(productos)

# Ruta para procesar el formulario de ventas
@app.route('/procesar_venta', methods=['POST'])
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
    db.commit()

    return redirect(url_for('procesar_venta'))

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
@app.route('/obtener_ultimo_numero_venta', methods=['GET'])
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

@app.route('/verificar_numero_venta', methods=['POST'])
def verificar_numero_venta():
    numero_venta = request.form.get('numero_venta')
    
    db = get_db()
    cursor = db.execute('SELECT COUNT(*) AS count FROM Ventas WHERE numero_venta = ?', (numero_venta,))
    result = cursor.fetchone()
    count = result['count']
    
    # Devolver si el número de venta existe o no
    return jsonify({'existe': count > 0})

@app.route('/historial_ventas')
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

@app.route('/eliminar_venta/<int:numero_venta>', methods=['POST'])
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

    return redirect(url_for('historial_ventas'))

# Ruta para eliminar un producto de una venta específica
@app.route('/eliminar_producto/<int:numero_venta>/<nombre_producto>', methods=['POST'])
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

@app.route('/crear_notas_entrega')
def crear_notas_entrega():
    return render_template('crear_notas_entrega.html')

@app.route('/manejar_credito')
def manejar_credito():
    return render_template('manejar_credito.html')

@app.route('/enviar_mensajes')
def enviar_mensajes():
    return render_template('enviar_mensajes.html')

@app.route('/mostrar_inventario')
def mostrar_inventario():
    db = get_db()   
    cursor = db.execute('SELECT * FROM inventario')
    inventario = cursor.fetchall()
    return render_template('mostrar_inventario.html', inventario=inventario)



if __name__ == '__main__':
    app.run(debug=True)
