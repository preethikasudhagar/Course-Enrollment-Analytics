"""
Permission definitions and utilities for RBAC
"""
from enum import Enum
from functools import wraps
from datetime import datetime
from flask import session, jsonify, redirect, url_for, flash, request
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Permission(Enum):
    """System permissions"""
    # User Management
    CREATE_USER = "create_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    VIEW_ALL_USERS = "view_all_users"
    ASSIGN_ROLES = "assign_roles"
    
    # Course Management
    CREATE_COURSE = "create_course"
    UPDATE_COURSE = "update_course"
    DELETE_COURSE = "delete_course"
    VIEW_ALL_COURSES = "view_all_courses"
    MANAGE_SEAT_LIMITS = "manage_seat_limits"
    MANAGE_ENROLLMENT_RULES = "manage_enrollment_rules"
    
    # Department Management
    CREATE_DEPARTMENT = "create_department"
    UPDATE_DEPARTMENT = "update_department"
    DELETE_DEPARTMENT = "delete_department"
    VIEW_ALL_DEPARTMENTS = "view_all_departments"
    
    # Enrollment Management
    VIEW_ALL_ENROLLMENTS = "view_all_enrollments"
    CREATE_ENROLLMENT = "create_enrollment"
    UPDATE_ENROLLMENT = "update_enrollment"
    DELETE_ENROLLMENT = "delete_enrollment"
    OVERRIDE_ENROLLMENT = "override_enrollment"
    VIEW_OWN_ENROLLMENTS = "view_own_enrollments"
    ENROLL_IN_COURSE = "enroll_in_course"
    WITHDRAW_FROM_COURSE = "withdraw_from_course"
    
    # Analytics
    VIEW_SYSTEM_ANALYTICS = "view_system_analytics"
    VIEW_COURSE_ANALYTICS = "view_course_analytics"
    VIEW_DEPARTMENT_ANALYTICS = "view_department_analytics"
    VIEW_ENROLLMENT_TRENDS = "view_enrollment_trends"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    VIEW_SYSTEM_HEALTH = "view_system_health"
    
    # Academic Operations
    VIEW_STUDENT_ENROLLMENTS = "view_student_enrollments"
    UPDATE_ENROLLMENT_STATUS = "update_enrollment_status"
    ADD_ENROLLMENT_REMARKS = "add_enrollment_remarks"
    VIEW_COURSE_STATISTICS = "view_course_statistics"

# Role-Permission Mapping
ROLE_PERMISSIONS = {
    'admin': {
        # User Management
        Permission.CREATE_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.VIEW_ALL_USERS,
        Permission.ASSIGN_ROLES,
        
        # Course Management
        Permission.CREATE_COURSE,
        Permission.UPDATE_COURSE,
        Permission.DELETE_COURSE,
        Permission.VIEW_ALL_COURSES,
        Permission.MANAGE_SEAT_LIMITS,
        Permission.MANAGE_ENROLLMENT_RULES,
        
        # Department Management
        Permission.CREATE_DEPARTMENT,
        Permission.UPDATE_DEPARTMENT,
        Permission.DELETE_DEPARTMENT,
        Permission.VIEW_ALL_DEPARTMENTS,
        
        # Enrollment Management
        Permission.VIEW_ALL_ENROLLMENTS,
        Permission.CREATE_ENROLLMENT,
        Permission.UPDATE_ENROLLMENT,
        Permission.DELETE_ENROLLMENT,
        Permission.OVERRIDE_ENROLLMENT,
        
        # Analytics
        Permission.VIEW_SYSTEM_ANALYTICS,
        Permission.VIEW_COURSE_ANALYTICS,
        Permission.VIEW_DEPARTMENT_ANALYTICS,
        Permission.VIEW_ENROLLMENT_TRENDS,
        Permission.VIEW_AUDIT_LOGS,
        Permission.VIEW_SYSTEM_HEALTH,
    },
    'faculty': {
        # Limited Academic Operations
        Permission.VIEW_STUDENT_ENROLLMENTS,
        Permission.VIEW_COURSE_ANALYTICS,
        Permission.VIEW_DEPARTMENT_ANALYTICS,
        Permission.VIEW_COURSE_STATISTICS,
        Permission.UPDATE_ENROLLMENT_STATUS,
        Permission.ADD_ENROLLMENT_REMARKS,
        Permission.VIEW_ENROLLMENT_TRENDS,
    },
    'student': {
        # Personal Access Only
        Permission.VIEW_OWN_ENROLLMENTS,
        Permission.ENROLL_IN_COURSE,
        Permission.WITHDRAW_FROM_COURSE,
    }
}

def has_permission(permission: Permission, user_role: str = None) -> bool:
    """Check if user role has the specified permission"""
    if user_role is None:
        user_role = session.get('role')
    
    if not user_role:
        return False
    
    role_perms = ROLE_PERMISSIONS.get(user_role, set())
    return permission in role_perms

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check authentication
            if 'user_id' not in session:
                log_security_event('unauthorized_access', {
                    'route': request.path,
                    'method': request.method,
                    'reason': 'not_authenticated'
                })
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please login to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            # Check permission
            user_role = session.get('role')
            if not has_permission(permission, user_role):
                log_security_event('unauthorized_access', {
                    'user_id': session.get('user_id'),
                    'user_role': user_role,
                    'route': request.path,
                    'method': request.method,
                    'required_permission': permission.value,
                    'reason': 'insufficient_permissions'
                })
                if request.is_json:
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'required_permission': permission.value
                    }), 403
                flash(f'You do not have permission to access this feature. Required: {permission.value}', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_security_event(event_type: str, details: dict):
    """Log security events for audit trail"""
    user_id = session.get('user_id', 'anonymous')
    user_role = session.get('role', 'unknown')
    ip_address = request.remote_addr if request else 'unknown'
    
    log_entry = {
        'event_type': event_type,
        'user_id': user_id,
        'user_role': user_role,
        'ip_address': ip_address,
        'timestamp': str(datetime.now()),
        'details': details
    }
    
    logger.warning(f"SECURITY EVENT: {log_entry}")
    
    # In production, store in database audit log table
    # For now, log to file/system logs

def get_user_permissions(user_role: str = None) -> set:
    """Get all permissions for a user role"""
    if user_role is None:
        user_role = session.get('role')
    
    if not user_role:
        return set()
    
    return ROLE_PERMISSIONS.get(user_role, set())

def filter_data_by_role(query, model_class, user_role: str = None, user_id: int = None):
    """Filter database queries based on user role"""
    if user_role is None:
        user_role = session.get('role')
    
    if user_role == 'admin':
        # Admin can see all data
        return query
    
    elif user_role == 'faculty':
        # Faculty can see enrollments for courses they're assigned to
        # For now, faculty can see all enrollments (can be refined)
        return query
    
    elif user_role == 'student':
        # Students can only see their own data
        if user_id is None:
            user_id = session.get('user_id')
        
        if hasattr(model_class, 'user_id'):
            return query.filter(model_class.user_id == user_id)
        elif hasattr(model_class, 'student_id'):
            # For enrollment model
            from models.student import Student
            student = Student.query.filter_by(user_id=user_id).first()
            if student:
                return query.filter(model_class.student_id == student.id)
        
        return query.filter(False)  # Return empty query
    
    return query.filter(False)  # Default: no access
