from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Regexp
from models import User, TestType

class LoginForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired(), Length(min=2, max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long"),
        Regexp(r'.*[!@#$%^&*(),.?":{}|<>].*', message="Password must contain at least one special character")
    ])
    confirm_password = PasswordField('Retype Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Sign Up')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email or login.')

class AddUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=10, max=15)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters long"),
        Regexp(r'.*[!@#$%^&*(),.?":{}|<>].*', message="Password must contain at least one special character")
    ])
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Add User')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class TestTypeForm(FlaskForm):
    test_type = StringField('Test type', validators=[DataRequired(), Length(min=2, max=100)])
    language = StringField('Language', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Add Test Type')

class TestMasterForm(FlaskForm):
    test_type_id = SelectField('Test Type', coerce=int, validators=[DataRequired()])
    question = TextAreaField('Question', validators=[DataRequired()])
    question_image = FileField('Question Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    answer_a = TextAreaField('Answer (A)', validators=[DataRequired()])
    answer_b = TextAreaField('Answer (B)', validators=[DataRequired()])
    answer_c = TextAreaField('Answer (C)', validators=[DataRequired()])
    answer_d = TextAreaField('Answer (D)', validators=[DataRequired()])
    correct_answer = SelectField('Correct Answer', choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ], validators=[DataRequired()])
    submit = SubmitField('Submit')
    
    def __init__(self, *args, **kwargs):
        super(TestMasterForm, self).__init__(*args, **kwargs)
        self.test_type_id.choices = [(t.id, f"{t.test_type} - {t.language}") 
                                   for t in TestType.query.order_by(TestType.test_type).all()]
