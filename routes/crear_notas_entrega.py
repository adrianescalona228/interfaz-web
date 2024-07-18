# routes/crear_notas_entrega.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash


crear_notas_entrega_bp = Blueprint('crear_notas_entrega', __name__)

@crear_notas_entrega_bp.route('/crear_notas_entrega')
def crear_notas_entrega():
    return render_template('crear_notas_entrega.html')
