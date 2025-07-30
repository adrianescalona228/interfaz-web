# routes/products/register_product.py

import logging
from flask import Blueprint, render_template, request, jsonify
from database import db
from database.models import Product, Inventory

register_product_bp = Blueprint('register_product', __name__)

@register_product_bp.route('/register_product')
def register_product():
    logging.info("Rendering register product page.")
    return render_template('/inventory/register_new_product.html')

@register_product_bp.route('/save_product', methods=['POST'])
def save_product():
    data = request.json
    logging.info(f'Data received: {data}')

    try:
        name = data.get('product', '').strip().upper()
        price = float(data.get('price', 0))
        cost = float(data.get('cost', 0))
        brand_name = data.get('brand', '').strip()  # ahora es brand_name, no brand_id

        if not name or price <= 0 or cost <= 0:
            logging.warning("Missing or invalid fields.")
            return jsonify({'success': False, 'message': 'Missing or invalid fields'}), 400

        # Crear producto
        new_product = Product(
            name=name,
            brand_name=brand_name,
            price=price,
            cost=cost,
        )

        db.session.add(new_product)
        db.session.flush()  # Obtener new_product.id sin hacer commit

        # Crear entrada en inventario con cantidad = 0
        inventory_entry = Inventory(
            product_id=new_product.id,
            quantity=0
        )
        db.session.add(inventory_entry)
        db.session.commit()

        logging.info("Product and inventory entry saved successfully.")
        return jsonify({'success': True, 'message': 'Product saved successfully'}), 201

    except Exception as e:
        logging.error(f"Error saving product: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Error saving product'}), 500

