"""
Course announcement model - faculty posts to enrolled students (RBAC: assigned course only)
"""
from models.database import db

class CourseAnnouncement(db.Model):
    __tablename__ = 'course_announcements'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculty.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=True)
    announcement_type = db.Column(db.String(30), default='general')  # general, academic_update, enrollment_status
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    course = db.relationship('Course', backref=db.backref('announcements', lazy='dynamic', cascade='all, delete-orphan'))
    faculty = db.relationship('Faculty', backref=db.backref('announcements', lazy='dynamic', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'faculty_id': self.faculty_id,
            'title': self.title,
            'body': self.body,
            'announcement_type': self.announcement_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
