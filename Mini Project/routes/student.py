"""
Student routes with enhanced RBAC and data filtering
"""
from flask import Blueprint, render_template, request, jsonify, session
from models.database import db
from models.student import Student
from models.enrollment import Enrollment
from models.course import Course
from models.department import Department
from models.user import User
from models.course_announcement import CourseAnnouncement
from utils.auth import login_required, role_required, log_audit_event
from utils.permissions import Permission, require_permission, filter_data_by_role
from services.analytics_service import AnalyticsService

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard')
@login_required
@role_required('student')
@require_permission(Permission.VIEW_OWN_ENROLLMENTS)
def dashboard():
    """Student dashboard - focused enrollment analytics for the current student"""
    user_id = session.get('user_id')
    student = Student.query.filter_by(user_id=user_id).first()
    
    if not student:
        return render_template('error.html', error_code=404, error_message='Student profile not found'), 404
    
    # Ensure student can only see their own data
    if student.user_id != user_id:
        log_audit_event('unauthorized_data_access', {
            'attempted_user_id': user_id,
            'target_student_id': student.id,
            'reason': 'user_id_mismatch'
        })
        return render_template('error.html', error_code=403, error_message='Unauthorized access'), 403
    
    analytics_service = AnalyticsService()
    enrollments_df = analytics_service.get_student_enrollments(student.id)
    enrollments = enrollments_df.to_dict('records') if not enrollments_df.empty else []

    # Build enrollment status counts for chart (enrolled vs waitlisted)
    status_counts = {'enrolled': 0, 'waitlisted': 0}
    try:
        rows = Enrollment.query.filter(Enrollment.student_id == student.id).all()
        for e in rows:
            if e.status in status_counts:
                status_counts[e.status] += 1
    except Exception:
        status_counts = {'enrolled': 0, 'waitlisted': 0}

    # Available courses with seat status
    courses = Course.query.all()
    available_courses = []
    try:
        enrolled_course_ids = {e.course_id for e in Enrollment.query.filter_by(student_id=student.id, status='enrolled').all()}
    except Exception:
        enrolled_course_ids = set()
    for c in courses:
        try:
            cnt = c.enrollments.filter_by(status='enrolled').count()
            seats_available = c.seats_available() if c.seat_limit is not None else None
        except Exception:
            cnt = 0
            seats_available = None
        available_courses.append({
            'id': c.id,
            'name': c.name,
            'code': c.code,
            'department': c.department.name if c.department else 'N/A',
            'seat_limit': c.seat_limit,
            'enrollment_count': cnt,
            'seats_available': seats_available,
            'already_enrolled': c.id in enrolled_course_ids
        })

    # Course announcements: from faculty for courses this student is enrolled in (enrolled or waitlisted)
    announcements = []
    try:
        my_enrollment_records = Enrollment.query.filter(Enrollment.student_id == student.id).all()
        my_course_ids = [e.course_id for e in my_enrollment_records]
        if my_course_ids:
            anns = CourseAnnouncement.query.filter(
                CourseAnnouncement.course_id.in_(my_course_ids)
            ).order_by(CourseAnnouncement.created_at.desc()).limit(30).all()
            for a in anns:
                course = Course.query.get(a.course_id)
                announcements.append({
                    'id': a.id,
                    'course_name': course.name if course else '—',
                    'course_code': course.code if course else '—',
                    'title': a.title,
                    'body': a.body or '',
                    'announcement_type': a.announcement_type or 'general',
                    'created_at': a.created_at
                })
    except Exception:
        announcements = []
    
    log_audit_event('student_dashboard_access', {
        'student_id': student.id
    })
    
    return render_template(
        'student/dashboard.html',
        enrollments=enrollments,
        status_counts=status_counts,
        available_courses=available_courses,
        announcements=announcements
    )

@student_bp.route('/available-courses')
@login_required
@role_required('student')
def available_courses():
    """List all courses with seat availability (for enrollment)"""
    courses = Course.query.all()
    student = Student.query.filter_by(user_id=session.get('user_id')).first()
    enrolled_course_ids = set()
    if student:
        enrolled_course_ids = {e.course_id for e in Enrollment.query.filter_by(student_id=student.id, status='enrolled').all()}
    course_list = []
    for c in courses:
        cnt = c.enrollments.filter_by(status='enrolled').count()
        available = c.seats_available() if c.seat_limit is not None else None
        course_list.append({
            'id': c.id, 'name': c.name, 'code': c.code,
            'department': c.department.name if c.department else 'N/A',
            'credits': c.credits, 'seat_limit': c.seat_limit,
            'enrollment_count': cnt,
            'seats_available': available,
            'already_enrolled': c.id in enrolled_course_ids
        })
    return render_template('student/available_courses.html', courses=course_list)

