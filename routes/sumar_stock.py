# routes/agregar_stock.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from .database import get_db

sumar_stock_bp = Blueprint('sumar_stock', __name__)

@sumar_stock_bp.route('/sumar_stock', methods=['GET', 'POST'])
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

