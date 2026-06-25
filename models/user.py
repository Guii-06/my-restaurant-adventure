from flask_login import UserMixin


class User(UserMixin):
    # Represents the logged player used by Flask-Login
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email