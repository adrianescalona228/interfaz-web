# routes/inventory/view_inventory.py
import logging
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy.orm import joinedload
from database import db
from database.models import Inventory, Product

view_inventory_bp = Blueprint('view_inventory', __name__)

@view_inventory_bp.route('/view_inventory')
def view_inventory():
    inventory_items = db.session.query(Inventory).options(joinedload(Inventory.product)).all()
    return render_template('inventory/view_inventory.html', inventory=inventory_items)

@view_inventory_bp.route('/update_product', methods=['POST'])
def update_product():
    data = request.json
    product_id = data.get('id')
    column = data.get('column')
    value = data.get('value')

    # Valid column mapping
    valid_columns = {
        'id': 'id',
        'product': 'product_id',
        'quantity': 'quantity',
        'price': 'price',
        'cost': 'cost',
        'brand': 'brand_id'
    }

    column_attr = valid_columns.get(column)
    if column_attr is None:
        return jsonify({'success': False, 'message': 'Invalid column'}), 400

    try:
        inventory_item = db.session.get(Inventory, product_id)
        if not inventory_item:
            return jsonify({'success': False, 'message': 'Product not found'}), 404

        # Convert value if needed (int, float)
        if column_attr in ['quantity', 'product_type_id', 'brand_id']:
            value = int(value)
        elif column_attr in ['price', 'cost']:
            value = float(value)

        setattr(inventory_item, column_attr, value)
        db.session.commit()

        logging.info(f"Updated product ID {product_id}. Column: {column_attr.upper()}, New value: {value}")
        return jsonify({'success': True, 'message': 'Product updated successfully'}), 200

    except Exception as e:
        logging.error(f"Error updating product ID {product_id}, Column: {column_attr.upper()}, Value: {value} - {e}", exc_info=True)
        return jsonify({'success': False, 'message': 'Error updating product'}), 500
