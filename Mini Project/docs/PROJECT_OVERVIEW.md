# Course Enrollment Analytics Web Application — Project Overview

## 1. Introduction

The **Course Enrollment Analytics Web Application** is a college-level web system for managing and analyzing course enrollments. It provides role-based dashboards (Admin, Faculty, Student), enrollment management, seat allocation, and analytics with charts and reports.

---

## 2. Technologies Used

### Backend
| Technology | Version / Purpose |
|------------|-------------------|
| **Python** | 3.x |
| **Flask** | ≥3.0.0 — Web framework |
| **Flask-SQLAlchemy** | ≥3.1.0 — ORM and database integration |
| **SQLite** | Default DB (configurable via `DATABASE_URL`) |
| **Pandas** | ≥2.0.0 — Analytics and data processing |
| **Werkzeug** | ≥3.0.0 — WSGI utilities |
| **bcrypt** | ≥4.0.0 — Password hashing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure |
| **Jinja2** | Server-side templating (Flask) |
| **CSS3** | Styling (custom `style.css`) |
| **JavaScript** | Interactivity, Chart.js integration |
| **Chart.js** | 4.4.0 (CDN) — Bar, line, pie/donut charts |

### Architecture
- **MVC-style**: Routes → Services/Models → Templates
- **Blueprint-based** routing: `auth`, `admin`, `faculty`, `student`
- **RBAC**: Role-Based Access Control with permission enums and decorators

---

## 3. Project Structure (Step by Step)

### 3.1 Directory Layout

```
Mini Project/
├── app.py                    # Application entry point, blueprint registration
├── requirements.txt         # Python dependencies
├── course_enrollment.db     # SQLite database (created at runtime)
│
├── models/                  # Database models
│   ├── __init__.py
│   ├── database.py         # DB config, init_db(), schema_upgrade()
│   ├── user.py             # User (auth, role)
│   ├── student.py           # Student profile
│   ├── faculty.py           # Faculty profile
│   ├── course.py            # Course (seat_limit, department, etc.)
│   ├── department.py        # Department
│   ├── enrollment.py        # Enrollment (student–course, status)
│   ├── faculty_course.py    # Faculty–course assignment
│   ├── course_announcement.py
│   └── audit_log.py         # Security/audit events
│
├── routes/                  # Flask blueprints (controllers)
│   ├── __init__.py
│   ├── auth.py             # Login, logout, change password
│   ├── admin.py            # Admin-only routes
│   ├── faculty.py           # Faculty-only routes
│   └── student.py           # Student-only routes
│
├── services/                # Business logic
│   ├── __init__.py
│   └── analytics_service.py # Enrollment stats, trends, faculty-scoped analytics
│
├── utils/                   # Shared utilities
│   ├── __init__.py
│   ├── auth.py             # login_required, role_required, hash_password, verify_password
│   └── permissions.py      # Permission enum, ROLE_PERMISSIONS, require_permission
│
├── templates/               # Jinja2 HTML templates
│   ├── base.html           # Layout, topbar, role-based sidebar
│   ├── error.html
│   ├── auth/               # login, change_password
│   ├── admin/               # dashboard, users, courses, enrollments, analytics, etc.
│   ├── faculty/             # dashboard, my_courses, students, analytics, etc.
│   └── student/             # dashboard, courses, available_courses, profile, etc.
│
├── static/
│   ├── css/style.css       # Main styles (dashboard, charts, alerts, badges)
│   └── js/
│       ├── main.js         # Sidebar toggle, UI behavior
│       └── rbac.js         # Role-based client-side helpers
│
├── data/                    # Sample data and import scripts
│   ├── generate_sample_data.py  # Generates students.csv, faculty.csv
│   ├── import_sample_data.py     # Imports CSVs, creates enrollments + waitlisted
│   ├── students.csv
│   └── faculty.csv
│
├── docs/                    # Documentation
│   ├── PROJECT_OVERVIEW.md  # This file
│   ├── RBAC_AND_ENROLLMENT.md
│   └── FACULTY_MODULE_RBAC.md
│
└── tests/
    ├── __init__.py
    └── test_auth.py
```

### 3.2 Data Flow (Step by Step)

1. **Request** → Flask (`app.py`) routes to the correct blueprint by URL prefix (`/admin`, `/faculty`, `/student`, or none for auth).
2. **Auth** → `@login_required` and `@role_required` (and optionally `@require_permission`) enforce access.
3. **Business logic** → Routes use **models** (User, Student, Faculty, Course, Department, Enrollment, etc.) and **AnalyticsService** for analytics.
4. **Response** → Routes pass data to **Jinja2 templates**; templates use Chart.js for charts where needed.
5. **Database** → SQLAlchemy talks to SQLite; `init_db()` creates tables and runs `schema_upgrade()` for existing DBs.

