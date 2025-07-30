from flask import Blueprint, render_template

add_new_product_bp = Blueprint('add_product', __name__)

@add_new_product_bp.route('/add_product')
def add_new_product():
    return render_template('purchases/add_new_product.html')
