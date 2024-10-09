#/routes/graficas/graficas.py
from flask import Blueprint, render_template, jsonify, request
from ..database2 import get_db
import pandas as pd
from datetime import datetime, timedelta

graficas_bp = Blueprint('graficas', __name__)

# Plantilla HTML
@graficas_bp.route('/graficas_template', methods=['GET'])
def graficas_template():
    return render_template('graficas/graficas.html')


# Función para obtener ventas totales por producto (ya la teníamos)
def grafica_total_vendidos(start_date, categoria):
    db = get_db()
    query = """
    SELECT i.PRODUCTO, COALESCE(SUM(v.cantidad), 0) AS total_vendido
    FROM inventario i
    LEFT JOIN Ventas v ON i.PRODUCTO = v.producto AND v.fecha >= ?
    WHERE (? IS NULL OR i.TIPO_DE_PRODUCTO = ?) AND i.PRODUCTO != 'OTRO'
    GROUP BY i.PRODUCTO
    ORDER BY total_vendido DESC
    """
    params = (start_date, categoria, categoria) if categoria else (start_date, None, None)
    df = pd.read_sql_query(query, db, params=params)
    # db.close()
    return df.to_dict(orient='records')


# Función para obtener ventas por fecha (nueva gráfica)
def grafica_ventas_tiempo(start_date):
    # print('hola')
    db = get_db()
    query = """
    SELECT v.fecha, SUM(v.cantidad) AS total_ventas
    FROM Ventas v
    WHERE v.fecha >= ?
    GROUP BY v.fecha
    ORDER BY v.fecha
    """
    params = (start_date,)
    df = pd.read_sql_query(query, db, params=params)
    print(df)
    # db.close()
    return df.to_dict(orient='records')


# Función para filtrar productos de bajo vendido
def grafica_bajo_vendido(df, umbral=10):
    df_bajo_vendido = df[df['total_vendido'] < umbral]
    return df_bajo_vendido.to_dict(orient='records'), df_bajo_vendido.shape[0]


# Endpoint principal que llama a múltiples funciones de gráficas
@graficas_bp.route('/graficas')
def graficas():
    try:
        rango_dias = request.args.get('rango', default=14, type=int)
        categoria = request.args.get('categoria', default=None, type=str)
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=rango_dias)

        print(f"Rango de días: {rango_dias}, Categoría: {categoria}")
        
        # Llamar a las funciones para obtener los datos de varias gráficas
        total_vendidos = grafica_total_vendidos(start_date, categoria)  # Gráfica 1
        print("Total vendidos obtenidos")

        ventas_tiempo = grafica_ventas_tiempo(start_date)  # Gráfica 2
        print("Ventas por tiempo obtenidas")

        # Filtrar los productos de bajo vendido usando el resultado de total_vendidos
        bajo_vendido, numero_bajo_vendido = grafica_bajo_vendido(pd.DataFrame(total_vendidos))
        print(f"Bajo vendido: {numero_bajo_vendido} productos")

        # Devolver todas las gráficas en un solo JSON
        return jsonify({
            'total_vendidos': total_vendidos,  # Gráfica de productos vendidos
            'ventas_tiempo': ventas_tiempo,    # Gráfica de ventas a lo largo del tiempo
            'bajo_vendido': bajo_vendido,      # Productos de bajo vendido
            'numero_bajo_vendido': numero_bajo_vendido
        })

    except Exception as e:
        print(f"Error en el servidor en /graficas: {str(e)}")
        return jsonify({'error': str(e)}), 500

