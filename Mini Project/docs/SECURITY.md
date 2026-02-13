# Security Documentation

## Authentication & Authorization

### Password Security
- Passwords are hashed using SHA-256 with a random salt
- Salt is stored alongside the hash: `salt:hash`
- Passwords are never stored in plain text
- Password verification compares hashed values

### Session Management
- Flask session-based authentication
- Session stores: user_id, name, email, role
- Sessions cleared on logout
- Session timeout handled by Flask

### Role-Based Access Control
- Three roles: Admin, Faculty, Student
- Route protection via decorators
- Feature-level access control
- Data filtering by role

## Security Best Practices

1. **Input Validation**
   - All user inputs validated
   - SQL injection prevention via SQLAlchemy ORM
   - XSS protection via Jinja2 auto-escaping

2. **Error Handling**
   - Generic error messages for security
   - Detailed errors logged server-side
   - User-friendly error pages

3. **Access Control**
   - Least privilege principle
   - Separation of duties
   - Defense in depth

4. **Data Privacy**
   - Students see only their data
   - Faculty see relevant academic data
   - Admin sees all data

## Security Checklist

- [x] Password hashing implemented
- [x] Session management secure
- [x] Role-based access control
- [x] Route protection decorators
- [x] SQL injection prevention
- [x] XSS protection
- [ ] CSRF protection (future enhancement)
- [ ] Rate limiting (future enhancement)
- [ ] Activity logging (future enhancement)
