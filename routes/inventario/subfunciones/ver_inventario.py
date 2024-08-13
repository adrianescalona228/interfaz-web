# routes/mostrar_inventario.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

ver_inventario_bp = Blueprint('ver_inventario', __name__)

@ver_inventario_bp.route('/ver_inventario')
def ver_inventario():
    db = get_db()   
    cursor = db.execute('SELECT * FROM inventario')
    inventario = cursor.fetchall()
    return render_template('/inventario/ver_inventario.html', inventario=inventario)
