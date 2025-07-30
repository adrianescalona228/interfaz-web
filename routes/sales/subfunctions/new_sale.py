# routes/sales/new_sale.py

from flask import Blueprint, render_template, request, jsonify
from database import db
from database.models import Client, Sale, SaleItem, Inventory, Debt, Product
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

new_sale_bp = Blueprint('new_sale', __name__)

@new_sale_bp.route('/new_sale')
def new_sale():
    """Render the new sale form."""
    return render_template('sales/new_sale.html')

@new_sale_bp.route('/process_sale', methods=['POST'])
def process_sale():
    """Process a new sale: create Sale, SaleItems, update inventory and debt."""
    data = request.get_json() or {}
    print(data,flush=True)
    client_name   = data.get('client')
    sale_number   = data.get('sale_number')
    date_str      = data.get('date')
    products      = data.get('products', [])
    total_amount  = data.get('total_amount')

    if not products:
        logger.error('No products received in payload.')
        return jsonify({'error': 'No products provided'}), 400

    # Parse date
    try:
        sale_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except Exception:
        logger.error('Invalid date format: %s', date_str)
        return jsonify({'error': 'Invalid date'}), 400

    # Check for duplicate sale_number
    if Sale.query.filter_by(sale_number=sale_number).first():
        logger.error('Sale number %s already exists.', sale_number)
        return jsonify({'error': 'Sale number already exists'}), 400

    # Find client
    client = db.session.query(Client).filter_by(client_name=client_name).first()
    if not client:
        logger.error('Client not found: %s', client_name)
        return jsonify({'error': 'Client not found'}), 400

    try:
        # Create the Sale record
        sale = Sale(sale_number=sale_number, 
                    client_id=client.id, 
                    issue_date=sale_date,
                    total_amount=total_amount,
                    due_date=sale_date + timedelta(days=15))
        db.session.add(sale)
        db.session.flush()  # so sale.id is available

        # For each product: record SaleItem and update inventory
        for p in products:
            name     = p.get('product')
            qty      = float(str(p.get('quantity')).replace(',', '.'))
            unit_pr  = float(str(p.get('price')).replace(',', '.'))

            logger.info(f'Processing product {name}: qty={qty}, unit_price={unit_pr}')

            # Lookup Inventory by product name
            inv = db.session.query(Inventory).join(Inventory.product)\
                     .filter_by(name=name).first()
            if not inv:
                logger.error('Product %s not in inventory', name)
                return jsonify({'error': f'Product {name} not in inventory'}), 400

            # Create item
            item = SaleItem(
                sale_id=sale.id,
                product_id=inv.product_id,
                quantity=qty,
                price_unit=unit_pr
            )
            db.session.add(item)

            # Update inventory quantity
            inv.quantity -= qty
            if inv.quantity < 0:
                logger.error('Insufficient stock for %s', name)
                return jsonify({'error': f'Insufficient stock for {name}'}), 400

        # Create debt record
        debt = Debt(
            sale_id=sale.id,
            client_id=client.id,
            paid_amount=0.0,
            status='pending'
        )
        db.session.add(debt)

        db.session.commit()
        logger.info('Sale %s processed successfully.', sale.id)
        return jsonify({'message': f'Sale {sale.id} processed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error('Error processing sale: %s', e, exc_info=True)
        return jsonify({'error': 'Error processing sale'}), 500

@new_sale_bp.route('/autocomplete_clients', methods=['GET'])
def autocomplete_clients():
    term = request.args.get('term', '')
    names = [c.client_name for c in Client.query.filter(Client.client_name.ilike(f'%{term}%')).all()]
    return jsonify(names)

@new_sale_bp.route('/autocomplete_products', methods=['GET'])
def autocomplete_products():
    term = request.args.get('term', '')
    # join Product and Inventory to get price/cost/qty
    rows = db.session.query(Inventory).join(Inventory.product)\
        .filter(Inventory.product.has(Product.name.ilike(f'%{term}%')))
    result = []
    for inv in rows:
        result.append({
            'label': inv.product.name,
            'value': inv.product.name,
            'price': inv.product.price,
            'cost': inv.product.cost,
            'quantity': inv.quantity
        })
    return jsonify(result)

@new_sale_bp.route('/last_sale_number', methods=['GET'])
def last_sale_number():
    last = db.session.query(db.func.max(Sale.sale_number)).scalar() or 0
    print(last, flush=True)
    return jsonify({'last_number': int(last) + 1})

@new_sale_bp.route('/verify_sale_number', methods=['POST'])
def verify_sale_number():
    data = request.get_json() or {}
    num = data.get('sale_number')
    exists = db.session.query(Sale).filter_by(sale_number=num).first() is not None
    return jsonify({'exists': exists})
