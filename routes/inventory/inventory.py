#routes/compras/compras.py
from flask import Blueprint, render_template
from .subfunctions.view_inventory import view_inventory_bp
from .subfunctions.register_new_product import register_product_bp

inventario_bp = Blueprint('inventory', __name__)
inventario_bp.register_blueprint(view_inventory_bp, url_prefix='/view_inventory')
inventario_bp.register_blueprint(register_product_bp, url_prefix='/register_new_product')

@inventario_bp.route('/inventory')
def inventory():
    return render_template('/inventory/inventory.html')
