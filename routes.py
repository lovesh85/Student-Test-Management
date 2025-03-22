import os
from flask import render_template, redirect, url_for, flash, request, abort, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import random

from app import db
from models import User, VerificationToken
from forms import LoginForm, SignupForm, AddUserForm
from utils import save_profile_picture, send_verification_email

def register_routes(app):
    @app.route('/')
    def index():
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Redirect if user is already logged in
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            
            if user and user.check_password(form.password.data):
                if not user.is_verified:
                    flash('Please verify your email address first.', 'warning')
                    return redirect(url_for('login'))
                    
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid email or password', 'danger')
                
        return render_template('login.html', form=form)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        # Redirect if user is already logged in
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        form = SignupForm()
        if form.validate_on_submit():
            # Handle profile picture upload
            profile_picture = None
            if form.profile_picture.data:
                profile_picture = save_profile_picture(form.profile_picture.data)
                
            # Create user
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                password=form.password.data,
                profile_picture=profile_picture
            )
            
            db.session.add(user)
            db.session.commit()
            
            # Send verification email
            send_verification_email(user)
            
            flash('Account created successfully! Please check your email to verify your account.', 'success')
            return redirect(url_for('verification_sent'))
            
        return render_template('signup.html', form=form)

    @app.route('/verification-sent')
    def verification_sent():
        return render_template('verification_sent.html')

    @app.route('/verify-email/<token>')
    def verify_email(token):
        # Find the token
        verification = VerificationToken.query.filter_by(token=token).first_or_404()
        
        # Check if token is expired
        if verification.is_expired():
            # Delete expired token
            db.session.delete(verification)
            db.session.commit()
            flash('The verification link has expired. Please request a new one.', 'warning')
            return redirect(url_for('login'))
            
        # Verify the user
        user = verification.user
        user.is_verified = True
        
        # Delete the token once verified
        db.session.delete(verification)
        db.session.commit()
        
        flash('Your email has been verified! You can now login.', 'success')
        return redirect(url_for('verify_success'))

    @app.route('/verify-success')
    def verify_success():
        return render_template('verify_success.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Dashboard statistics 
        # In a real app, this would be actual data from the database
        total_students = User.query.count()
        new_students = User.query.filter(
            User.created_at >= datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ).count()
        
        # For demo purposes, we're using some sample values
        stats = {
            'total_students': total_students,
            'new_students': new_students,
            'test_types': 4,
            'total_attempts': 84,
            'passed_attempts': 47,
            'failed_attempts': 37
        }
        
        return render_template('dashboard.html', stats=stats)
    
    @app.route('/users')
    @login_required
    def users():
        users = User.query.all()
        return render_template('users.html', users=users)
    
    @app.route('/add-user', methods=['GET', 'POST'])
    @login_required
    def add_user():
        form = AddUserForm()
        if form.validate_on_submit():
            # Handle profile picture upload
            profile_picture = None
            if form.profile_picture.data:
                profile_picture = save_profile_picture(form.profile_picture.data)
                
            # Create user (no email verification needed for admin-added users)
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data,
                phone=form.phone.data,
                password=form.password.data,
                profile_picture=profile_picture,
                is_verified=True  # Auto-verify users added by admin
            )
            
            db.session.add(user)
            db.session.commit()
            
            flash('User added successfully!', 'success')
            return redirect(url_for('users'))
            
        return render_template('add_user.html', form=form)
    
    @app.route('/test-type')
    @login_required
    def test_type():
        return render_template('test_type.html')
    
    @app.route('/test-master')
    @login_required
    def test_master():
        return render_template('test_master.html')
    
    @app.route('/allocate-test')
    @login_required
    def allocate_test():
        return render_template('allocate_test.html')
    
    @app.route('/user-test')
    @login_required
    def user_test():
        return render_template('user_test.html')
    
    @app.route('/reports')
    @login_required
    def reports():
        return render_template('reports.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('login'))
    
    # API endpoint for chart data
    @app.route('/api/chart-data')
    @login_required
    def chart_data():
        # In a real app, this would be actual data from the database
        # For demo purposes, we're using sample data
        data = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'datasets': [{
                'label': 'Students Test',
                'data': [1, 0, 0, 0, 0, 0],
                'borderColor': '#6f42c1',
                'backgroundColor': 'transparent',
                'tension': 0.4
            }]
        }
        return jsonify(data)
