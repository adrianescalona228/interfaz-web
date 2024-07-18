# routes/manejar_credito.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash


manejar_credito_bp = Blueprint('manejar_credito', __name__)

@manejar_credito_bp.route('/manejar_credito')
def manejar_credito():
    return render_template('manejar_credito.html')