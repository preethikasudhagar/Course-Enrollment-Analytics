"""
Student model
"""
from models.database import db

class Student(db.Model):
    """Student profile model"""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    enrollment_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Student {self.user_id}>'
    
    def to_dict(self):
        """Convert student to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'student_id': self.student_id,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None
        }
