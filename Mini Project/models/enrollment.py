"""
Enrollment model
"""
from models.database import db

class Enrollment(db.Model):
    """Enrollment model linking students to courses"""
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    status = db.Column(db.String(20), default='enrolled')  # enrolled, waitlisted, completed, dropped, withdrawn
    grade = db.Column(db.String(2), nullable=True)
    remarks = db.Column(db.Text, nullable=True)  # Faculty can add remarks
    enrollment_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Unique constraint: one student can only enroll once per course
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_student_course'),)
    
    def __repr__(self):
        return f'<Enrollment {self.student_id}-{self.course_id}>'
    
    def to_dict(self):
        """Convert enrollment to dictionary"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'status': self.status,
            'grade': self.grade,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None
        }
