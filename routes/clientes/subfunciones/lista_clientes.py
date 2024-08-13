# routes/agregar_stock.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

lista_clientes_bp = Blueprint('lista_clientes', __name__)

@lista_clientes_bp.route('/lista_clientes')
def lista_clientes():
    db = get_db()   
    cursor = db.execute('SELECT * FROM Clientes')
    clientes = cursor.fetchall()
    return render_template('/clientes/lista_clientes.html', clientes=clientes)

