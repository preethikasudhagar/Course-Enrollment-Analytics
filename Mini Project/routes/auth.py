"""
Authentication routes
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from models.database import db
from models.user import User
from utils.auth import hash_password, verify_password, log_audit_event, get_role_redirect_url

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication"""
    if request.method == 'GET':
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template('auth/login.html')
    
    # POST request
    try:
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Email and password are required'}), 400
            flash('Email and password are required', 'error')
            return render_template('auth/login.html')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not verify_password(password, user.password):
            # Log failed login attempt
            log_audit_event('login_failed', {
                'email': email,
                'reason': 'invalid_credentials',
                'ip_address': request.remote_addr
            })
            if request.is_json:
                return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
            flash('Invalid email or password', 'error')
            return render_template('auth/login.html')
        
        # Set session
        session['user_id'] = user.id
        session['name'] = user.name
        session['email'] = user.email
        session['role'] = user.role
        
        # Log successful login
        log_audit_event('login_success', {
            'user_id': user.id,
            'user_role': user.role,
            'email': email
        }, user_id=user.id)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'user': user.to_dict(),
                'redirect_url': get_role_redirect_url(user.role)
            }), 200
        
        # Redirect based on role using utility function
        return redirect(get_role_redirect_url(user.role))
        
    except Exception as e:
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(f'An error occurred: {str(e)}', 'error')
        return render_template('auth/login.html')

@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """Change password for current user (all roles)"""
    if 'user_id' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('auth.login'))
    if request.method == 'GET':
        return render_template('auth/change_password.html')
    try:
        data = request.get_json() if request.is_json else request.form
        current = data.get('current_password', '')
        new_pass = data.get('new_password', '')
        if not current or not new_pass:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Current and new password required'}), 400
            flash('Current and new password are required', 'error')
            return redirect(url_for('auth.change_password'))
        user = User.query.get(session['user_id'])
        if not user or not verify_password(current, user.password):
            if request.is_json:
                return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401
            flash('Current password is incorrect', 'error')
            return redirect(url_for('auth.change_password'))
        user.password = hash_password(new_pass)
        db.session.commit()
        log_audit_event('password_changed', {'user_id': user.id}, user_id=user.id)
        if request.is_json:
            return jsonify({'success': True, 'message': 'Password updated'}), 200
        flash('Password updated successfully.', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': str(e)}), 500
        flash(str(e), 'error')
        return redirect(url_for('auth.change_password'))

@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    """Logout user"""
    user_id = session.get('user_id')
    user_role = session.get('role')
    
    # Log logout event
    if user_id:
        log_audit_event('logout', {
            'user_id': user_id,
            'user_role': user_role
        }, user_id=user_id)
    
    session.clear()
    if request.is_json:
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    flash('You have been logged out', 'info')
    return redirect(url_for('auth.login'))
