# Role-Based Access Control (RBAC) – Detailed Analysis

## Overview

The Course Enrollment Analytics Web Application implements a structured Role-Based Access Control (RBAC) mechanism to ensure secure, organized, and role-specific access to system functionalities. The system defines three primary user roles: Admin, Faculty, and Student, where each role is assigned distinct permissions aligned with institutional responsibilities. RBAC ensures that users can access only the features relevant to their role, thereby improving security, data integrity, and operational efficiency.

## Role Definitions

### 1. Admin Role

The Admin role has full system privileges and acts as the highest authority within the application.

#### Permissions and Responsibilities:

**User Management:**
- Create, update, and delete user accounts (students, faculty, and other admins)
- Assign and modify user roles
- Control system access and authentication
- View all user information and activity

**Course Management:**
- Create and manage courses
- Define course codes, names, credits, and descriptions
- Assign courses to departments
- Set enrollment capacity limits (future enhancement)
- Modify course details

**Department Management:**
- Create and manage academic departments
- Define department codes and names
- Organize courses under departments

**Analytics and Reporting:**
- Complete access to enrollment analytics
- Course-wise enrollment counts and statistics
- Department-wise enrollment distribution
- Trend analysis over time
- Identification of high-demand courses
- Comprehensive visual analytics using tables and charts
- Support academic planning and decision-making

**System Administration:**
- Monitor system activity
- Ensure smooth application operation
- Access all system features and configurations

#### Technical Implementation:
- Routes protected with `@role_required('admin')` decorator
- Access to `/admin/*` routes
- Full CRUD operations on all entities

---

### 2. Faculty Role

The Faculty role is designed to support academic and instructional responsibilities while restricting administrative privileges.

#### Permissions and Responsibilities:

**Viewing Capabilities:**
- Access dedicated faculty dashboard
- View course-wise enrollment analytics
- View department-wise enrollment statistics
- Analyze enrollment trends relevant to their department or subject
- View list of students enrolled in courses

**Student Information:**
- View enrolled student details
- Access student enrollment information
- View course enrollment status and grades

**Restrictions:**
- Cannot modify system configurations
- Cannot manage users or create accounts
- Cannot alter course definitions
- Cannot access administrative features
- Ensures separation of duties

#### Technical Implementation:
- Routes protected with `@role_required('faculty')` decorator
- Access to `/faculty/*` routes
- Read-only access to analytics and student data

---

### 3. Student Role

The Student role provides limited and personalized access focused on enrollment activities.

#### Permissions and Responsibilities:

**Personal Enrollment:**
- View available courses (future enhancement)
- Check seat availability (future enhancement)
- Enroll in courses according to eligibility and seat limits (future enhancement)
- View only their own enrollment details
- View assigned courses through student dashboard
- Access personal academic information

**Restrictions:**
- Strictly restricted from accessing analytics
- Cannot view other users' data
- Cannot access administrative features
- Cannot modify any system data
- Ensures privacy and prevents unauthorized data exposure

#### Technical Implementation:
- Routes protected with `@role_required('student')` decorator
- Access to `/student/*` routes
- Personal data access only (filtered by user_id)

---

## RBAC Enforcement Mechanism

### Authentication Level

1. **Secure Login:**
   - Users authenticate using email and password
   - Passwords are hashed using SHA-256 with salt
   - Session-based authentication maintains user state

2. **Session Management:**
   - User sessions store:
     - `user_id`: Unique user identifier
     - `name`: User's display name
     - `email`: User's email address
     - `role`: User's role (admin, faculty, student)
   - Sessions persist throughout user interaction
   - Sessions cleared on logout

### Authorization Level

1. **Route Protection:**
   - `@login_required` decorator ensures user is authenticated
   - `@role_required('role1', 'role2', ...)` decorator restricts access to specific roles
   - Unauthorized access attempts are blocked

2. **Feature-Level Checks:**
   - Each route validates user role before processing
   - Data queries filtered by role (e.g., students see only their data)
   - API endpoints validate role permissions

3. **Error Handling:**
   - Unauthorized access attempts return 401/403 status codes
   - User-friendly error messages displayed
   - Graceful handling maintains system integrity

## Implementation Details

### Decorator Functions

