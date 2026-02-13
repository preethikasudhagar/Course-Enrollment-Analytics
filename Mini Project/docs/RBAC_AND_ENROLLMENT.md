# Role-Based Access Control (RBAC) and Enrollment Workflow

## Role-Based Access Control

### Admin Role
- **Purpose:** Full system administrator. Not a manageable user type (no "Manage Admin" page).
- **Access:** All dashboards, user management (students and faculty only), course management, seat allocation, department mapping, enrollment management (view all, approve/override), analytics and reports, system logs, profile.
- **Restrictions:** Cannot delete own account. Admin user is created at setup; role assignment page does not allow assigning Admin (only Student/Faculty).

### Faculty Role
- **Purpose:** Academic staff with assigned courses and department.
- **Access:** Dashboard (assigned courses and department stats only), My Courses, Enrolled Students (for assigned courses only), Course Analytics (read-only, filtered by assigned courses/department), Academic Monitoring, profile.
- **Restrictions:** Cannot access user management, system settings, or system-wide analytics. Cannot modify course structure or seat limits. Data is filtered by `FacultyCourseAssignment` and `department_id`.

### Student Role
- **Purpose:** Enrolled learners.
- **Access:** Dashboard (own enrollments), Available Courses, My Enrollments, Enrollment Actions (enroll/withdraw), profile.
- **Restrictions:** Cannot view analytics, other students, or any admin/faculty tools. All queries are scoped to the current user's student profile.

### Enforcement
- **Backend:** Every role-specific route uses `@login_required` and `@role_required('admin'|'faculty'|'student')`. Permission decorators used where applicable. Unauthorized access is logged to the audit log and returns 403.
- **Frontend:** Sidebar and menus are rendered by role in `base.html`; only links for the current role are shown. Buttons and links point to routes that enforce role on the server.

---

## User Management Structure

- **Manage Students:** Lists only users with role `student`. Add Student button creates a user with role student. Edit/Delete apply to students only.
- **Manage Faculty:** Lists only users with role `faculty`. Add Faculty creates a user with role faculty. No "Manage Admin" — admin is the system owner.
- **Role Assignment:** Lists users with role `student` or `faculty`. Allows changing a user's role between Student and Faculty only (dropdown has no Admin option). Purpose: convert a student to faculty or vice versa without creating a new account.

---

## Course Management

### Seat Allocation
- **Workflow:** Admin opens Seat Allocation page, sees each course with current enrolled count and seat limit. Can set or clear (empty = no limit) the seat limit per course. Saving calls `/admin/courses/<id>/seat-limit`.
- **Business logic:** When a student enrolls, the backend checks `course.seat_limit`; if set, enrollment is rejected when `current_enrollment_count >= seat_limit`. Prevents over-enrollment.

### Department Mapping
- **Workflow:** Admin opens Department Mapping page, sees each course with its current department. Dropdown to assign a different department and Update button. Calls `/admin/courses/<id>/update` with `department_id`.
- **Business logic:** Courses are grouped by department in the catalog and in analytics. Faculty can be assigned to a department; department-level analytics for faculty are scoped to that department.

---

## Enrollment Workflow

1. **Browse:** Student sees Available Courses (all courses with seat availability and current enrollment count). Courses with a seat limit show "seats available"; full courses can be indicated.
2. **Enroll:** From Enrollment Actions, student selects a course and clicks Enroll. Backend checks: (1) not already enrolled, (2) course exists, (3) if course has `seat_limit`, current enrolled count < limit. If any check fails, enrollment is rejected with a clear message. On success, an `Enrollment` record is created with `status='enrolled'`.
3. **Withdraw:** From Enrollment Actions or My Enrollments, student clicks Withdraw. Backend updates that enrollment to `status='withdrawn'`. Seat becomes available for others.
4. **Admin override:** Admin can view all enrollments and override status (e.g. set to enrolled/withdrawn) or add remarks. Used for manual corrections or policy exceptions.
5. **Conflicts:** One student can only have one active enrollment per course (unique constraint on `student_id`, `course_id`). Duplicate enrollments are rejected. Seat limits are enforced at enrollment time.

---

## Analytics and Reports

- **Admin:** Analytics Overview shows course-wise enrollment, department distribution, capacity utilization (enrolled vs seat limit %), enrollment trends over time, and high/low demand courses. All data is system-wide.
- **Faculty:** Course Analytics and Academic Monitoring show only data for assigned courses and the faculty's department. Read-only; no export or config.

All analytics routes and services return empty data on error (no 500) so the UI can render with "No data" placeholders.
