# routes/agregar_stock.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

agregar_clientes_nuevos_bp = Blueprint('agregar_clientes_nuevos', __name__)

@agregar_clientes_nuevos_bp.route('/agregar_clientes_nuevos')
def agregar_clientes_nuevos():
    return render_template('/clientes/agregar_clientes_nuevos.html')

@agregar_clientes_nuevos_bp.route('/guardar_cliente', methods=['POST'])
def guardar_cliente():
    try:
        data = request.get_json()
        print(data)
        # Obtén los datos del formulario
        nombre = request.json.get('nombre')
        razon_social = request.json.get('razon_social')
        rif_cedula = request.json.get('rif_cedula')
        direccion = request.json.get('direccion')
        telefono = request.json.get('telefono')
        
        db = get_db()
        cursor = db.cursor()

        # Insertar los datos en la tabla Clientes
        cursor.execute('''
            INSERT INTO Clientes (nombre_cliente, razon_social, rif_cedula, direccion, telefono)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, razon_social, rif_cedula, direccion, telefono))

        db.commit()
        db.close()

        # Responder con éxito
        response_data = {
            'success': True,
            'message': 'Cliente agregado correctamente',
            'data': {
                'nombre': nombre,
                'razon_social': razon_social,
                'rif_cedula': rif_cedula,
                'direccion': direccion,
                'telefono': telefono
            }
        }
        return jsonify(response_data)

    except Exception as e:
        # Manejo de errores
        cursor.rollback()  # Deshacer cambios en caso de error
        db.close()
        response_data = {
            'success': False,
            'message': str(e)
        }
        return jsonify(response_data)
