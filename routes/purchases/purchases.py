#routes/compras/compras.py
from flask import Blueprint, render_template
from .subfunctions.add_product import add_new_product_bp
from .subfunctions.purchase_stock import purchase_stock_bp
from .subfunctions.purchase_history import purchase_history_bp

purchases_bp = Blueprint('purchases', __name__)
purchases_bp.register_blueprint(add_new_product_bp, url_prefix='/new_product')
purchases_bp.register_blueprint(purchase_stock_bp, url_prefix='/purchase_stock')
purchases_bp.register_blueprint(purchase_history_bp, url_prefix='/purchase_history')

@purchases_bp.route('/purchases')
def purchases():
    return render_template('/purchases/purchases.html')
