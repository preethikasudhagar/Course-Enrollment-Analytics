"""
Authentication utilities with enhanced security and audit logging.
Uses bcrypt for password hashing; falls back to legacy salt:sha256 for existing records.
"""
import hashlib
import secrets
import json
import logging
from functools import wraps
from datetime import datetime
from flask import session, redirect, url_for, jsonify, request, flash, current_app
from models.database import db

try:
    import bcrypt
    _USE_BCRYPT = True
except ImportError:
    _USE_BCRYPT = False

logger = logging.getLogger(__name__)

def hash_password(password):
    """Hash password using bcrypt (or SHA-256 with salt if bcrypt unavailable)"""
    if _USE_BCRYPT:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"

def verify_password(password, password_hash):
    """Verify password against stored hash (bcrypt or legacy salt:sha256)"""
    if not password_hash:
        return False
    try:
        if password_hash.startswith('$2') and _USE_BCRYPT:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        salt, stored_hash = password_hash.split(':', 1)
        check = hashlib.sha256((password + salt).encode()).hexdigest()
        return check == stored_hash
    except Exception:
        return False

def log_audit_event(event_type: str, details: dict = None, user_id: int = None):
    """Log security events to audit log"""
    try:
        from models.audit_log import AuditLog
        
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id or session.get('user_id'),
            user_role=session.get('role'),
            ip_address=request.remote_addr if request else None,
            route=request.path if request else None,
            method=request.method if request else None,
            details=json.dumps(details) if details else None,
            timestamp=datetime.utcnow()
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Failed to log audit event: {e}")

def login_required(f):
    """Decorator to require login with audit logging"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            log_audit_event('unauthorized_access_attempt', {
                'route': request.path,
                'method': request.method,
                'reason': 'not_authenticated'
            })
            if request.is_json:
                return jsonify({'error': 'Authentication required'}), 401
            flash('Please login to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    """Decorator to require specific role(s) with audit logging"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                log_audit_event('unauthorized_access_attempt', {
                    'route': request.path,
                    'method': request.method,
                    'reason': 'not_authenticated'
                })
                if request.is_json:
                    return jsonify({'error': 'Authentication required'}), 401
                flash('Please login to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            user_role = session.get('role')
            if user_role not in roles:
                log_audit_event('unauthorized_access_attempt', {
                    'user_id': session.get('user_id'),
                    'user_role': user_role,
                    'route': request.path,
                    'method': request.method,
                    'required_roles': list(roles),
                    'reason': 'insufficient_permissions'
                }, user_id=session.get('user_id'))
                if request.is_json:
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'required_roles': list(roles)
                    }), 403
                flash(f'You do not have permission to access this page. Required roles: {", ".join(roles)}', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_role_redirect_url(role: str):
    """Get redirect URL based on user role"""
    role_routes = {
        'admin': 'admin.dashboard',
        'faculty': 'faculty.dashboard',
        'student': 'student.dashboard'
    }
    return url_for(role_routes.get(role, 'index'))
