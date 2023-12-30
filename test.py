from unittest import TestCase

from app import app
from models import db, User, Feedback

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()


USER_DATA_1 = {
    "username": "user1",
    "password": "password1",
    "email": "user1@example.com",
    "first": "First1",
    "last": "Last1",
    "is_admin": False
}

USER_DATA_2 = {
    "username": "user2",
    "password": "password2",
    "email": "user2@example.com",
    "first": "First2",
    "last": "Last2",
    "is_admin": False
}

USER_DATA_3 = {
    "username": "admin",
    "password": "adminpassword",
    "email": "admin@example.com",
    "first": "Admin",
    "last": "User",
    "is_admin": True
}

FEEDBACK_DATA_1 = {
    "title": "Great Service",
    "content": "The service provided was exceptional, very happy with the experience.",
    "username": "user1"  # Assuming 'user1' is a valid username in your User model
}

FEEDBACK_DATA_2 = {
    "title": "Excellent Product",
    "content": "The product quality is top-notch. Highly recommend!",
    "username": "user2"  # Assuming 'user2' is a valid username in your User model
}

FEEDBACK_DATA_3 = {
    "title": "Quick Support",
    "content": "Had an issue, and it was resolved quickly by the support team. Impressed!",
    "username": "admin"  # Assuming 'admin' is a valid username in your User model
}


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        user = User.register(**USER_DATA_1)
        db.session.add(user)
        db.session.commit()

        self.user = user

    def tearDown(self):
        Feedback.query.filter_by(username=self.user.username).delete()
        User.query.filter_by(username=self.user.username).delete()
        db.session.commit()
        db.session.rollback()

    def test_user_register(self):
        user = User.query.get("user1")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'user1')
        self.assertNotEqual(user.password, 'password1')

    def test_user_authenticate(self):
        """Test user authentication."""
        user = User.authenticate("user1", "password1")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "user1")

        invalid_user = User.authenticate("user1", "wrongpassword")
        self.assertFalse(invalid_user)


class FeedbackModelTestCase(TestCase):
    """Tests for Feedback model."""

    def setUp(self):
        """Create test client and add sample data."""
        User.query.delete()
        Feedback.query.delete()
        user = User.register(**USER_DATA_1)
        db.session.add(user)
        feedback = Feedback(**FEEDBACK_DATA_1)
        db.session.add(feedback)
        db.session.commit()
        self.user = user
        self.feedback = feedback

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_feedback_creation(self):
        """Test feedback creation."""
        feedback = Feedback.query.filter_by(username="user1").first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.title, "Great Service")
        self.assertEqual(
            feedback.content, "The service provided was exceptional, very happy with the experience.")
