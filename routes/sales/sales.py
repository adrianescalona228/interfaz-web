#routes/ventas/ventas.py
from flask import Blueprint, render_template
from .subfunctions.new_sale import new_sale_bp
from .subfunctions.sale_history import sales_history_bp

sales_bp = Blueprint('sales', __name__)  
sales_bp.register_blueprint(new_sale_bp, url_prefix='/new_sale')
sales_bp.register_blueprint(sales_history_bp, url_prefix='/sales_history')

@sales_bp.route('/sales')
def sales():
    return render_template('/sales/sales.html')
