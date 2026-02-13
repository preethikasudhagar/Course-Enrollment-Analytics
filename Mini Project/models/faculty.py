"""
Faculty model
"""
from models.database import db

class Faculty(db.Model):
    """Faculty profile model"""
    __tablename__ = 'faculty'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=True)
    hire_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    department = db.relationship('Department', backref='faculty_members')
    
    def __repr__(self):
        return f'<Faculty {self.user_id}>'
    
    def to_dict(self):
        """Convert faculty to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'department_id': self.department_id,
            'employee_id': self.employee_id,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None
        }
