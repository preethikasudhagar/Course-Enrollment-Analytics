"""
Audit log model for security event tracking
"""
from models.database import db
from datetime import datetime

class AuditLog(db.Model):
    """Audit log for security and system events"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    user_role = db.Column(db.String(20), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    route = db.Column(db.String(200), nullable=True)
    method = db.Column(db.String(10), nullable=True)
    details = db.Column(db.Text, nullable=True)  # JSON string
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f'<AuditLog {self.event_type} - {self.timestamp}>'
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'user_id': self.user_id,
            'user_role': self.user_role,
            'ip_address': self.ip_address,
            'route': self.route,
            'method': self.method,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
