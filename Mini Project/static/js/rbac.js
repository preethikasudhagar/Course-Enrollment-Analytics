/**
 * Role-Based Access Control Frontend Utilities
 * Controls navigation and UI elements based on user role
 */

class RBACController {
    constructor() {
        this.userRole = this.getUserRole();
        this.userPermissions = this.getUserPermissions();
        this.init();
    }

    getUserRole() {
        // Get role from session (set by backend in template or via API)
        const roleElement = document.querySelector('[data-user-role]');
        return roleElement ? roleElement.getAttribute('data-user-role') : null;
    }

    getUserPermissions() {
        // Permissions are defined based on role
        const permissions = {
            'admin': [
                'manage_users', 'manage_courses', 'manage_departments',
                'view_analytics', 'view_audit_logs', 'override_enrollments'
            ],
            'faculty': [
                'view_students', 'view_course_analytics', 'update_enrollment_status',
                'add_remarks'
            ],
            'student': [
                'view_own_enrollments', 'enroll_courses', 'withdraw_courses'
            ]
        };
        return permissions[this.userRole] || [];
    }

    init() {
        this.hideUnauthorizedElements();
        this.showRoleBasedNavigation();
        this.attachPermissionChecks();
    }

    hideUnauthorizedElements() {
        // Hide elements that require specific permissions
        const elements = document.querySelectorAll('[data-requires-permission]');
        elements.forEach(element => {
            const requiredPermission = element.getAttribute('data-requires-permission');
            if (!this.hasPermission(requiredPermission)) {
                element.style.display = 'none';
            }
        });

        // Hide elements that require specific roles
        const roleElements = document.querySelectorAll('[data-requires-role]');
        roleElements.forEach(element => {
            const requiredRoles = element.getAttribute('data-requires-role').split(',');
            if (!requiredRoles.includes(this.userRole)) {
                element.style.display = 'none';
            }
        });
    }

    showRoleBasedNavigation() {
        // Show/hide navigation items based on role
        const navItems = {
            'admin': ['users', 'courses', 'departments', 'analytics', 'audit-logs'],
            'faculty': ['students', 'analytics'],
            'student': ['courses', 'enrollments']
        };

        const allowedItems = navItems[this.userRole] || [];
        
        document.querySelectorAll('[data-nav-item]').forEach(item => {
            const navItem = item.getAttribute('data-nav-item');
            if (!allowedItems.includes(navItem)) {
                item.style.display = 'none';
            }
        });
    }

    hasPermission(permission) {
        return this.userPermissions.includes(permission);
    }

    attachPermissionChecks() {
        // Add click handlers to check permissions before actions
        document.querySelectorAll('[data-action]').forEach(element => {
            element.addEventListener('click', (e) => {
                const requiredPermission = element.getAttribute('data-requires-permission');
                if (requiredPermission && !this.hasPermission(requiredPermission)) {
                    e.preventDefault();
                    alert('You do not have permission to perform this action.');
                    return false;
                }
            });
        });
    }

    checkPermissionBeforeAction(permission, callback) {
        if (this.hasPermission(permission)) {
            callback();
        } else {
            alert('You do not have permission to perform this action.');
        }
    }
}

// Initialize RBAC controller when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.rbac = new RBACController();
});

// Export for use in other scripts
window.RBACController = RBACController;
