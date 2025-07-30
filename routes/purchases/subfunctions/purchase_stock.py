from flask import Blueprint, render_template, request, jsonify
from database import db
from database.models import Supplier, Inventory, Purchase, PurchaseItem, Product
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

purchase_stock_bp = Blueprint('purchase_stock', __name__)

@purchase_stock_bp.route('/purchase_stock')
def purchase_stock():
    return render_template('purchases/purchase_stock.html')

@purchase_stock_bp.route('/process_purchase', methods=['POST'])
def process_purchase():
    try:
        data = request.get_json()
        supplier_name = data.get('supplier', '')
        purchase_number = data['purchase_id']
        date_str = data['date']
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        products = data['products']
        print(products, flush=True)

        logger.debug(f"Received data: {data}")
    except (KeyError, TypeError) as e:
        logger.error(f"Error processing request data: {e}")
        return jsonify({'status': 'error', 'message': f"Invalid input data: {e}"}), 400

    try:
        # Check if purchase number exists
        existing_purchase = db.session.query(Purchase).filter_by(purchase_number=purchase_number).first()
        if existing_purchase:
            raise ValueError('This purchase number has already been registered.')

        # Get supplier object

        supplier = None
        if supplier_name != '':
            supplier = db.session.query(Supplier).filter_by(name=supplier_name).first()
            if not supplier:
                raise ValueError('Supplier not found')
            logger.info(f"Supplier found: ID {supplier.id} for '{supplier_name}'")


        # Calculate total purchase amount
        total_purchase = sum(float(p['cost']) * int(p['quantity']) for p in products)
        total_purchase = round(total_purchase, 2)
        logger.info(f"Total purchase calculated: {total_purchase}")
        # Create Purchase object
        new_purchase = Purchase(
            supplier_id=supplier.id if supplier else None,
            purchase_number=purchase_number,
            date=date,
            total_amount=total_purchase
        )
        db.session.add(new_purchase)
        db.session.flush()  # To get new_purchase.id before commit

        # Add purchase items and update inventory
        for p in products:
            # Find product by name
            product_obj = db.session.query(Product).filter_by(name=p['product']).first()
            if not product_obj:
                logger.warning(f"Product '{p['product']}' not found. Skipping.")
                continue

            # Get inventory items linked to product
            # Assuming one inventory item per product for simplicity
            if not product_obj.inventory_items:
                logger.warning(f"No inventory found for product '{p['product']}'. Skipping.")
                continue

            inventory_product = product_obj.inventory_items[0]

            # Add purchase item
            purchase_item = PurchaseItem(
                purchase_id=new_purchase.id,
                product_id=product_obj.id,
                quantity=p['quantity'],
                cost=p['cost']
            )
            db.session.add(purchase_item)

            # Update inventory quantity
            inventory_product.quantity += int(p['quantity'])
            logger.info(f"Updated inventory for product '{p['product']}' to quantity {inventory_product.quantity}")

        db.session.commit()
        logger.info(f"Purchase transaction committed successfully for purchase number {purchase_number}")
        return jsonify({'status': 'success', 'message': 'Purchase processed successfully'})

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing purchase {purchase_number}: {e}", exc_info=True)
        return jsonify({'status': 'error', 'message': str(e)}), 500

@purchase_stock_bp.route('/autocomplete_suppliers', methods=['GET'])
def autocomplete_suppliers():
    term = request.args.get('term', '')
    suppliers = db.session.query(Supplier.name).filter(Supplier.name.ilike(f'%{term}%')).all()
    supplier_names = [s[0] for s in suppliers]
    return jsonify(supplier_names)
