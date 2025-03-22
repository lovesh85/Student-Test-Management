import os
from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime

from app import db
from models import User, VerificationToken
from forms import LoginForm, SignupForm
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
        # Placeholder for future dashboard
        flash('Welcome to your dashboard!', 'success')
        return render_template('dashboard.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out', 'info')
        return redirect(url_for('login'))
