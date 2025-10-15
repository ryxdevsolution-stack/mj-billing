"""
Run script for RYX Billing Backend
This ensures proper Flask application context
"""
from app import create_app
from extensions import db

# Create the Flask app
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create tables if they don't exist (optional, since we use migrations)
        # db.create_all()
        pass

    # Run the app
    print("=" * 60)
    print("RYX Billing API Server")
    print("=" * 60)
    print("Server running at: http://localhost:5000")
    print("API endpoints available at: http://localhost:5000/api/")
    print("=" * 60)

    app.run(host='0.0.0.0', port=5000, debug=True)
