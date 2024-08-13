# routes/agregar_stock.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database import get_db

agregar_clientes_nuevos_bp = Blueprint('agregar_clientes_nuevos', __name__)

@agregar_clientes_nuevos_bp.route('/agregar_clientes_nuevos')
def agregar_clientes_nuevos():
    return render_template('/clientes/agregar_clientes_nuevos.html')