from models import db, User, Feedback, connect_db
from app import app

# This will create the database (based on your models)
# and connect to it
connect_db(app)
db.drop_all()
db.create_all()

# Create some sample users
user1 = User.register("user1", "1234",
                      "user1@example.com", "User", "One", False)
user2 = User.register("user2", "1234",
                      "user2@example.com", "User", "Two", False)
admin = User.register("admin", "1234",
                      "admin@example.com", "Admin", "User", True)

# Add users to the session
db.session.add(user1)
db.session.add(user2)
db.session.add(admin)

# Commit to save users
db.session.commit()

# Create some sample feedbacks
feedback1 = Feedback(title="Sample Feedback 1",
                     content="This is a sample feedback from user1.", username="user1")
feedback2 = Feedback(title="Sample Feedback 2",
                     content="This is a sample feedback from user1.", username="user1")
feedback3 = Feedback(title="Sample Feedback 3",
                     content="This is a sample feedback from user2.", username="user2")
feedback4 = Feedback(title="Sample Feedback 4",
                     content="This is a sample feedback from user2.", username="user2")

# Add feedbacks to the session
db.session.add_all([feedback1, feedback2, feedback3, feedback4])


# Commit to save feedbacks
db.session.commit()