### 3.3 Database Schema (Main Entities)

- **users** — id, name, email, password, role (admin/faculty/student)
- **students** — id, user_id, student_id
- **faculty** — id, user_id, department_id, employee_id
- **departments** — id, name, code
- **courses** — id, name, code, department_id, credits, seat_limit, schedule, semester, etc.
- **enrollments** — id, student_id, course_id, status (enrolled/waitlisted/withdrawn/etc.), grade, remarks, enrollment_date
- **faculty_course_assignments** — faculty_id, course_id (many-to-many)
- **audit_logs** — event_type, user_id, route, details, timestamp
- **course_announcements** — course_id, faculty_id, title, body, created_at

---

## 4. Role-Based Performance (What Each Role Can Do)

### 4.1 Admin

**Purpose:** Full system control and institution-wide enrollment analytics.

| Area | Capabilities |
|------|----------------|
| **Dashboard** | Summary counts (users, students, faculty, courses, departments, enrollments, waitlisted). Quick actions. Charts: Department distribution (pie), Course-wise enrollment (bar), Enrollment trends (line). Option to refresh sample data. |
| **User management** | Manage Students list; Manage Faculty list; Role assignment (Student/Faculty only). Create user; Update user (name, email, optional password); Delete user; Assign role. |
| **Course management** | List all courses; Add course; Edit course; Delete course. Seat allocation (set/clear seat limits per course). Department mapping (course ↔ department). Faculty ↔ Course mapping (assign courses and department to faculty). |
| **Enrollment management** | View all enrollments; Approve/override enrollments (with `?mode=override`); Prevent over-enrollments via Seat Allocation. Override enrollment status (e.g. force enroll/waitlist). |
| **Analytics & reports** | Analytics overview (capacity utilization, course/department stats, trends, high/low demand). Course-wise enrollment; Department-wise enrollment; High/Low demand courses; Enrollment trends. All charts use institution-wide data. |
| **System** | Audit logs (view security events). Admin profile. Change password. Logout. |

**Permissions (examples):** CREATE_USER, UPDATE_USER, DELETE_USER, VIEW_ALL_USERS, ASSIGN_ROLES, CREATE_COURSE, UPDATE_COURSE, DELETE_COURSE, VIEW_ALL_COURSES, MANAGE_SEAT_LIMITS, VIEW_ALL_ENROLLMENTS, OVERRIDE_ENROLLMENT, VIEW_SYSTEM_ANALYTICS, VIEW_AUDIT_LOGS, etc.

---

### 4.2 Faculty

**Purpose:** Manage and analyze only **assigned courses** and **assigned department**.

| Area | Capabilities |
|------|----------------|
| **Dashboard** | Summary: assigned courses count, total enrolled students, seat utilization (avg %), department enrollment. Alerts: over-enrolled and under-enrolled courses. Waitlisted students table. Charts: Course enrollment (assigned only), Department distribution (own department), Enrollment trends (assigned courses). Enrolled students table. |
| **Academic** | **My courses** — list of assigned courses; course detail (syllabus, schedule). **Enrolled students** — list students in assigned courses; search/filter; view student profile; update enrollment status/remarks; export CSV. |
| **Analytics** | **Course analytics** — charts and tables for assigned courses only (utilization, trends, high/low demand). **Academic monitoring** — waitlisted students, cutoff alerts, links to manage remarks. |
| **Communication** | **Announcements** — create and view course announcements for assigned courses. |
| **Profile & security** | View profile (with department); Change password; Logout. |

**Restrictions:**  
- No access to admin routes or global user/course management.  
- Data filtered by `FacultyCourseAssignment` and (where applicable) `faculty.department_id`.  
- Permissions: VIEW_STUDENT_ENROLLMENTS, VIEW_COURSE_STATISTICS, UPDATE_ENROLLMENT_STATUS, ADD_ENROLLMENT_REMARKS, VIEW_COURSE_ANALYTICS, VIEW_DEPARTMENT_ANALYTICS, VIEW_ENROLLMENT_TRENDS (all scoped to assigned courses/department).

---

### 4.3 Student

**Purpose:** View own enrollments and enroll/withdraw from courses.

| Area | Capabilities |
|------|----------------|
| **Dashboard** | Overview of own enrollment status and quick links. |
| **Courses** | **Available courses** — browse courses; see capacity/available seats; enroll (subject to seat limit; may get waitlisted). **My enrollments** — list of enrolled courses. **Enrollment actions** — enroll in new courses or withdraw from enrolled courses. |
| **Profile & settings** | View profile; Change password; Logout. |

