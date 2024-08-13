#routes/compras/compras.py
from flask import Blueprint, render_template
from .subfunciones.agregar_nuevo_producto import agregar_nuevo_producto_bp
from .subfunciones.comprar_stock import comprar_stock_bp

compras_bp = Blueprint('compras', __name__)
compras_bp.register_blueprint(agregar_nuevo_producto_bp, url_prefix='/agregar_stock')
compras_bp.register_blueprint(comprar_stock_bp, url_prefix='/comprar_stock')

@compras_bp.route('/compras')
def compras():
    return render_template('/compras/compras.html')