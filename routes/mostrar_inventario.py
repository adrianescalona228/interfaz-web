# routes/mostrar_inventario.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from .database import get_db

mostrar_inventario_bp = Blueprint('mostrar_inventario', __name__)

@mostrar_inventario_bp.route('/mostrar_inventario')
def mostrar_inventario():
    db = get_db()   
    cursor = db.execute('SELECT * FROM inventario')
    inventario = cursor.fetchall()
    return render_template('mostrar_inventario.html', inventario=inventario)
