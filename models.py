import uuid
import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class TestType(db.Model):
    __tablename__ = 'test_types'
    
    id = db.Column(db.Integer, primary_key=True)
    test_type = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(50), nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total_attempts = db.Column(db.Integer, default=0)
    passed_attempts = db.Column(db.Integer, default=0)
    failed_attempts = db.Column(db.Integer, default=0)
    
    # Relationships
    test_masters = db.relationship('TestMaster', back_populates='test_type', cascade='all, delete-orphan')
    test_allocations = db.relationship('TestAllocation', back_populates='test_type', cascade='all, delete-orphan')
    test_sessions = db.relationship('TestSession', back_populates='test_type', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TestType {self.test_type}>'

class TestMaster(db.Model):
    __tablename__ = 'test_masters'
    
    id = db.Column(db.Integer, primary_key=True)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_types.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    question_image = db.Column(db.String(256), nullable=True)
    answer_a = db.Column(db.Text, nullable=False)
    answer_b = db.Column(db.Text, nullable=False)
    answer_c = db.Column(db.Text, nullable=False)
    answer_d = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(1), nullable=False)  # A, B, C, or D
    created_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Relationships
    test_type = db.relationship('TestType', back_populates='test_masters')
    creator = db.relationship('User', backref='created_tests')
    
    def __repr__(self):
        return f'<TestMaster {self.id}>'

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
    
    # Relationships
    verification_tokens = db.relationship('VerificationToken', back_populates='user', cascade='all, delete-orphan')
    test_allocations = db.relationship('TestAllocation', foreign_keys='TestAllocation.user_id', back_populates='user', cascade='all, delete-orphan')
    test_sessions = db.relationship('TestSession', back_populates='user', cascade='all, delete-orphan')

    def __init__(self, first_name, last_name, email, phone, password, profile_picture=None, is_verified=False):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.set_password(password)
        self.profile_picture = profile_picture
        self.is_verified = is_verified
    
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

class TestAllocation(db.Model):
    __tablename__ = 'test_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_types.id'), nullable=False)
    allocated_on = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    allocated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='allocated')  # allocated, completed, expired
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], back_populates='test_allocations')
    test_type = db.relationship('TestType', back_populates='test_allocations')
    allocator = db.relationship('User', foreign_keys=[allocated_by], backref='allocated_tests')
    
    def __repr__(self):
        return f'<TestAllocation {self.id}>'

class TestSession(db.Model):
    __tablename__ = 'test_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    test_type_id = db.Column(db.Integer, db.ForeignKey('test_types.id'), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    score = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, timed_out
    
    # Relationships
    user = db.relationship('User', back_populates='test_sessions')
    test_type = db.relationship('TestType', back_populates='test_sessions')
    answers = db.relationship('TestAnswer', back_populates='test_session', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<TestSession {self.id}>'

class TestAnswer(db.Model):
    __tablename__ = 'test_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    test_session_id = db.Column(db.Integer, db.ForeignKey('test_sessions.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('test_masters.id'), nullable=False)
    selected_answer = db.Column(db.String(1), nullable=True)  # A, B, C, or D
    is_correct = db.Column(db.Boolean, nullable=True)
    answered_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    test_session = db.relationship('TestSession', back_populates='answers')
    question = db.relationship('TestMaster')
    
    def __repr__(self):
        return f'<TestAnswer {self.id}>'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