**Restrictions:**  
- Can only see and modify own enrollments.  
- Permissions: VIEW_OWN_ENROLLMENTS, ENROLL_IN_COURSE, WITHDRAW_FROM_COURSE.

---

## 5. Key Features (Step by Step)

### 5.1 Authentication & Security

1. **Login** — Email + password; session stores `user_id`, `name`, `role`. Redirect by role to `/admin/dashboard`, `/faculty/dashboard`, or `/student/dashboard`.
2. **Passwords** — Stored hashed (bcrypt preferred; fallback salt + SHA-256). No plain text.
3. **Protected routes** — `@login_required`, `@role_required('admin'|'faculty'|'student')`, and optionally `@require_permission(Permission.XXX)`.
4. **Audit** — Security events (e.g. login, unauthorized access) logged via `log_audit_event` into `audit_log` and/or logging.

### 5.2 Enrollment Logic

1. **Enroll** — Student requests course; backend checks seat limit; if space available → status `enrolled`; else → `waitlisted`.
2. **Withdraw** — Student can withdraw; status updated (e.g. withdrawn/dropped).
3. **Override** — Admin can override enrollment status (e.g. force enroll) from enrollment management (override mode).
4. **Seat limits** — Set per course in Seat Allocation; enforced on enroll and in analytics (capacity/utilization).

### 5.3 Analytics Pipeline

1. **AnalyticsService** — Central place for:
   - Course-wise enrollment stats (with outer joins so courses with 0 enrollments appear).
   - Department-wise enrollment stats (same idea for departments).
   - Enrollment trends over time (by date).
   - Faculty-scoped: course stats for assigned courses, department stats for assigned department, utilization, high/low demand.
2. **Charts** — Data passed from route to template as JSON; Chart.js (bar, line, pie/donut) initialized in script blocks with error handling and responsive options.
3. **RBAC** — Admin sees institution-wide analytics; Faculty sees only assigned courses and department; Student sees only own data.

### 5.4 Sample Data & Refresh

1. **generate_sample_data.py** — Generates `students.csv` (e.g. 60 students) and `faculty.csv` (e.g. 10 faculty with departments).
2. **import_sample_data.py** — Creates/updates departments, courses, users (students/faculty), faculty–course assignments, and enrollments; includes a second pass to add **waitlisted** enrollments for demonstration.
3. **Refresh Sample Data** — Admin dashboard button calls `/admin/refresh-sample-data` (POST), runs the import script, then page reloads so all charts and tables show updated data.

### 5.5 UI/UX

- **Layout** — `base.html`: topbar (brand, user, logout), sidebar (role-based nav), main content.
- **Styling** — Single main stylesheet: stat cards, action buttons, charts container, alerts, badges (success, warning, danger, info), tables, responsive behavior.
- **Charts** — Chart.js 4.x; charts in dedicated containers with fallback text when no data; no duplicate chart blocks.

---

## 6. How to Run the Project (Step by Step)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Optional: generate and import sample data**
   ```bash
   cd data
   python generate_sample_data.py    # creates students.csv, faculty.csv
   python import_sample_data.py      # run from project root or data/
   ```
   Or from project root:
   ```bash
   python data/import_sample_data.py
   ```

3. **Start the application**
   ```bash
   python app.py
   ```
   Default: http://127.0.0.1:5000

4. **Login**
   - Admin: `admin@test.com` / `admin123`
   - Faculty: e.g. `faculty1@college.edu` / `faculty123` (if sample data imported)
   - Student: e.g. `student1@college.edu` / `student123` (if sample data imported)

5. **See analytics** — Use Admin dashboard “Refresh Sample Data” to repopulate waitlisted enrollments and refresh charts/tables.

---

## 7. Summary

| Aspect | Detail |
|--------|--------|
| **Name** | Course Enrollment Analytics Web Application |
| **Stack** | Python, Flask, SQLAlchemy, SQLite, Pandas, Jinja2, CSS, JavaScript, Chart.js |
| **Roles** | Admin (full access), Faculty (assigned courses/department), Student (own enrollments) |
| **Focus** | Enrollment management, seat limits, waitlisting, and analytics (course/department/trends) |
| **Security** | Session-based auth, hashed passwords, RBAC, audit logging |
| **Data** | Sample data scripts + refresh button for demos and chart visibility |

This document gives a full, step-by-step view of the project: technologies, structure, role-based behavior, main features, and how to run it.
