"""
Generate realistic sample data for Course Enrollment Analytics System
Creates ~60 students, ~10 faculty, departments, courses, and enrollments
"""
import csv
import random
from datetime import datetime, timedelta
import hashlib
import secrets

# Department codes and names
DEPARTMENTS = [
    ('CS', 'Computer Science'),
    ('IT', 'Information Technology'),
    ('IS', 'Information Systems'),
    ('EE', 'Electrical Engineering'),
    ('ME', 'Mechanical Engineering'),
    ('CE', 'Civil Engineering')
]

# Course templates by department
COURSES_BY_DEPT = {
    'CS': [
        ('CS101', 'Introduction to Programming', 3),
        ('CS201', 'Data Structures', 3),
        ('CS301', 'Database Systems', 3),
        ('CS401', 'Data Science', 3),
        ('CS402', 'Machine Learning', 3),
        ('CS403', 'Artificial Intelligence', 3),
        ('CS404', 'Software Engineering', 3),
        ('CS405', 'Computer Networks', 3),
    ],
    'IT': [
        ('IT101', 'Web Development Fundamentals', 3),
        ('IT201', 'Network Administration', 3),
        ('IT301', 'Cloud Computing', 3),
        ('IT401', 'Web Development', 3),
        ('IT402', 'Mobile App Development', 3),
        ('IT403', 'Cybersecurity', 3),
    ],
    'IS': [
        ('IS101', 'Business Information Systems', 3),
        ('IS201', 'Systems Analysis', 3),
        ('IS301', 'Enterprise Systems', 3),
        ('IS401', 'Database Management', 3),
        ('IS402', 'Business Intelligence', 3),
    ],
    'EE': [
        ('EE101', 'Circuit Analysis', 3),
        ('EE201', 'Digital Electronics', 3),
        ('EE301', 'Power Systems', 3),
        ('EE401', 'Embedded Systems', 3),
    ],
    'ME': [
        ('ME101', 'Engineering Mechanics', 3),
        ('ME201', 'Thermodynamics', 3),
        ('ME301', 'Machine Design', 3),
        ('ME401', 'Manufacturing Processes', 3),
    ],
    'CE': [
        ('CE101', 'Structural Analysis', 3),
        ('CE201', 'Construction Materials', 3),
        ('CE301', 'Geotechnical Engineering', 3),
        ('CE401', 'Transportation Engineering', 3),
    ]
}

# First names and last names for realistic names
FIRST_NAMES = [
    'John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'James', 'Jessica',
    'Robert', 'Ashley', 'William', 'Amanda', 'Richard', 'Melissa', 'Joseph', 'Nicole',
    'Thomas', 'Michelle', 'Charles', 'Kimberly', 'Christopher', 'Amy', 'Daniel', 'Angela',
    'Matthew', 'Lisa', 'Anthony', 'Nancy', 'Mark', 'Karen', 'Donald', 'Betty',
    'Steven', 'Helen', 'Paul', 'Sandra', 'Andrew', 'Donna', 'Joshua', 'Carol',
    'Kenneth', 'Ruth', 'Kevin', 'Sharon', 'Brian', 'Michelle', 'George', 'Laura',
    'Edward', 'Sarah', 'Ronald', 'Kimberly', 'Timothy', 'Deborah', 'Jason', 'Elizabeth',
    'Jeffrey', 'Jennifer', 'Ryan', 'Maria', 'Jacob', 'Susan', 'Gary', 'Margaret'
]

LAST_NAMES = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas', 'Taylor',
    'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris', 'Sanchez',
    'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker', 'Young', 'Allen', 'King',
    'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores', 'Green', 'Adams',
    'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts'
]

def hash_password(password):
    """Hash password (same as utils/auth.py)"""
    try:
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    except ImportError:
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"

def generate_students(num=60):
    """Generate student data"""
    students = []
    for i in range(1, num + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        name = f"{first} {last}"
        email = f"student{i}@college.edu"
        student_id = f"STU{2024000 + i:04d}"
        password = "student123"  # Default password
        students.append({
            'name': name,
            'email': email,
            'password': password,
            'role': 'student',
            'student_id': student_id
        })
    return students

def generate_faculty(num=10):
    """Generate faculty data"""
    titles = ['Dr.', 'Prof.', 'Dr.', 'Prof.', 'Dr.']
    faculty = []
    dept_codes = [d[0] for d in DEPARTMENTS]
    for i in range(1, num + 1):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        title = random.choice(titles)
        name = f"{title} {first} {last}"
        email = f"faculty{i}@college.edu"
        employee_id = f"FAC{1000 + i:04d}"
        password = "faculty123"
        # Assign department (distribute evenly)
        dept_code = dept_codes[(i - 1) % len(dept_codes)]
        faculty.append({
            'name': name,
            'email': email,
            'password': password,
            'role': 'faculty',
            'employee_id': employee_id,
            'department_code': dept_code
        })
    return faculty

def write_csv(filename, data, headers):
    """Write data to CSV"""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

if __name__ == '__main__':
    print("Generating sample data...")
    
    students = generate_students(60)
    write_csv('students.csv', students, ['name', 'email', 'password', 'role', 'student_id'])
    print(f"Generated {len(students)} students -> students.csv")
    
    faculty = generate_faculty(10)
    write_csv('faculty.csv', faculty, ['name', 'email', 'password', 'role', 'employee_id', 'department_code'])
    print(f"Generated {len(faculty)} faculty -> faculty.csv")
    
    print("\nNext: Run 'python import_sample_data.py' to load into database")
