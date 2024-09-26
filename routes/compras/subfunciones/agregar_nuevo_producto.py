# routes/agregar_stock.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from ...database2 import get_db

agregar_nuevo_producto_bp = Blueprint('agregar_nuevo_producto', __name__)

@agregar_nuevo_producto_bp.route('/agregar_nuevo_producto')
def agregar_nuevo_producto():
    return render_template('/compras/agregar_nuevo_producto.html')
