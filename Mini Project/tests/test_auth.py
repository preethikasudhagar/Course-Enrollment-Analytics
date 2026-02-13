"""
Authentication tests
"""
import unittest
from app import app
from models.database import db, init_db
from utils.auth import hash_password, verify_password

class AuthTestCase(unittest.TestCase):
    """Test authentication functionality"""
    
    def setUp(self):
        """Set up test client"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            init_db()
    
    def tearDown(self):
        """Clean up after tests"""
        with app.app_context():
            db.drop_all()
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = 'testpassword123'
        hashed = hash_password(password)
        
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password('wrongpassword', hashed))
    
    def test_login_page_loads(self):
        """Test login page loads correctly"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        response = self.client.post('/login',
            json={'email': 'admin@test.com', 'password': 'admin123'},
            follow_redirects=False
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()
