import uuid
import io
import csv
from datetime import datetime
from flask import Blueprint, request, jsonify, g, send_file
from werkzeug.utils import secure_filename
import pandas as pd
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


@stock_bp.route('/bulk-import', methods=['POST'])
@authenticate
def bulk_import_stock():
    """
    Bulk import stock from CSV or Excel file
    Supports both create new and update existing products
    """
    try:
        client_id = g.user['client_id']

        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check file extension
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

        if file_ext not in ['csv', 'xlsx', 'xls']:
            return jsonify({'error': 'Invalid file format. Only CSV, XLSX, XLS files are allowed'}), 400

        # Read file based on extension
        try:
            if file_ext == 'csv':
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return jsonify({'error': 'Failed to read file', 'message': str(e)}), 400

        # Validate required columns
        required_columns = ['product_name', 'quantity', 'rate']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            return jsonify({
                'error': f'Missing required columns: {", ".join(missing_columns)}',
                'required_columns': required_columns,
                'found_columns': list(df.columns)
            }), 400

        # Process each row
        success_count = 0
        error_count = 0
        updated_count = 0
        created_count = 0
        errors = []

        for index, row in df.iterrows():
            try:
                # Skip rows with missing required fields
                if pd.isna(row['product_name']) or pd.isna(row['quantity']) or pd.isna(row['rate']):
                    error_count += 1
                    errors.append(f"Row {index + 2}: Missing required fields")
                    continue

                product_name = str(row['product_name']).strip()
                quantity = int(row['quantity'])
                rate = float(row['rate'])
                category = str(row['category']).strip() if 'category' in row and not pd.isna(row['category']) else 'Other'
                unit = str(row['unit']).strip() if 'unit' in row and not pd.isna(row['unit']) else 'pcs'
                low_stock_alert = int(row['low_stock_alert']) if 'low_stock_alert' in row and not pd.isna(row['low_stock_alert']) else 10

                # Validate quantity and rate
                if quantity < 0 or rate < 0:
                    error_count += 1
                    errors.append(f"Row {index + 2}: Quantity and rate must be positive")
                    continue

                # Check if product already exists
                existing_product = StockEntry.query.filter_by(
                    client_id=client_id,
                    product_name=product_name
                ).first()

                if existing_product:
                    # Update existing product (auto-sum quantity)
                    old_data = existing_product.to_dict()
                    existing_product.quantity += quantity
                    existing_product.rate = rate
                    existing_product.category = category
                    existing_product.unit = unit
                    existing_product.low_stock_alert = low_stock_alert
                    existing_product.updated_at = datetime.utcnow()

                    # Log action
                    log_action('UPDATE', 'stock_entry', existing_product.product_id, old_data, existing_product.to_dict())

                    updated_count += 1
                else:
                    # Create new product
                    new_product = StockEntry(
                        product_id=str(uuid.uuid4()),
                        client_id=client_id,
                        product_name=product_name,
                        category=category,
                        quantity=quantity,
                        rate=rate,
                        unit=unit,
                        low_stock_alert=low_stock_alert,
                        created_at=datetime.utcnow()
                    )

                    db.session.add(new_product)

                    # Log action
                    log_action('CREATE', 'stock_entry', new_product.product_id, None, new_product.to_dict())

                    created_count += 1

                success_count += 1

            except Exception as e:
                error_count += 1
                errors.append(f"Row {index + 2}: {str(e)}")

        # Commit all changes
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Bulk import completed',
            'summary': {
                'total_rows': len(df),
                'success_count': success_count,
                'created_count': created_count,
                'updated_count': updated_count,
                'error_count': error_count,
                'errors': errors[:10] if errors else []  # Return first 10 errors
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to import stock', 'message': str(e)}), 500


@stock_bp.route('/download-template', methods=['POST'])
@authenticate
def download_template():
    """Download CSV/Excel template for bulk import with sample data"""
    try:
        import os
        data = request.get_json() or {}
        file_format = data.get('format', 'csv')

        print(file_format)

        # Get the path to template files
        template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')

        if file_format == 'csv':
            template_path = os.path.join(template_dir, 'stock_template.csv')
            if os.path.exists(template_path):
                return send_file(
                    template_path,
                    mimetype='text/csv',
                    as_attachment=True,
                    download_name='stock_import_template.csv'
                )
        else:  # xlsx
            template_path = os.path.join(template_dir, 'stock_template.xlsx')
            if os.path.exists(template_path):
                return send_file(
                    template_path,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name='stock_import_template.xlsx'
                )

        # Fallback: Generate sample data if template files don't exist
        data = {
            'product_name': ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'Pen', 'Notebook'],
            'quantity': [10, 50, 30, 20, 100, 80],
            'rate': [50000.00, 500.00, 1500.00, 15000.00, 10.00, 25.00],
            'category': ['Electronics', 'Electronics', 'Electronics', 'Electronics', 'Stationery', 'Stationery'],
            'unit': ['pcs', 'pcs', 'pcs', 'pcs', 'pcs', 'pcs'],
            'low_stock_alert': [5, 10, 8, 5, 20, 15]
        }

        df = pd.DataFrame(data)
        output = io.BytesIO()

        if file_format == 'csv':
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name='stock_import_template.csv'
            )
        else:  # xlsx
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Stock Import')
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='stock_import_template.xlsx'
            )

    except Exception as e:
        return jsonify({'error': 'Failed to generate template', 'message': str(e)}), 500


@stock_bp.route('/bulk-export', methods=['POST'])
@authenticate
def bulk_export_stock():
    """Export all stock data to CSV or Excel"""
    try:
        client_id = g.user['client_id']
        data = request.get_json() or {}
        file_format = data.get('format', 'csv')

        # Get all stock entries
        stock_entries = StockEntry.query.filter_by(client_id=client_id).order_by(StockEntry.product_name).all()

        if not stock_entries:
            return jsonify({'error': 'No stock data to export'}), 404

        # Convert to DataFrame
        data = []
        for stock in stock_entries:
            data.append({
                'product_name': stock.product_name,
                'quantity': stock.quantity,
                'rate': stock.rate,
                'category': stock.category,
                'unit': stock.unit,
                'low_stock_alert': stock.low_stock_alert,
                'created_at': stock.created_at.strftime('%Y-%m-%d %H:%M:%S') if stock.created_at else ''
            })

        df = pd.DataFrame(data)

        # Create in-memory file
        output = io.BytesIO()

        if file_format == 'csv':
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(
                output,
                mimetype='text/csv',
                as_attachment=True,
                download_name='stock_export.csv'
            )
        else:  # xlsx
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Stock')
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='stock_export.xlsx'
            )

    except Exception as e:
        return jsonify({'error': 'Failed to export stock', 'message': str(e)}), 500
