import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, g
from extensions import db
from models.payment_model import PaymentType
from utils.auth_middleware import authenticate
from utils.audit_logger import log_action

payment_bp = Blueprint('payment', __name__)


@payment_bp.route('', methods=['POST'])
@authenticate
def add_payment_type():
    """Add payment type with client_id"""
    try:
        data = request.get_json()
        client_id = g.user['client_id']

        # Validate required fields
        if 'type_name' not in data:
            return jsonify({'error': 'Missing required field: type_name'}), 400

        # Check if payment type already exists for this client
        existing = PaymentType.query.filter_by(
            client_id=client_id,
            payment_name=data['type_name']
        ).first()

        if existing:
            return jsonify({'error': 'Payment type already exists'}), 400

        # Create new payment type
        new_payment_type = PaymentType(
            payment_type_id=str(uuid.uuid4()),
            client_id=client_id,
            payment_name=data['type_name'],
            created_at=datetime.utcnow()
        )

        db.session.add(new_payment_type)
        db.session.commit()

        # Log action
        log_action('CREATE', 'payment_type', new_payment_type.payment_type_id, None, new_payment_type.to_dict())

        return jsonify({
            'success': True,
            'payment_type_id': new_payment_type.payment_type_id,
            'message': 'Payment type added successfully',
            'payment_type': new_payment_type.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add payment type', 'message': str(e)}), 500


@payment_bp.route('/list', methods=['GET'])
@authenticate
def get_payment_types():
    """List payment types filtered by client_id"""
    try:
        client_id = g.user['client_id']

        payment_types = PaymentType.query.filter_by(client_id=client_id).order_by(PaymentType.payment_name).all()

        return jsonify({
            'success': True,
            'payment_types': [pt.to_dict() for pt in payment_types]
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to fetch payment types', 'message': str(e)}), 500


@payment_bp.route('/<payment_type_id>', methods=['GET'])
@authenticate
def get_payment_type(payment_type_id):
    """Get payment type details with client_id validation"""
    try:
        client_id = g.user['client_id']

        payment_type = PaymentType.query.filter_by(
            payment_type_id=payment_type_id,
            client_id=client_id
        ).first()

        if not payment_type:
            return jsonify({'error': 'Payment type not found'}), 404

        return jsonify({
            'success': True,
            'payment_type': payment_type.to_dict()
        }), 200

    except Exception as e:
        return jsonify({'error': 'Failed to fetch payment type', 'message': str(e)}), 500


@payment_bp.route('/<payment_type_id>', methods=['PUT'])
@authenticate
def update_payment_type(payment_type_id):
    """Update payment type with client_id validation"""
    try:
        client_id = g.user['client_id']
        data = request.get_json()

        payment_type = PaymentType.query.filter_by(
            payment_type_id=payment_type_id,
            client_id=client_id
        ).first()

        if not payment_type:
            return jsonify({'error': 'Payment type not found'}), 404

        # Store old data for audit
        old_data = payment_type.to_dict()

        # Update fields
        if 'type_name' in data:
            payment_type.payment_name = data['type_name']

        payment_type.updated_at = datetime.utcnow()

        db.session.commit()

        # Log action
        log_action('UPDATE', 'payment_type', payment_type_id, old_data, payment_type.to_dict())

        return jsonify({
            'success': True,
            'message': 'Payment type updated successfully',
            'payment_type': payment_type.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update payment type', 'message': str(e)}), 500


@payment_bp.route('/<payment_type_id>', methods=['DELETE'])
@authenticate
def delete_payment_type(payment_type_id):
    """Delete payment type with client_id validation"""
    try:
        client_id = g.user['client_id']

        payment_type = PaymentType.query.filter_by(
            payment_type_id=payment_type_id,
            client_id=client_id
        ).first()

        if not payment_type:
            return jsonify({'error': 'Payment type not found'}), 404

        # Store data for audit
        old_data = payment_type.to_dict()

        db.session.delete(payment_type)
        db.session.commit()

        # Log action
        log_action('DELETE', 'payment_type', payment_type_id, old_data, None)

        return jsonify({
            'success': True,
            'message': 'Payment type deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete payment type', 'message': str(e)}), 500