```python
@login_required
def protected_route():
    """Requires user to be logged in"""
    pass

@role_required('admin')
def admin_only_route():
    """Requires admin role"""
    pass

@role_required('faculty', 'admin')
def faculty_or_admin_route():
    """Requires faculty or admin role"""
    pass
```

### Route Protection Examples

**Admin Routes:**
- `/admin/dashboard` - Admin dashboard
- `/admin/users` - User management
- `/admin/users/create` - Create users
- `/admin/courses` - Course management
- `/admin/courses/create` - Create courses
- `/admin/departments` - Department management
- `/admin/analytics/api/*` - Analytics APIs

**Faculty Routes:**
- `/faculty/dashboard` - Faculty dashboard
- `/faculty/students` - View enrolled students
- `/faculty/analytics/api/*` - Analytics APIs (read-only)

**Student Routes:**
- `/student/dashboard` - Student dashboard
- `/student/courses` - View enrolled courses

### Data Access Control

**Student Data Filtering:**
```python
# Students can only see their own data
user_id = session.get('user_id')
student = Student.query.filter_by(user_id=user_id).first()
enrollments = Enrollment.query.filter_by(student_id=student.id).all()
```

**Faculty Data Access:**
```python
# Faculty can see all enrollments but cannot modify
enrollments = Enrollment.query.filter_by(status='enrolled').all()
```

**Admin Data Access:**
```python
# Admin can access all data
all_users = User.query.all()
all_enrollments = Enrollment.query.all()
```

## Security Features

1. **Password Security:**
   - SHA-256 hashing with random salt
   - Passwords never stored in plain text
   - Secure password verification

2. **Session Security:**
   - Flask session management
   - Session data stored server-side
   - Session timeout on logout

3. **Route Security:**
   - All protected routes require authentication
   - Role-based access enforced at route level
   - Unauthorized requests rejected

4. **Data Privacy:**
   - Students see only their own data
   - Faculty see relevant academic data
   - Admin sees all data

## Access Control Matrix

| Feature | Admin | Faculty | Student |
|---------|-------|---------|---------|
| View Dashboard | ✅ | ✅ | ✅ |
| Manage Users | ✅ | ❌ | ❌ |
| Create Courses | ✅ | ❌ | ❌ |
| Manage Departments | ✅ | ❌ | ❌ |
| View All Analytics | ✅ | ✅ | ❌ |
| View All Students | ✅ | ✅ | ❌ |
| View Own Enrollments | ✅ | ❌ | ✅ |
| Modify System Config | ✅ | ❌ | ❌ |
| View Course Statistics | ✅ | ✅ | ❌ |
| View Department Stats | ✅ | ✅ | ❌ |

## Best Practices Implemented

1. **Principle of Least Privilege:**
   - Each role has minimum necessary permissions
   - Students have most restricted access
   - Faculty have moderate access
   - Admin have full access

2. **Separation of Duties:**
   - Faculty cannot modify courses they teach
   - Students cannot view other students' data
   - Clear boundaries between roles

3. **Defense in Depth:**
   - Multiple layers of security checks
   - Authentication + Authorization
   - Route-level + Feature-level protection

4. **Audit Trail:**
   - User actions logged (future enhancement)
   - Session tracking
   - Error logging

## Future Enhancements

1. **Granular Permissions:**
   - Permission-based system within roles
   - Custom permission sets
   - Dynamic role assignment

2. **Activity Logging:**
   - Track user actions
   - Audit trail for sensitive operations
   - Security event monitoring

3. **Role Hierarchies:**
   - Sub-roles within main roles
   - Department-specific faculty roles
   - Student year-based permissions

4. **Advanced Features:**
   - Course enrollment capacity management
   - Prerequisite checking
   - Waitlist functionality
   - Grade management for faculty

## Conclusion

The RBAC implementation in the Course Enrollment Analytics System provides a robust, secure, and scalable access control mechanism. By clearly defining role boundaries and enforcing them at multiple levels, the system ensures:

- **Security:** Unauthorized access is prevented
- **Data Integrity:** Users can only access appropriate data
- **Operational Efficiency:** Role-specific dashboards improve usability
- **Scalability:** System can accommodate future role additions
- **Compliance:** Adheres to best practices in web application security

The RBAC model ensures a secure, scalable, and institution-ready system that supports academic operations while maintaining strict security standards and access management principles.
