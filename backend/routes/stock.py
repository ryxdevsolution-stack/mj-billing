import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from extensions import db
from models.stock_model import StockEntry
from utils.auth_middleware import authenticate
from utils.audit_logger import log_action

stock_bp = Blueprint('stock', __name__)


@stock_bp.route('', methods=['POST'])
@authenticate
def add_stock():
    """
    Add stock entry with client_id
    Auto-sum if product already exists for this client
    """
    try:
        data = request.get_json()
        client_id = g.user['client_id']

        # Validate required fields
        required_fields = ['product_name', 'quantity', 'rate']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if product already exists for this client
        existing_product = StockEntry.query.filter_by(
            client_id=client_id,
            product_name=data['product_name']
        ).first()

        if existing_product:
            # Auto-sum: Update existing product quantity
            old_data = existing_product.to_dict()
            existing_product.quantity += data['quantity']
            existing_product.rate = data.get('rate', existing_product.rate)
            existing_product.category = data.get('category', existing_product.category)
            existing_product.unit = data.get('unit', existing_product.unit)
            existing_product.low_stock_alert = data.get('low_stock_alert', existing_product.low_stock_alert)
            existing_product.updated_at = datetime.utcnow()

            db.session.commit()

            # Log action
            log_action('UPDATE', 'stock_entry', existing_product.product_id, old_data, existing_product.to_dict())

            return jsonify({
                'success': True,
                'product_id': existing_product.product_id,
                'message': 'Stock updated successfully (quantity added)',
                'product': existing_product.to_dict()
            }), 200

        else:
            # Create new product entry
            new_product = StockEntry(
                product_id=str(uuid.uuid4()),
                client_id=client_id,
                product_name=data['product_name'],
                category=data.get('category', 'Other'),
                quantity=data['quantity'],
                rate=data['rate'],
                unit=data.get('unit', 'pcs'),
                low_stock_alert=data.get('low_stock_alert', 10),
                created_at=datetime.utcnow()
            )

            db.session.add(new_product)
            db.session.commit()

            # Log action
            log_action('CREATE', 'stock_entry', new_product.product_id, None, new_product.to_dict())

            return jsonify({
                'success': True,
                'product_id': new_product.product_id,
                'message': 'Stock added successfully',
                'product': new_product.to_dict()
            }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add stock', 'message': str(e)}), 500


@stock_bp.route('', methods=['GET'])
@authenticate
def get_stock():
    """List stock entries filtered by client_id"""
    try:
        client_id = g.user['client_id']

        # Get query parameters
        category = request.args.get('category')
        search = request.args.get('search')

        # Build query
        query = StockEntry.query.filter_by(client_id=client_id)

        if category:
            query = query.filter_by(category=category)

        if search:
            query = query.filter(StockEntry.product_name.ilike(f'%{search}%'))

        # Get results
        stock_entries = query.order_by(StockEntry.product_name).all()

        return jsonify({
            'success': True,
            'stock': [entry.to_dict() for entry in stock_entries]
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to fetch stock', 'message': str(e)}), 500


@stock_bp.route('/alerts', methods=['GET'])
@authenticate
def get_low_stock_alerts():
    """Get low stock alerts filtered by client_id"""
    try:
        client_id = g.user['client_id']

        # Get products where quantity <= low_stock_alert
        low_stock = StockEntry.query.filter(
            StockEntry.client_id == client_id,
            StockEntry.quantity <= StockEntry.low_stock_alert
        ).order_by(StockEntry.quantity).all()

        return jsonify({
            'success': True,
            'alerts': [
                {
                    'product_id': item.product_id,
                    'product_name': item.product_name,
                    'current_quantity': item.quantity,
                    'alert_threshold': item.low_stock_alert,
                    'unit': item.unit
                }
                for item in low_stock
            ],
            'alert_count': len(low_stock)
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to fetch alerts', 'message': str(e)}), 500


@stock_bp.route('/<product_id>', methods=['PUT'])
@authenticate
def update_stock(product_id):
    """Update stock entry with client_id validation"""
    try:
        client_id = g.user['client_id']
        data = request.get_json()

        # Find product
        product = StockEntry.query.filter_by(
            product_id=product_id,
            client_id=client_id
        ).first()

        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Store old data for audit
        old_data = product.to_dict()

        # Update fields
        if 'product_name' in data:
            product.product_name = data['product_name']
        if 'category' in data:
            product.category = data['category']
        if 'quantity' in data:
            product.quantity = data['quantity']
        if 'rate' in data:
            product.rate = data['rate']
        if 'unit' in data:
            product.unit = data['unit']
        if 'low_stock_alert' in data:
            product.low_stock_alert = data['low_stock_alert']

        product.updated_at = datetime.utcnow()

        db.session.commit()

        # Log action
        log_action('UPDATE', 'stock_entry', product_id, old_data, product.to_dict())

        return jsonify({
            'success': True,
            'message': 'Stock updated successfully',
            'product': product.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update stock', 'message': str(e)}), 500


@stock_bp.route('/<product_id>', methods=['DELETE'])
@authenticate
def delete_stock(product_id):
    """Delete stock entry with client_id validation"""
    try:
        client_id = g.user['client_id']

        # Find product
        product = StockEntry.query.filter_by(
            product_id=product_id,
            client_id=client_id
        ).first()

        if not product:
            return jsonify({'error': 'Product not found'}), 404

        # Store data for audit
        old_data = product.to_dict()

        db.session.delete(product)
        db.session.commit()

        # Log action
        log_action('DELETE', 'stock_entry', product_id, old_data, None)

        return jsonify({
            'success': True,
            'message': 'Stock deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete stock', 'message': str(e)}), 500
