import uuid
import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_picture = db.Column(db.String(256), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with verification tokens
    verification_tokens = db.relationship('VerificationToken', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, first_name, last_name, email, phone, password, profile_picture=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.set_password(password)
        self.profile_picture = profile_picture
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'

class VerificationToken(db.Model):
    __tablename__ = 'verification_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False, 
                          default=lambda: datetime.datetime.utcnow() + datetime.timedelta(hours=24))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with user
    user = db.relationship('User', back_populates='verification_tokens')
    
    def is_expired(self):
        return datetime.datetime.utcnow() > self.expires_at

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
