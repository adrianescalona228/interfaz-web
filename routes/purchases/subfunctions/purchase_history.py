# routes/purchases/purchase_history.py

from flask import Blueprint, render_template, jsonify, request, flash
from database import db
from database.models import Purchase, Supplier, PurchaseItem, Inventory, Product
import logging

logger = logging.getLogger(__name__)

purchase_history_bp = Blueprint('purchase_history', __name__)

@purchase_history_bp.route('/purchase_history')
def purchase_history():
    try:
        purchases = db.session.query(Purchase).outerjoin(Supplier).order_by(Purchase.purchase_number).all()
        logger.info(f"{len(purchases)} purchases loaded for history.")

        purchase_data = []
        for purchase in purchases:
            purchase_items = db.session.query(PurchaseItem).filter_by(purchase_id=purchase.id).all()
            items_data = []
            total_amount = 0

            for item in purchase_items:
                product = db.session.get(Product, item.product_id)
                if product:
                    item_total = float(item.cost) * int(item.quantity)
                    total_amount += item_total
                    items_data.append({
                        "product_id": item.product_id,
                        "product_name": product.name,
                        "quantity": item.quantity,
                        "unit_cost": item.cost
                    })

            purchase_data.append({
                "purchase_number": purchase.purchase_number,
                "supplier": purchase.supplier.name if purchase.supplier else "Proveedor no asignado",
                "date": purchase.date,
                "products": items_data,
                "total_amount": total_amount
            })
        logger.info("Purchase history processed successfully.")
        return render_template('/purchases/purchase_history.html', purchases=purchase_data)

    except Exception as e:
        logger.error(f"Error in purchase_history(): {e}")
        return jsonify({'status': 'error', 'message': 'Failed to load purchase history.'}), 500


@purchase_history_bp.route('/delete_purchase/<int:purchase_number>', methods=['POST'])
def delete_purchase(purchase_number):
    try:
        purchase = db.session.query(Purchase).filter_by(purchase_number=purchase_number).first()
        if not purchase:
            flash("Purchase does not exist", "error")
            return '', 404

        items = db.session.query(PurchaseItem).filter_by(purchase_id=purchase.id).all()

        # Restore inventory before deleting purchase
        for item in items:
            inventory = db.session.query(Inventory).filter_by(product_id=item.product_id).first()
            if inventory:
                inventory.quantity -= item.quantity

        # Delete purchase items and purchase
        for item in items:
            db.session.delete(item)

        db.session.delete(purchase)
        db.session.commit()

        flash("Purchase and associated products deleted successfully", "success")
        return '', 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting purchase {purchase_number}: {e}")
        flash("An error occurred while deleting the purchase", "error")
        return '', 500


@purchase_history_bp.route('/delete_product/<int:purchase_id>/<int:product_id>', methods=['POST'])
def delete_product_from_purchase(purchase_id, product_id):
    try:
        purchase_item = db.session.query(PurchaseItem).filter_by(purchase_id=purchase_id, product_id=product_id).first()

        if not purchase_item:
            flash("Product not found in purchase", "error")
            return '', 404

        # Calculate total to subtract
        total_to_subtract = float(purchase_item.cost) * int(purchase_item.quantity)

        # Update inventory
        inventory = db.session.query(Inventory).filter_by(product_id=product_id).first()
        if inventory:
            before_qty = inventory.quantity
            inventory.quantity -= purchase_item.quantity
            after_qty = inventory.quantity
        else:
            before_qty = after_qty = 'Not available'

        # Update purchase total
        purchase = db.session.get(Purchase, purchase_id)
        if purchase:
            purchase.total_amount -= total_to_subtract

        db.session.delete(purchase_item)
        db.session.commit()

        logger.info(f"Product deleted from purchase: Purchase ID {purchase_id}, Product ID {product_id}. "
                    f"Total deducted: {total_to_subtract}. Inventory before: {before_qty}, after: {after_qty}")
        return '', 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting product from purchase {purchase_id}, product {product_id}: {str(e)}")
        flash("An error occurred while deleting the product.", "error")
        return '', 500
