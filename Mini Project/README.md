# Course Enrollment Analytics System

A comprehensive, production-ready web application for managing course enrollments with role-based access control, analytics, and data visualization.

## Project Overview

The Course Enrollment Analytics System is a full-stack web application designed for educational institutions to manage student enrollments, track course statistics, and provide analytics dashboards for administrators, faculty, and students.

## Architecture

### Technology Stack
- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Data Processing**: Pandas
- **Visualization**: Chart.js
- **Authentication**: Session-based with password hashing
- **Security**: Role-Based Access Control (RBAC)

### Project Structure
```
Course Enrollment Analytics System/
├── app.py                 # Main application entry point
├── models/                # Database models
│   ├── database.py       # Database configuration
│   ├── user.py           # User model
│   ├── student.py        # Student model
│   ├── faculty.py        # Faculty model
│   ├── course.py         # Course model
│   ├── department.py     # Department model
│   └── enrollment.py     # Enrollment model
├── routes/                # Flask route handlers
│   ├── auth.py           # Authentication routes
│   ├── admin.py          # Admin routes
│   ├── faculty.py        # Faculty routes
│   └── student.py        # Student routes
├── services/              # Business logic layer
│   └── analytics_service.py  # Analytics processing
├── utils/                 # Utility functions
│   └── auth.py           # Authentication utilities
├── templates/             # Jinja2 templates
│   ├── base.html         # Base template
│   ├── auth/             # Authentication templates
│   ├── admin/            # Admin templates
│   ├── faculty/          # Faculty templates
│   └── student/          # Student templates
├── static/                # Static files
│   ├── css/              # Stylesheets
│   └── js/               # JavaScript files
├── tests/                 # Unit tests
│   └── test_auth.py      # Authentication tests
└── requirements.txt       # Python dependencies
```

## Features

### Role-Based Access Control

#### Admin
- Manage users (create, view all users)
- Manage courses and departments
- View comprehensive analytics dashboard
- Access to all system features

#### Faculty
- View enrolled students
- View course-wise and department-wise analytics
- Access student enrollment information

#### Student
- View personal enrollment details
- View assigned courses only
- Access personal academic information

### Key Features
- Secure authentication with password hashing
- Session management
- Real-time analytics with Chart.js visualizations
- Data processing with Pandas
- Responsive design
- Error handling and logging
- RESTful API endpoints

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory**
   ```bash
   cd "Course Enrollment Analytics System"
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:5000/`
   - The application will automatically initialize the database and create default users

## Default Credentials

The system creates default users on first run:

- **Admin**
  - Email: `admin@test.com`
  - Password: `admin123`

- **Faculty**
  - Email: `faculty1@test.com`
  - Password: `faculty123`

- **Student**
  - Email: `student1@test.com`
  - Password: `student123`

## Usage Guide

### For Administrators

1. **Login** with admin credentials
2. **Dashboard** - View overall statistics and analytics
3. **Manage Users** - Create new users (admin, faculty, or student)
4. **Manage Courses** - Add new courses and assign to departments
5. **Manage Departments** - Create and manage academic departments

### For Faculty

1. **Login** with faculty credentials
2. **Dashboard** - View course and department enrollment statistics
3. **Students** - View list of enrolled students

### For Students

1. **Login** with student credentials
2. **Dashboard** - View personal enrollment information
3. **Courses** - View enrolled courses and grades

## Database Schema

### Tables
- **users** - User accounts and authentication
- **students** - Student profiles
- **faculty** - Faculty profiles
- **courses** - Course information
- **departments** - Department information
- **enrollments** - Student-course enrollment relationships

## API Endpoints

### Authentication
- `GET /login` - Login page
- `POST /login` - Authenticate user
- `POST /logout` - Logout user

### Admin APIs
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/users` - List all users
- `POST /admin/users/create` - Create new user
- `GET /admin/courses` - List all courses
- `POST /admin/courses/create` - Create new course
- `GET /admin/departments` - List all departments
- `POST /admin/departments/create` - Create new department
- `GET /admin/analytics/api/course-stats` - Course statistics API
- `GET /admin/analytics/api/department-stats` - Department statistics API

### Faculty APIs
- `GET /faculty/dashboard` - Faculty dashboard
- `GET /faculty/students` - View enrolled students
- `GET /faculty/analytics/api/course-stats` - Course statistics API
- `GET /faculty/analytics/api/department-stats` - Department statistics API

### Student APIs
- `GET /student/dashboard` - Student dashboard
- `GET /student/courses` - View enrolled courses

## Security Features

- Password hashing using SHA-256 with salt
- Session-based authentication
- Role-based route protection
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (Jinja2 auto-escaping)
- CSRF protection (Flask sessions)

### Role-Based Access Control (RBAC)

The system implements comprehensive RBAC with three distinct roles:

- **Admin**: Full system access, user management, course/department management, complete analytics
- **Faculty**: View enrollments, course/department analytics, student information (read-only)
- **Student**: Personal enrollment view only, restricted data access

For detailed RBAC analysis, see [docs/RBAC_ANALYSIS.md](docs/RBAC_ANALYSIS.md)

For security documentation, see [docs/SECURITY.md](docs/SECURITY.md)

## Testing

Run tests using:
```bash
python -m pytest tests/
```

Or run specific test file:
```bash
python tests/test_auth.py
```

## Production Deployment

### Environment Variables
Set the following environment variables for production:

```bash
export SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///production.db"
export FLASK_DEBUG="False"
```

### Security Checklist
- [ ] Change default SECRET_KEY
- [ ] Set FLASK_DEBUG=False
- [ ] Use production database (PostgreSQL recommended)
- [ ] Enable HTTPS
- [ ] Set up proper logging
- [ ] Configure firewall rules
- [ ] Regular database backups

## Future Enhancements

- Email notifications
- Grade management system
- Course prerequisites
- Enrollment capacity limits
- Advanced reporting and exports
- Multi-semester support
- Integration with external systems
- Mobile app support
- Real-time notifications
- Advanced analytics and machine learning insights

## Troubleshooting

### Database Issues
If you encounter database errors, delete the `course_enrollment.db` file and restart the application to recreate the database.

### Port Already in Use
If port 5000 is already in use, modify `app.py` to use a different port:
```python
app.run(debug=True, port=5001)
```

### Module Not Found Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## License

This project is developed for educational purposes.

## Support

For issues or questions, please refer to the project documentation or contact the development team.

## Acknowledgments

- Flask Framework
- SQLAlchemy ORM
- Chart.js
- Pandas

---

**Version**: 1.0.0  
**Last Updated**: 2026  
**Status**: Production Ready