@student_bp.route('/courses')
@login_required
@role_required('student')
@require_permission(Permission.VIEW_OWN_ENROLLMENTS)
def courses():
    """View enrolled courses - student's own courses only (My Enrollments)"""
    user_id = session.get('user_id')
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        return render_template('error.html', error_code=404, error_message='Student profile not found'), 404
    if student.user_id != user_id:
        log_audit_event('unauthorized_data_access', {
            'attempted_user_id': user_id, 'target_student_id': student.id, 'reason': 'user_id_mismatch'
        })
        return render_template('error.html', error_code=403, error_message='Unauthorized access'), 403
    analytics_service = AnalyticsService()
    enrollments_df = analytics_service.get_student_enrollments(student.id)
    enrollments = enrollments_df.to_dict('records') if not enrollments_df.empty else []
    return render_template('student/courses.html', enrollments=enrollments)

@student_bp.route('/enrollment-actions')
@login_required
@role_required('student')
@require_permission(Permission.ENROLL_IN_COURSE)
def enrollment_actions():
    """Page to enroll or withdraw from courses"""
    student = Student.query.filter_by(user_id=session.get('user_id')).first()
    if not student:
        return render_template('error.html', error_code=404, error_message='Student profile not found'), 404
    enrolled = Enrollment.query.filter_by(student_id=student.id, status='enrolled').all()
    available = Course.query.all()
    enrolled_ids = {e.course_id for e in enrolled}
    enrollments_with_course = []
    for e in enrolled:
        co = Course.query.get(e.course_id)
        enrollments_with_course.append({
            'enrollment_id': e.id, 'course_id': co.id, 'course_name': co.name,
            'course_code': co.code, 'status': e.status
        })
    courses_available = [c for c in available if c.id not in enrolled_ids]
    course_options = [{'id': c.id, 'name': c.name, 'code': c.code, 'seats_available': c.seats_available(), 'seat_limit': c.seat_limit} for c in courses_available]
    return render_template('student/enrollment_actions.html', enrollments=enrollments_with_course, course_options=course_options)

@student_bp.route('/profile')
@login_required
@role_required('student')
def profile():
    user = User.query.get_or_404(session.get('user_id'))
    return render_template('student/profile.html', user=user)

@student_bp.route('/courses/enroll', methods=['POST'])
@login_required
@role_required('student')
@require_permission(Permission.ENROLL_IN_COURSE)
def enroll_in_course():
    """Enroll in a course.

    Business rules for waitlisting:
    - If seats are available (or no seat_limit is set), the student is enrolled immediately.
    - If the course is full (current enrolled >= seat_limit), the student is created with status='waitlisted'
      so that an admin/faculty can later approve using the override/approval flows.
    """
    try:
        user_id = session.get('user_id')
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({'success': False, 'message': 'Course ID is required'}), 400
        
        # Check if already enrolled
        existing = Enrollment.query.filter_by(student_id=student.id, course_id=course_id).first()
        if existing:
            return jsonify({'success': False, 'message': 'Already enrolled in this course'}), 400

        # Enforce seat limit at backend and decide between enrolled vs waitlisted
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'success': False, 'message': 'Course not found'}), 404
        if course.seat_limit is not None:
            current_count = course.enrollments.filter_by(status='enrolled').count()
            if current_count >= course.seat_limit:
                # Course is full → place the student on waitlist instead of hard failure
                enrollment_status = 'waitlisted'
            else:
                enrollment_status = 'enrolled'
        else:
            # No seat limit configured → always enroll directly
            enrollment_status = 'enrolled'

        # Create enrollment with computed status (enrolled or waitlisted)
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course_id,
            status=enrollment_status
        )
        db.session.add(enrollment)
        db.session.commit()
        
        log_audit_event(
            'course_enrollment_waitlisted' if enrollment_status == 'waitlisted' else 'course_enrollment',
            {
                'student_id': student.id,
                'course_id': course_id,
                'status': enrollment_status
            }
        )
        
        if enrollment_status == 'waitlisted':
            message = 'Course is currently full. You have been placed on the waitlist pending seat availability / faculty approval.'
        else:
            message = 'Successfully enrolled in course'
        return jsonify({'success': True, 'message': message}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@student_bp.route('/courses/withdraw', methods=['POST'])
@login_required
@role_required('student')
@require_permission(Permission.WITHDRAW_FROM_COURSE)
def withdraw_from_course():
    """Withdraw from a course"""
    try:
        user_id = session.get('user_id')
        student = Student.query.filter_by(user_id=user_id).first()
        
        if not student:
            return jsonify({'success': False, 'message': 'Student profile not found'}), 404
        
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({'success': False, 'message': 'Course ID is required'}), 400
        
        # Find enrollment
        enrollment = Enrollment.query.filter_by(student_id=student.id, course_id=course_id).first()
        if not enrollment:
            return jsonify({'success': False, 'message': 'Not enrolled in this course'}), 404
        
        # Update status
        enrollment.status = 'withdrawn'
        db.session.commit()
        
        log_audit_event('course_withdrawal', {
            'student_id': student.id,
            'course_id': course_id
        })
        
        return jsonify({'success': True, 'message': 'Successfully withdrawn from course'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
