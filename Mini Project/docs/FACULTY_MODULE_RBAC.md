# Faculty Role Module – RBAC and Boundaries

## Access Boundaries

- **Faculty can access ONLY their assigned courses.** Assignment is stored in `faculty_course_assignments` (faculty_id, course_id). Every faculty route that takes a `course_id` or `enrollment_id` validates ownership before returning data or performing actions.
- **Faculty cannot:** Add or delete courses, manage users (students/faculty), modify seat limits, access admin-level or institution-wide analytics, or view other departments’ confidential data.
- **Unauthorized access attempts** are logged via `log_audit_event` (e.g. `faculty_unauthorized_course_access`, `faculty_unauthorized_student_access`, `faculty_unauthorized_announcement`) and return **403 Forbidden**.

## Backend Enforcement

1. **Helpers (routes/faculty.py):**
   - `_assigned_course_ids(faculty_id)` – list of course IDs assigned to the faculty.
   - `_faculty_or_404()` – current faculty or 404.
   - `_ensure_course_assigned(faculty_id, course_id)` – returns True only if the course is assigned to the faculty.
   - `_ensure_enrollment_in_assigned_course(faculty_id, enrollment_id)` – returns (True, enrollment) only if the enrollment’s course is assigned to the faculty.

2. **Route-level checks:**
   - **Course detail:** `course_detail(course_id)` – 403 if not assigned.
   - **Student profile:** `student_profile(student_id)` – 403 unless the student is enrolled in at least one assigned course.
   - **Update enrollment status/remarks:** `update_enrollment_status(enrollment_id)` – 403 if enrollment not in an assigned course.
   - **Create announcement:** `communication_create()` – 403 if `course_id` is not assigned.

3. **Query filtering:**
   - All student/enrollment lists use `Course.id.in_(assigned_ids)`.
   - Analytics use `AnalyticsService.get_course_stats_for_faculty(faculty_id)` and `get_department_stats_for_faculty(department_id)` (department is the faculty’s own).
   - CSV export uses the same assigned-course filter.

## Frontend

- Admin menus are hidden for faculty (sidebar is role-based in `base.html`). Faculty see only: Dashboard, My Courses, Enrolled Students, Course Analytics, Academic Monitoring, Communication, Profile & Security.

## Data Privacy and Hierarchy

- Faculty see only:
  - Their assigned courses (name, code, department, seats, syllabus, schedule, semester).
  - Enrollments (and waitlisted) for those courses.
  - Department-level enrollment summary for **their** department only.
  - Course-wise utilization and trends for assigned courses only.
- No institution-wide user list, no other departments’ detailed data, no course create/delete or seat-limit changes.
