# routes/agregar_stock.py
import sqlite3
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from .database import get_db

agregar_stock_bp = Blueprint('agregar_stock', __name__)

@agregar_stock_bp.route('/agregar_stock')
def agregar_stock():
    return render_template('agregar_stock.html')
