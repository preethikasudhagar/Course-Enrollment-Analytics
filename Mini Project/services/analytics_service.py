"""
Analytics service for data processing and analysis
"""
import pandas as pd
from models.database import db
from models.enrollment import Enrollment
from models.course import Course
from models.department import Department
from models.student import Student

class AnalyticsService:
    """Service for enrollment analytics"""
    
    @staticmethod
    def get_course_enrollment_stats():
        """Get enrollment statistics by course. Returns empty DataFrame on error."""
        try:
            # OUTER JOIN so courses with 0 enrollments still appear
            query = db.session.query(
                Course.name,
                Course.code,
                Department.name.label('department'),
                db.func.count(Enrollment.id).label('enrollment_count')
            ).join(
                Department, Course.department_id == Department.id
            ).outerjoin(
                Enrollment,
                db.and_(Course.id == Enrollment.course_id, Enrollment.status == 'enrolled')
            ).group_by(
                Course.id, Course.name, Course.code, Department.name
            ).all()
            data = [{
                'course_name': row.name,
                'course_code': row.code,
                'department': row.department,
                'enrollment_count': row.enrollment_count
            } for row in query]
            return pd.DataFrame(data)
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_department_enrollment_stats():
        """Get enrollment statistics by department. Returns empty DataFrame on error."""
        try:
            # OUTER JOIN so departments with 0 enrollments still appear
            query = db.session.query(
                Department.name,
                Department.code,
                db.func.count(Enrollment.id).label('enrollment_count')
            ).outerjoin(
                Course, Department.id == Course.department_id
            ).outerjoin(
                Enrollment,
                db.and_(Course.id == Enrollment.course_id, Enrollment.status == 'enrolled')
            ).group_by(
                Department.id, Department.name, Department.code
            ).all()
            data = [{
                'department_name': row.name,
                'department_code': row.code,
                'enrollment_count': row.enrollment_count
            } for row in query]
            return pd.DataFrame(data)
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_enrollment_trends():
        """Get enrollment trends over time. Returns empty DataFrame on error."""
        try:
            query = db.session.query(
                db.func.date(Enrollment.enrollment_date).label('date'),
                db.func.count(Enrollment.id).label('count')
            ).filter(
                Enrollment.status == 'enrolled'
            ).group_by(
                db.func.date(Enrollment.enrollment_date)
            ).order_by(
                db.func.date(Enrollment.enrollment_date)
            ).all()
            data = [{
                'date': row.date.isoformat() if row.date else None,
                'count': row.count
            } for row in query]
            return pd.DataFrame(data)
        except Exception:
            return pd.DataFrame()
    
    @staticmethod
    def get_student_enrollments(student_id):
        """Get enrollments for a specific student. Returns empty DataFrame on error."""
        try:
            enrollments = Enrollment.query.filter_by(student_id=student_id, status='enrolled').all()
            data = []
            for enrollment in enrollments:
                course = Course.query.get(enrollment.course_id)
                department = Department.query.get(course.department_id) if course else None
                data.append({
                    'course_name': course.name if course else 'N/A',
                    'course_code': course.code if course else 'N/A',
                    'course_id': course.id if course else None,
                    'department': department.name if department else 'N/A',
                    'credits': course.credits if course else 0,
                    'status': enrollment.status,
                    'grade': enrollment.grade
                })
            return pd.DataFrame(data)
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_high_low_demand_courses(threshold_high=None, threshold_low=None):
        """Identify high-demand and low-demand courses. Returns empty lists on error."""
        try:
            df = AnalyticsService.get_course_enrollment_stats()
            if df.empty:
                return {'high_demand': [], 'low_demand': []}
            df = df.sort_values('enrollment_count', ascending=False).reset_index(drop=True)
            n = len(df)
            if threshold_high is not None and threshold_low is not None:
                high = df[df['enrollment_count'] >= threshold_high].to_dict('records')
                low = df[df['enrollment_count'] <= threshold_low].to_dict('records')
            else:
                high_idx = max(1, n // 2)
                high = df.head(high_idx).to_dict('records')
                low = df.tail(high_idx).to_dict('records')
            return {'high_demand': high, 'low_demand': low}
        except Exception:
            return {'high_demand': [], 'low_demand': []}

    @staticmethod
    def get_course_stats_for_faculty(faculty_id):
        """Course-wise enrollment stats only for courses assigned to this faculty."""
        try:
            from models.faculty_course import FacultyCourseAssignment
            assigned_course_ids = db.session.query(FacultyCourseAssignment.course_id).filter(
                FacultyCourseAssignment.faculty_id == faculty_id
            ).all()
            assigned_course_ids = [r[0] for r in assigned_course_ids]
            if not assigned_course_ids:
                return pd.DataFrame()
            query = db.session.query(
                Course.name,
                Course.code,
                Department.name.label('department'),
                db.func.count(Enrollment.id).label('enrollment_count')
            ).join(Enrollment, Course.id == Enrollment.course_id
            ).join(Department, Course.department_id == Department.id
            ).filter(Enrollment.status == 'enrolled', Course.id.in_(assigned_course_ids)
            ).group_by(Course.id, Course.name, Course.code, Department.name).all()
            data = [{'course_name': r.name, 'course_code': r.code, 'department': r.department, 'enrollment_count': r.enrollment_count} for r in query]
            return pd.DataFrame(data)
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_department_stats_for_faculty(department_id):
        """Department-level enrollment summary for a single department."""
        if not department_id:
            return pd.DataFrame()
        try:
            query = db.session.query(
                Department.name,
                Department.code,
                db.func.count(Enrollment.id).label('enrollment_count')
            ).join(Course, Department.id == Course.department_id
            ).join(Enrollment, Course.id == Enrollment.course_id
            ).filter(Enrollment.status == 'enrolled', Department.id == department_id
            ).group_by(Department.id, Department.name, Department.code).all()
            data = [{'department_name': r.name, 'department_code': r.code, 'enrollment_count': r.enrollment_count} for r in query]
            return pd.DataFrame(data)
        except Exception:
            return pd.DataFrame()

    @staticmethod
    def get_course_utilization_for_faculty(faculty_id):
        """Course-wise seat utilization % for assigned courses only."""
        try:
            from models.faculty_course import FacultyCourseAssignment
            assigned = db.session.query(FacultyCourseAssignment.course_id).filter(
                FacultyCourseAssignment.faculty_id == faculty_id
            ).all()
            assigned_ids = [r[0] for r in assigned]
            if not assigned_ids:
                return []
            out = []
            for c in Course.query.filter(Course.id.in_(assigned_ids)).all():
                cnt = c.enrollments.filter_by(status='enrolled').count()
                limit = c.seat_limit
                pct = round(100 * cnt / limit, 1) if limit else 0
                out.append({
                    'course_id': c.id, 'course_name': c.name, 'course_code': c.code,
                    'enrolled': cnt, 'seat_limit': limit, 'utilization_pct': pct
                })
            return out
        except Exception:
            return []

    @staticmethod
    def get_high_low_demand_for_faculty(faculty_id, department_id):
        """High/low demand courses within faculty's assigned courses (or department)."""
        try:
            from models.faculty_course import FacultyCourseAssignment
            assigned = db.session.query(FacultyCourseAssignment.course_id).filter(
                FacultyCourseAssignment.faculty_id == faculty_id
            ).all()
            assigned_ids = [r[0] for r in assigned]
            if not assigned_ids:
                return {'high_demand': [], 'low_demand': []}
            q = db.session.query(
                Course.id, Course.name, Course.code,
                db.func.count(Enrollment.id).label('cnt')
            ).outerjoin(Enrollment, db.and_(Course.id == Enrollment.course_id, Enrollment.status == 'enrolled')
            ).filter(Course.id.in_(assigned_ids)).group_by(Course.id, Course.name, Course.code).all()
            rows = [{'course_name': r.name, 'course_code': r.code, 'enrollment_count': r.cnt} for r in q]
            if not rows:
                return {'high_demand': [], 'low_demand': []}
            rows.sort(key=lambda x: x['enrollment_count'], reverse=True)
            n = len(rows)
            mid = max(1, n // 2)
            return {'high_demand': rows[:mid], 'low_demand': rows[-mid:]}
        except Exception:
            return {'high_demand': [], 'low_demand': []}
