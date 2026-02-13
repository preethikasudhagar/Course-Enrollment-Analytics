"""
Import sample data (students.csv, faculty.csv) into the database
Also creates courses, departments, faculty-course assignments, and enrollments
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models.database import db, init_db
from models.user import User
from models.student import Student
from models.faculty import Faculty
from models.course import Course
from models.department import Department
from models.enrollment import Enrollment
from models.faculty_course import FacultyCourseAssignment
from utils.auth import hash_password
import csv
import random
from datetime import datetime, timedelta

DEPARTMENTS = [
    ('CS', 'Computer Science'),
    ('IT', 'Information Technology'),
    ('IS', 'Information Systems'),
    ('EE', 'Electrical Engineering'),
    ('ME', 'Mechanical Engineering'),
    ('CE', 'Civil Engineering')
]

COURSES_BY_DEPT = {
    'CS': [
        ('CS101', 'Introduction to Programming', 3, 30),
        ('CS201', 'Data Structures', 3, 25),
        ('CS301', 'Database Systems', 3, 30),
        ('CS401', 'Data Science', 3, 25),
        ('CS402', 'Machine Learning', 3, 25),
        ('CS403', 'Artificial Intelligence', 3, 20),
        ('CS404', 'Software Engineering', 3, 30),
        ('CS405', 'Computer Networks', 3, 25),
    ],
    'IT': [
        ('IT101', 'Web Development Fundamentals', 3, 30),
        ('IT201', 'Network Administration', 3, 25),
        ('IT301', 'Cloud Computing', 3, 30),
        ('IT401', 'Web Development', 3, 30),
        ('IT402', 'Mobile App Development', 3, 25),
        ('IT403', 'Cybersecurity', 3, 20),
    ],
    'IS': [
        ('IS101', 'Business Information Systems', 3, 30),
        ('IS201', 'Systems Analysis', 3, 25),
        ('IS301', 'Enterprise Systems', 3, 30),
        ('IS401', 'Database Management', 3, 30),
        ('IS402', 'Business Intelligence', 3, 25),
    ],
    'EE': [
        ('EE101', 'Circuit Analysis', 3, 30),
        ('EE201', 'Digital Electronics', 3, 25),
        ('EE301', 'Power Systems', 3, 30),
        ('EE401', 'Embedded Systems', 3, 25),
    ],
    'ME': [
        ('ME101', 'Engineering Mechanics', 3, 30),
        ('ME201', 'Thermodynamics', 3, 25),
        ('ME301', 'Machine Design', 3, 30),
        ('ME401', 'Manufacturing Processes', 3, 25),
    ],
    'CE': [
        ('CE101', 'Structural Analysis', 3, 30),
        ('CE201', 'Construction Materials', 3, 25),
        ('CE301', 'Geotechnical Engineering', 3, 30),
        ('CE401', 'Transportation Engineering', 3, 25),
    ]
}

def import_data():
    """Import all sample data"""
    with app.app_context():
        print("Initializing database...")
        init_db()
        
        # 1. Create/ensure departments
        print("\n1. Creating departments...")
        dept_map = {}
        for code, name in DEPARTMENTS:
            dept = Department.query.filter_by(code=code).first()
            if not dept:
                dept = Department(name=name, code=code)
                db.session.add(dept)
                db.session.flush()
            dept_map[code] = dept
        db.session.commit()
        print(f"   OK: {len(dept_map)} departments ready")
        
        # 2. Create courses
        print("\n2. Creating courses...")
        course_map = {}
        for dept_code, courses_list in COURSES_BY_DEPT.items():
            dept = dept_map[dept_code]
            for code, name, credits, seat_limit in courses_list:
                course = Course.query.filter_by(code=code).first()
                if not course:
                    course = Course(
                        name=name,
                        code=code,
                        department_id=dept.id,
                        credits=credits,
                        seat_limit=seat_limit,
                        schedule=f"Mon/Wed/Fri {random.choice(['9-10 AM', '10-11 AM', '11-12 PM', '2-3 PM', '3-4 PM'])}",
                        semester=random.choice(['Fall 2024', 'Spring 2025', 'Fall 2025'])
                    )
                    db.session.add(course)
                    db.session.flush()
                course_map[code] = course
        db.session.commit()
        print(f"   OK: {len(course_map)} courses created")
        
        # 3. Import students from CSV
        print("\n3. Importing students...")
        students_created = 0
        student_list = []
        csv_path = os.path.join(os.path.dirname(__file__), 'students.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if User.query.filter_by(email=row['email']).first():
                        continue
                    user = User(
                        name=row['name'],
                        email=row['email'],
                        password=hash_password(row['password']),
                        role='student'
                    )
                    db.session.add(user)
                    db.session.flush()
                    student = Student(user_id=user.id, student_id=row.get('student_id'))
                    db.session.add(student)
                    student_list.append(student)
                    students_created += 1
            db.session.commit()
            print(f"   OK: {students_created} students imported")
        else:
            print(f"   WARNING: students.csv not found at {csv_path}")
        
        # 4. Import faculty from CSV
        print("\n4. Importing faculty...")
        faculty_created = 0
        faculty_list = []
        csv_path = os.path.join(os.path.dirname(__file__), 'faculty.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if User.query.filter_by(email=row['email']).first():
                        continue
                    user = User(
                        name=row['name'],
                        email=row['email'],
                        password=hash_password(row['password']),
                        role='faculty'
                    )
                    db.session.add(user)
                    db.session.flush()
                    dept = dept_map.get(row.get('department_code', 'CS'))
                    faculty = Faculty(
                        user_id=user.id,
                        employee_id=row.get('employee_id'),
                        department_id=dept.id if dept else None
                    )
                    db.session.add(faculty)
                    faculty_list.append(faculty)
                    faculty_created += 1
            db.session.commit()
            print(f"   OK: {faculty_created} faculty imported")
        else:
            print(f"   WARNING: faculty.csv not found at {csv_path}")
        
        # 5. Assign courses to faculty (each faculty gets 2-4 courses from their department)
        print("\n5. Assigning courses to faculty...")
        assignments_created = 0
        for fac in faculty_list:
            if not fac.department_id:
                continue
            dept = Department.query.get(fac.department_id)
            if not dept:
                continue
            dept_code = dept.code
            dept_courses = [c for code, c in course_map.items() if code.startswith(dept_code)]
            num_courses = random.randint(2, min(4, len(dept_courses)))
            selected = random.sample(dept_courses, num_courses)
            for course in selected:
                existing = FacultyCourseAssignment.query.filter_by(
                    faculty_id=fac.id, course_id=course.id
                ).first()
                if not existing:
                    db.session.add(FacultyCourseAssignment(faculty_id=fac.id, course_id=course.id))
                    assignments_created += 1
        db.session.commit()
        print(f"   OK: {assignments_created} faculty-course assignments created")
        
        # 6. Create enrollments (each student enrolls in 3-6 courses)
        print("\n6. Creating enrollments...")
        enrollments_created = 0
        waitlisted_created = 0
        
        # Get all existing students if student_list is empty (students already imported)
        if not student_list:
            student_list = Student.query.all()
            print(f"   Using {len(student_list)} existing students")
        
        all_courses = list(course_map.values())
        
        # First pass: Create enrollments up to seat limits
        for student in student_list:
            num_enrollments = random.randint(3, 6)
            selected_courses = random.sample(all_courses, min(num_enrollments, len(all_courses)))
            for course in selected_courses:
                existing = Enrollment.query.filter_by(
                    student_id=student.id, course_id=course.id
                ).first()
                if existing:
                    continue
                # Check seat limit
                enrolled_count = Enrollment.query.filter_by(
                    course_id=course.id, status='enrolled'
                ).count()
                if course.seat_limit and enrolled_count >= course.seat_limit:
                    status = 'waitlisted'
                    waitlisted_created += 1
                else:
                    status = 'enrolled'
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    status=status,
                    enrollment_date=datetime.now() - timedelta(days=random.randint(1, 90))
                )
                db.session.add(enrollment)
                enrollments_created += 1
        
        db.session.commit()
        
        # Second pass: Intentionally over-enroll some popular courses to create waitlisted students
        # Select 5-8 popular courses and add extra enrollments beyond seat limit
        print("\n7. Creating waitlisted enrollments for over-capacity courses...")
        popular_courses = sorted([c for c in all_courses if c.seat_limit], 
                                key=lambda c: c.seat_limit or 0, reverse=True)[:8]
        waitlisted_added = 0
        
        for course in popular_courses:
            if not course.seat_limit:
                continue
            
            # Get current enrollment count
            enrolled_count = Enrollment.query.filter_by(
                course_id=course.id, status='enrolled'
            ).count()
            
            # Add 5-12 waitlisted students per popular course (beyond seat limit)
            extra_waitlisted = random.randint(5, 12)
            
            # Find students not already enrolled/waitlisted in this course
            existing_enrollment_student_ids = set(
                e.student_id for e in Enrollment.query.filter_by(course_id=course.id).all()
            )
            available_students = [s for s in student_list if s.id not in existing_enrollment_student_ids]
            
            if available_students:
                selected_students = random.sample(available_students, min(extra_waitlisted, len(available_students)))
                for student in selected_students:
                    enrollment = Enrollment(
                        student_id=student.id,
                        course_id=course.id,
                        status='waitlisted',
                        enrollment_date=datetime.now() - timedelta(days=random.randint(1, 90))
                    )
                    db.session.add(enrollment)
                    enrollments_created += 1
                    waitlisted_added += 1
        
        db.session.commit()
        print(f"   OK: {waitlisted_added} additional waitlisted enrollments created")
        print(f"   Total: {enrollments_created} enrollments created ({waitlisted_created + waitlisted_added} waitlisted)")
        
        # Summary
        print("\n" + "="*50)
        print("IMPORT SUMMARY")
        print("="*50)
        print(f"Departments: {Department.query.count()}")
        print(f"Courses: {Course.query.count()}")
        print(f"Students: {Student.query.count()}")
        print(f"Faculty: {Faculty.query.count()}")
        print(f"Faculty-Course Assignments: {FacultyCourseAssignment.query.count()}")
        print(f"Enrollments: {Enrollment.query.count()}")
        print(f"Active Enrollments: {Enrollment.query.filter_by(status='enrolled').count()}")
        print(f"Waitlisted: {Enrollment.query.filter_by(status='waitlisted').count()}")
        print("\nOK: Sample data import complete!")
        print("\nLogin credentials:")
        print("  Admin: admin@test.com / admin123")
        print("  Faculty: faculty1@college.edu / faculty123 (or faculty2-10)")
        print("  Student: student1@college.edu / student123 (or student2-60)")

if __name__ == '__main__':
    import_data()
