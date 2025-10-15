from extensions import db
from datetime import datetime

class StockEntry(db.Model):
    """Product inventory management with client isolation"""
    __tablename__ = 'stock_entry'

    product_id = db.Column(db.String(36), primary_key=True)
    client_id = db.Column(db.String(36), db.ForeignKey('client_entry.client_id'), nullable=False, index=True)
    product_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    quantity = db.Column(db.Integer, nullable=False, default=0)
    rate = db.Column(db.Numeric(10, 2), nullable=False)
    unit = db.Column(db.String(20), default='pcs')
    low_stock_alert = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'client_id': self.client_id,
            'product_name': self.product_name,
            'category': self.category,
            'quantity': self.quantity,
            'rate': str(self.rate),
            'unit': self.unit,
            'low_stock_alert': self.low_stock_alert,
            'is_low_stock': self.quantity <= self.low_stock_alert,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
