import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from extensions import db
from models.billing_model import GSTBilling, NonGSTBilling
from models.stock_model import StockEntry
from utils.auth_middleware import authenticate
from utils.audit_logger import log_action
from utils.helpers import calculate_gst_amount, calculate_final_amount, validate_items

billing_bp = Blueprint('billing', __name__)


@billing_bp.route('/gst', methods=['POST'])
@authenticate
def create_gst_bill():
    """
    Create GST-enabled bill with client_id validation
    MANDATORY: All items must belong to same client_id
    """
    try:
        data = request.get_json()
        client_id = g.user['client_id']

        # Validate required fields
        required_fields = ['customer_name', 'items', 'subtotal', 'gst_percentage', 'payment_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate items
        is_valid, error_msg = validate_items(data['items'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Verify all products belong to this client
        for item in data['items']:
            product = StockEntry.query.filter_by(
                product_id=item['product_id'],
                client_id=client_id
            ).first()

            if not product:
                return jsonify({'error': f"Product {item['product_name']} not found for your account"}), 404

            # Check stock availability
            if product.quantity < item['quantity']:
                return jsonify({'error': f"Insufficient stock for {item['product_name']}. Available: {product.quantity}"}), 400

        # Calculate GST amount and final amount
        gst_amount = calculate_gst_amount(data['subtotal'], data['gst_percentage'])
        final_amount = calculate_final_amount(data['subtotal'], gst_amount)

        # Get next bill number for this client
        last_bill = GSTBilling.query.filter_by(client_id=client_id).order_by(GSTBilling.bill_number.desc()).first()
        bill_number = (last_bill.bill_number + 1) if last_bill else 1

        # Create GST bill
        new_bill = GSTBilling(
            bill_id=str(uuid.uuid4()),
            client_id=client_id,
            bill_number=bill_number,
            customer_name=data['customer_name'],
            customer_phone=data.get('customer_phone'),
            items=data['items'],
            subtotal=data['subtotal'],
            gst_percentage=data['gst_percentage'],
            gst_amount=gst_amount,
            final_amount=final_amount,
            payment_type=data['payment_type'],
            status='final',
            created_by=g.user['user_id'],
            created_at=datetime.utcnow()
        )

        db.session.add(new_bill)
        db.session.commit()

        # Log action
        log_action('CREATE', 'gst_billing', new_bill.bill_id, None, new_bill.to_dict())

        # Note: Stock reduction handled automatically by database trigger

        return jsonify({
            'success': True,
            'bill_id': new_bill.bill_id,
            'bill_number': bill_number,
            'final_amount': str(final_amount),
            'message': 'GST bill created successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create GST bill', 'message': str(e)}), 500


@billing_bp.route('/non-gst', methods=['POST'])
@authenticate
def create_non_gst_bill():
    """
    Create Non-GST bill with client_id validation
    MANDATORY: All items must belong to same client_id
    """
    try:
        data = request.get_json()
        client_id = g.user['client_id']

        # Validate required fields
        required_fields = ['customer_name', 'items', 'total_amount', 'payment_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Validate items
        is_valid, error_msg = validate_items(data['items'])
        if not is_valid:
            return jsonify({'error': error_msg}), 400

        # Verify all products belong to this client
        for item in data['items']:
            product = StockEntry.query.filter_by(
                product_id=item['product_id'],
                client_id=client_id
            ).first()

            if not product:
                return jsonify({'error': f"Product {item['product_name']} not found for your account"}), 404

            # Check stock availability
            if product.quantity < item['quantity']:
                return jsonify({'error': f"Insufficient stock for {item['product_name']}. Available: {product.quantity}"}), 400

        # Get next bill number for this client
        last_bill = NonGSTBilling.query.filter_by(client_id=client_id).order_by(NonGSTBilling.bill_number.desc()).first()
        bill_number = (last_bill.bill_number + 1) if last_bill else 1

        # Create Non-GST bill
        new_bill = NonGSTBilling(
            bill_id=str(uuid.uuid4()),
            client_id=client_id,
            bill_number=bill_number,
            customer_name=data['customer_name'],
            customer_phone=data.get('customer_phone'),
            items=data['items'],
            total_amount=data['total_amount'],
            payment_type=data['payment_type'],
            status='final',
            created_by=g.user['user_id'],
            created_at=datetime.utcnow()
        )

        db.session.add(new_bill)
        db.session.commit()

        # Log action
        log_action('CREATE', 'non_gst_billing', new_bill.bill_id, None, new_bill.to_dict())

        # Note: Stock reduction handled automatically by database trigger

        return jsonify({
            'success': True,
            'bill_id': new_bill.bill_id,
            'bill_number': bill_number,
            'total_amount': str(data['total_amount']),
            'message': 'Non-GST bill created successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create Non-GST bill', 'message': str(e)}), 500


@billing_bp.route('/list', methods=['GET'])
@authenticate
def get_bills():
    """
    List all bills (GST + Non-GST) filtered by client_id
    """
    try:
        client_id = g.user['client_id']

        # Get query parameters
        bill_type = request.args.get('type', 'all')  # gst, non-gst, all
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))

        bills = []

        # Get GST bills if requested
        if bill_type in ['gst', 'all']:
            gst_query = GSTBilling.query.filter_by(client_id=client_id)

            if date_from:
                gst_query = gst_query.filter(GSTBilling.created_at >= date_from)
            if date_to:
                gst_query = gst_query.filter(GSTBilling.created_at <= date_to)

            gst_bills = gst_query.order_by(GSTBilling.created_at.desc()).all()
            bills.extend([bill.to_dict() for bill in gst_bills])

        # Get Non-GST bills if requested
        if bill_type in ['non-gst', 'all']:
            non_gst_query = NonGSTBilling.query.filter_by(client_id=client_id)

            if date_from:
                non_gst_query = non_gst_query.filter(NonGSTBilling.created_at >= date_from)
            if date_to:
                non_gst_query = non_gst_query.filter(NonGSTBilling.created_at <= date_to)

            non_gst_bills = non_gst_query.order_by(NonGSTBilling.created_at.desc()).all()
            bills.extend([bill.to_dict() for bill in non_gst_bills])

        # Sort by created_at descending
        bills.sort(key=lambda x: x['created_at'], reverse=True)

        # Pagination
        total_records = len(bills)
        start = (page - 1) * limit
        end = start + limit
        paginated_bills = bills[start:end]

        return jsonify({
            'success': True,
            'bills': paginated_bills,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_records': total_records,
                'total_pages': (total_records + limit - 1) // limit
            }
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to fetch bills', 'message': str(e)}), 500


@billing_bp.route('/<bill_id>', methods=['GET'])
@authenticate
def get_bill_details(bill_id):
    """Get bill details by ID with client_id validation"""
    try:
        client_id = g.user['client_id']

        # Try GST billing first
        gst_bill = GSTBilling.query.filter_by(bill_id=bill_id, client_id=client_id).first()
        if gst_bill:
            return jsonify({
                'success': True,
                'bill': gst_bill.to_dict()
            }), 200

        # Try Non-GST billing
        non_gst_bill = NonGSTBilling.query.filter_by(bill_id=bill_id, client_id=client_id).first()
        if non_gst_bill:
            return jsonify({
                'success': True,
                'bill': non_gst_bill.to_dict()
            }), 200

        return jsonify({'error': 'Bill not found'}), 404

    except Exception as e:
        return jsonify({'error': 'Failed to fetch bill details', 'message': str(e)}), 500
