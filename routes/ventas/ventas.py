#routes/ventas/ventas.py
from flask import Blueprint, render_template
from .subfunciones.nueva_venta import nueva_venta_bp
from .subfunciones.historial_ventas import historial_ventas_bp

ventas_bp = Blueprint('ventas', __name__)  
ventas_bp.register_blueprint(nueva_venta_bp, url_prefix='/nueva_venta')
ventas_bp.register_blueprint(historial_ventas_bp, url_prefix='/historial_ventas')

@ventas_bp.route('/ventas')
def ventas():
    return render_template('/ventas/ventas.html')