# routes/automatizar_mensajes.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash


automatizar_mensajes_bp = Blueprint('automatizar_mensajes', __name__)

@automatizar_mensajes_bp.route('/enviar_mensajes')
def enviar_mensajes():
    return render_template('enviar_mensajes.html')
