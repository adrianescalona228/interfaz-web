#routes/compras/compras.py
from flask import Blueprint, render_template
from .subfunciones.ver_inventario import ver_inventario_bp
from .subfunciones.registar_producto_nuevo import registrar_producto_nuevo_bp

inventario_bp = Blueprint('inventario', __name__)
inventario_bp.register_blueprint(ver_inventario_bp, url_prefix='/ver_inventario')
inventario_bp.register_blueprint(registrar_producto_nuevo_bp, url_prefix='/registrar_producto_nuevo')

@inventario_bp.route('/inventario')
def inventario():
    return render_template('/inventario/inventario.html')