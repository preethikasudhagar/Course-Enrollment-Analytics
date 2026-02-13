"""
Faculty-Course assignment model (which courses a faculty teaches)
"""
from models.database import db

class FacultyCourseAssignment(db.Model):
    """Links faculty to courses they teach"""
    __tablename__ = 'faculty_course_assignments'

    id = db.Column(db.Integer, primary_key=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    assigned_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    __table_args__ = (db.UniqueConstraint('faculty_id', 'course_id', name='unique_faculty_course'),)

    faculty = db.relationship('Faculty', backref=db.backref('course_assignments', lazy='dynamic', cascade='all, delete-orphan'))
    course = db.relationship('Course', backref=db.backref('faculty_assignments', lazy='dynamic', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'faculty_id': self.faculty_id,
            'course_id': self.course_id,
        }
