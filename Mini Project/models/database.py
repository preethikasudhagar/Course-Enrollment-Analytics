"""
Database configuration and initialization
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

def schema_upgrade():
    """Add missing columns to existing tables (for DBs created before model changes)."""
    def has_column(table, column):
        result = db.session.execute(text(f"PRAGMA table_info({table})"))
        return any(row[1] == column for row in result)
    try:
        if not has_column('enrollments', 'remarks'):
            db.session.execute(text("ALTER TABLE enrollments ADD COLUMN remarks TEXT"))
        if not has_column('enrollments', 'updated_at'):
            db.session.execute(text("ALTER TABLE enrollments ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"))
        if not has_column('courses', 'seat_limit'):
            db.session.execute(text("ALTER TABLE courses ADD COLUMN seat_limit INTEGER"))
        if not has_column('courses', 'syllabus'):
            db.session.execute(text("ALTER TABLE courses ADD COLUMN syllabus TEXT"))
        if not has_column('courses', 'schedule'):
            db.session.execute(text("ALTER TABLE courses ADD COLUMN schedule VARCHAR(200)"))
        if not has_column('courses', 'semester'):
            db.session.execute(text("ALTER TABLE courses ADD COLUMN semester VARCHAR(20)"))
        if not has_column('faculty', 'department_id'):
            db.session.execute(text("ALTER TABLE faculty ADD COLUMN department_id INTEGER"))
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

def init_db():
    """Initialize database and create tables"""
    # Import models here to avoid circular imports
    from models.user import User
    from models.student import Student
    from models.faculty import Faculty
    from models.course import Course
    from models.department import Department
    from models.enrollment import Enrollment
    from models.audit_log import AuditLog
    from models.faculty_course import FacultyCourseAssignment
    from models.course_announcement import CourseAnnouncement
    from utils.auth import hash_password
    
    db.create_all()
    schema_upgrade()

    # Check if admin user exists
    admin = User.query.filter_by(email='admin@test.com').first()
    if not admin:
        # Create default admin user
        admin = User(
            name='System Administrator',
            email='admin@test.com',
            password=hash_password('admin123'),
            role='admin'
        )
        db.session.add(admin)
        
        # Create default faculty
        faculty1 = User(
            name='Dr. John Smith',
            email='faculty1@test.com',
            password=hash_password('faculty123'),
            role='faculty'
        )
        db.session.add(faculty1)
        db.session.flush()
        
        faculty_user = Faculty(user_id=faculty1.id)
        db.session.add(faculty_user)
        db.session.flush()
        # Assign faculty to CS department and some courses (after courses exist)
        
        # Create default student
        student1 = User(
            name='Alice Johnson',
            email='student1@test.com',
            password=hash_password('student123'),
            role='student'
        )
        db.session.add(student1)
        db.session.flush()
        
        student_user = Student(user_id=student1.id)
        db.session.add(student_user)
        db.session.commit()
        
        # Create departments
        dept1 = Department(name='Computer Science', code='CS')
        dept2 = Department(name='Information Technology', code='IT')
        dept3 = Department(name='Information Systems', code='IS')
        db.session.add_all([dept1, dept2, dept3])
        db.session.commit()
        
        # Create courses
        course1 = Course(name='Data Science', code='CS401', department_id=dept1.id, credits=3)
        course2 = Course(name='Machine Learning', code='CS402', department_id=dept1.id, credits=3)
        course3 = Course(name='Web Development', code='IT401', department_id=dept2.id, credits=3)
        course4 = Course(name='Database Management', code='IS401', department_id=dept3.id, credits=3, seat_limit=30)
        db.session.add_all([course1, course2, course3, course4])
        db.session.flush()
        course1.seat_limit = 25
        course2.seat_limit = 25
        course3.seat_limit = 30
        db.session.commit()

        # Assign faculty to department and courses
        fac = Faculty.query.filter_by(user_id=faculty1.id).first()
        if fac:
            fac.department_id = dept1.id
            db.session.add(FacultyCourseAssignment(faculty_id=fac.id, course_id=course1.id))
            db.session.add(FacultyCourseAssignment(faculty_id=fac.id, course_id=course2.id))
            db.session.commit()

        # Create enrollments
        enrollment1 = Enrollment(student_id=student_user.id, course_id=course1.id, status='enrolled')
        enrollment2 = Enrollment(student_id=student_user.id, course_id=course2.id, status='enrolled')
        db.session.add_all([enrollment1, enrollment2])
        db.session.commit()
