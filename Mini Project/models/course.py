"""
Course model
"""
from models.database import db

class Course(db.Model):
    """Course model"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False)
    credits = db.Column(db.Integer, default=3)
    seat_limit = db.Column(db.Integer, nullable=True)  # null = no limit
    description = db.Column(db.Text, nullable=True)
    syllabus = db.Column(db.Text, nullable=True)
    schedule = db.Column(db.String(200), nullable=True)  # e.g. "Mon/Wed 10-11 AM"
    semester = db.Column(db.String(20), nullable=True)   # e.g. "Fall 2024"
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    department = db.relationship('Department', backref='courses')
    enrollments = db.relationship('Enrollment', backref='course', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Course {self.code}>'
    
    def to_dict(self):
        """Convert course to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'department_id': self.department_id,
            'credits': self.credits,
            'seat_limit': self.seat_limit,
            'description': self.description,
            'syllabus': self.syllabus,
            'schedule': getattr(self, 'schedule', None),
            'semester': getattr(self, 'semester', None)
        }

    def current_enrollment_count(self):
        """Count of active enrollments (enrolled status)"""
        return self.enrollments.filter_by(status='enrolled').count()

    def seats_available(self):
        """Seats available (None if no limit)"""
        if self.seat_limit is None:
            return None
        return max(0, self.seat_limit - self.current_enrollment_count())
