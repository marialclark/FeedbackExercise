from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Initiates User Model"""
    __tablename__ = 'users'

    username = db.Column(db.String(20), 
                         nullable=False,
                         primary_key=True, 
                         unique=True)

    password = db.Column(db.Text, 
                         nullable=False)
    
    email = db.Column(db.String(50),
                      nullable=False,
                      unique=True)
    
    first_name = db.Column(db.String(30), 
                           nullable=False)
    
    last_name = db.Column(db.String(30), 
                          nullable=False)
    
    feedback = db.relationship("Feedback", backref="user", cascade="all,delete")
    
    @property
    def full_name(self):
        """Return full name of user."""
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def register(cls, username, password, email, first_name, last_name):
        """Registers user, hashes password, and returns user"""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        new_user = cls(
            username=username,
            password=hashed_utf8,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        # db.session.add(new_user)
        return new_user
    

    @classmethod
    def authenticate(cls, username, password):
        """Authenticates User for Login"""
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, password):
            return u
        else:
            return False
        

class Feedback(db.Model):
    """Initializes Feedback Model"""
    __tablename__ = 'feedback'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    
    title = db.Column(db.String(100),
                      nullable=False)
    
    content = db.Column(db.Text,
                        nullable=False)
    
    username = db.Column(db.String(20),
                         db.ForeignKey('users.username'),
                         nullable=False)

