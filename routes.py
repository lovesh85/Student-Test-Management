import os
from flask import render_template, redirect, url_for, flash, request, abort, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import datetime
import random

from app import db
from models import User, VerificationToken, TestType, TestMaster, TestAllocation, TestSession, TestAnswer

# Create or update database tables
db.create_all()
from forms import LoginForm, SignupForm, AddUserForm, TestTypeForm, TestMasterForm
from utils import save_profile_picture, send_verification_email, save_question_image

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
        # Dashboard statistics from actual database
        total_students = User.query.count()
        new_students = User.query.filter(
            User.created_at >= datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ).count()
        test_types_count = TestType.query.count()

        # Get test attempt statistics
        test_sessions = TestSession.query.filter_by(status='completed').all()
        total_attempts = len(test_sessions)
        passed_attempts = sum(1 for session in test_sessions if session.score >= 70)
        failed_attempts = total_attempts - passed_attempts

        stats = {
            'total_students': total_students,
            'new_students': new_students,
            'test_types': test_types_count,
            'total_attempts': total_attempts,
            'passed_attempts': passed_attempts,
            'failed_attempts': failed_attempts
        }

        return render_template('dashboard.html', stats=stats)

    @app.route('/users')
    @login_required
    def users():
        search_query = request.args.get('search', '')

        if search_query:
            # Search in first name, last name, or email
            users = User.query.filter(
                (User.first_name.ilike(f'%{search_query}%')) |
                (User.last_name.ilike(f'%{search_query}%')) |
                (User.email.ilike(f'%{search_query}%')) |
                (User.phone.ilike(f'%{search_query}%'))
            ).all()
        else:
            users = User.query.all()

        return render_template('users.html', users=users, search_query=search_query)

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

    @app.route('/edit-user/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_user(id):
        user = User.query.get_or_404(id)
        form = AddUserForm(obj=user)

        # Don't validate the password field if it's empty
        if request.method == 'POST':
            if not form.password.data:
                form.password.validators = []

        if form.validate_on_submit():
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.phone = form.phone.data

            # Only update password if provided
            if form.password.data:
                user.set_password(form.password.data)

            # Handle profile picture upload
            if form.profile_picture.data:
                # Delete old profile picture if exists
                if user.profile_picture:
                    old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.profile_picture)
                    if os.path.exists(old_file_path):
                        os.remove(old_file_path)

                user.profile_picture = save_profile_picture(form.profile_picture.data)

            db.session.commit()
            flash('User updated successfully!', 'success')
            return redirect(url_for('users'))

        return render_template('edit_user.html', form=form, user=user)

    @app.route('/delete-user/<int:id>')
    @login_required
    def delete_user(id):
        user = User.query.get_or_404(id)

        # Don't allow deleting your own account
        if user.id == current_user.id:
            flash('You cannot delete your own account!', 'danger')
            return redirect(url_for('users'))

        # Delete profile picture if exists
        if user.profile_picture:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.profile_picture)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
        return redirect(url_for('users'))

    @app.route('/test-type')
    @login_required
    def test_type():
        search_query = request.args.get('search', '')
        if search_query:
            test_types = TestType.query.filter(
                (TestType.test_type.ilike(f'%{search_query}%')) |
                (TestType.language.ilike(f'%{search_query}%'))
            ).all()
        else:
            test_types = TestType.query.all()
        return render_template('test_type.html', test_types=test_types, search_query=search_query)

    @app.route('/add-test-type', methods=['GET', 'POST'])
    @login_required
    def add_test_type():
        form = TestTypeForm()
        if form.validate_on_submit():
            test_type = TestType(
                test_type=form.test_type.data,
                language=form.language.data
            )
            db.session.add(test_type)
            db.session.commit()
            flash('Test Type added successfully!', 'success')
            return redirect(url_for('test_type'))
        return render_template('add_test_type.html', form=form)

    @app.route('/delete-test-type/<int:id>', methods=['POST'])
    @login_required
    def delete_test_type(id):
        test_type = TestType.query.get_or_404(id)
        db.session.delete(test_type)
        db.session.commit()
        flash('Test Type deleted successfully!', 'success')
        return redirect(url_for('test_type'))

    @app.route('/test-master')
    @login_required
    def test_master():
        test_masters = TestMaster.query.all()
        return render_template('test_master.html', test_masters=test_masters)

    @app.route('/add-test-master', methods=['GET', 'POST'])
    @login_required
    def add_test_master():
        form = TestMasterForm()
        if form.validate_on_submit():
            # Handle question image upload
            question_image = None
            if form.question_image.data:
                question_image = save_question_image(form.question_image.data)

            test_master = TestMaster(
                test_type_id=form.test_type_id.data,
                question=form.question.data,
                question_image=question_image,
                answer_a=form.answer_a.data,
                answer_b=form.answer_b.data,
                answer_c=form.answer_c.data,
                answer_d=form.answer_d.data,
                correct_answer=form.correct_answer.data,
                created_by=current_user.id
            )
            db.session.add(test_master)
            db.session.commit()
            flash('Test Master added successfully!', 'success')
            return redirect(url_for('test_master'))
        return render_template('add_test_master.html', form=form)

    @app.route('/allocate-test', methods=['GET', 'POST'])
    @login_required
    def allocate_test():
        # Get test types
        test_types = TestType.query.all()
        
        # Get all users including current user
        users = User.query.all()

        if request.method == 'POST':
            user_id = request.form.get('user_id')
            test_type_id = request.form.get('test_type_id')

            if not user_id or not test_type_id:
                flash('Please select both a user and a test type.', 'danger')
                return redirect(url_for('allocate_test'))

            # Check if user and test type exist
            user = User.query.get_or_404(user_id)
            test_type = TestType.query.get_or_404(test_type_id)

            # Check if this test has already been allocated to this user
            existing_allocation = TestAllocation.query.filter_by(
                user_id=user_id, 
                test_type_id=test_type_id,
                status='allocated'
            ).first()

            if existing_allocation:
                flash(f'This test has already been allocated to {user.first_name} {user.last_name}.', 'warning')
                return redirect(url_for('allocate_test'))

            # Create new allocation
            allocation = TestAllocation(
                user_id=user_id,
                test_type_id=test_type_id,
                allocated_by=current_user.id
            )

            db.session.add(allocation)
            db.session.commit()

            flash(f'Test successfully allocated to {user.first_name} {user.last_name}.', 'success')
            return redirect(url_for('allocate_test'))

        return render_template('allocate_test.html', users=users, test_types=test_types)

    @app.route('/allocate-test-submit', methods=['POST'])
    @login_required
    def allocate_test_submit():
        user_id = request.form.get('user_id')
        test_type_id = request.form.get('test_type_id')

        if not user_id or not test_type_id:
            flash('Please select both a user and a test type.', 'danger')
            return redirect(url_for('allocate_test'))

        # Check if user and test type exist
        user = User.query.get_or_404(user_id)
        test_type = TestType.query.get_or_404(test_type_id)

        # Check if this test has already been allocated to this user
        existing_allocation = TestAllocation.query.filter_by(
            user_id=user_id, 
            test_type_id=test_type_id,
            status='allocated'
        ).first()

        if existing_allocation:
            flash(f'This test has already been allocated to {user.first_name} {user.last_name}.', 'warning')
            return redirect(url_for('allocate_test'))

        # Create new allocation
        allocation = TestAllocation(
            user_id=user_id,
            test_type_id=test_type_id,
            allocated_by=current_user.id
        )

        db.session.add(allocation)
        db.session.commit()

        flash(f'Test successfully allocated to {user.first_name} {user.last_name}.', 'success')
        return redirect(url_for('allocate_test'))

    @app.route('/user-test')
    @login_required
    def user_test():
        # Get test allocations for the current user
        allocations = TestAllocation.query.filter_by(
            user_id=current_user.id,
            status='allocated'
        ).all()

        test_types = [allocation.test_type for allocation in allocations]
        return render_template('user_test.html', test_types=test_types)

    @app.route('/start-test', methods=['POST'])
    @login_required
    def start_test():
        test_type_id = request.form.get('test_type_id')

        if not test_type_id:
            flash('Please select a test type.', 'danger')
            return redirect(url_for('user_test'))

        # Check if this test type exists and is allocated to the user
        allocation = TestAllocation.query.filter_by(
            user_id=current_user.id,
            test_type_id=test_type_id,
            status='allocated'
        ).first_or_404()

        # Get all questions for this test type
        questions = TestMaster.query.filter_by(test_type_id=test_type_id).all()

        if not questions:
            flash('No questions available for this test.', 'warning')
            return redirect(url_for('user_test'))

        # Create a new test session
        test_session = TestSession(
            user_id=current_user.id,
            test_type_id=test_type_id
        )

        db.session.add(test_session)
        db.session.commit()

        # Create test answers for each question (initially with no selected answer)
        for question in questions:
            test_answer = TestAnswer(
                test_session_id=test_session.id,
                question_id=question.id
            )
            db.session.add(test_answer)

        db.session.commit()

        # Redirect to the first question
        return redirect(url_for('test_question', test_session_id=test_session.id, question_index=0))

    @app.route('/test-question/<int:test_session_id>/<int:question_index>', methods=['GET', 'POST'])
    @login_required
    def test_question(test_session_id, question_index):
        # Verify that this test session belongs to the current user
        test_session = TestSession.query.filter_by(
            id=test_session_id,
            user_id=current_user.id
        ).first_or_404()

        # If test is completed, redirect to results
        if test_session.status != 'in_progress':
            flash('This test is already completed.', 'info')
            return redirect(url_for('test_results', test_session_id=test_session.id))

        # Get all questions for this test
        questions = TestMaster.query.filter_by(test_type_id=test_session.test_type_id).all()

        # Check if question index is valid
        if question_index < 0 or question_index >= len(questions):
            flash('Invalid question index.', 'danger')
            return redirect(url_for('user_test'))

        # Get current question
        question = questions[question_index]
        
        # Get or create answer record
        test_answer = TestAnswer.query.filter_by(
            test_session_id=test_session.id,
            question_id=question.id
        ).first()
        
        if not test_answer:
            test_answer = TestAnswer(
                test_session_id=test_session.id,
                question_id=question.id
            )
            db.session.add(test_answer)
            db.session.commit()

        # Handle form submission (answer)
        if request.method == 'POST':
            selected_answer = request.form.get('answer')
            test_answer = test_answer or TestAnswer(
                test_session_id=test_session.id,
                question_id=question.id
            )
            
            if selected_answer in ['A', 'B', 'C', 'D']:
                test_answer.selected_answer = selected_answer
                test_answer.is_correct = (selected_answer == question.correct_answer)
                if not test_answer in db.session:
                    db.session.add(test_answer)
                db.session.commit()

                # If this was the last question, calculate score and complete test
                if question_index + 1 >= len(questions):
                    # Calculate score
                    total_questions = len(questions)
                    correct_answers = TestAnswer.query.filter_by(
                        test_session_id=test_session.id,
                        is_correct=True
                    ).count()

                    score = int((correct_answers / total_questions) * 100)

                    # Update test session
                    test_session.score = score
                    test_session.status = 'completed'
                    test_session.completed_at = datetime.datetime.utcnow()

                    # Update test allocation status
                    allocation = TestAllocation.query.filter_by(
                        user_id=current_user.id,
                        test_type_id=test_session.test_type_id,
                        status='allocated'
                    ).first()

                    if allocation:
                        allocation.status = 'completed'

                    db.session.commit()

                    return redirect(url_for('test_results', test_session_id=test_session.id))
                else:
                    # Redirect to next question
                    return redirect(url_for('test_question', test_session_id=test_session.id, question_index=question_index+1))
            else:
                flash('Please select a valid answer.', 'warning')

        # Get the current answer (if any)
        current_answer = TestAnswer.query.filter_by(
            test_session_id=test_session.id,
            question_id=question.id
        ).first()

        # Calculate time remaining (30 minutes from start time)
        start_time = test_session.started_at
        end_time = start_time + datetime.timedelta(minutes=30)
        time_remaining = max(0, int((end_time - datetime.datetime.utcnow()).total_seconds()))

        # Check if time's up
        if time_remaining <= 0:
            test_session.status = 'timed_out'
            test_session.completed_at = datetime.datetime.utcnow()
            db.session.commit()
            flash('Time is up! Your test has been submitted.', 'warning')
            return redirect(url_for('test_results', test_session_id=test_session.id))

        return render_template(
            'test_questions.html',
            test_session_id=test_session.id,
            question=question,
            current_question_index=question_index,
            total_questions=len(questions),
            time_remaining=time_remaining,
            current_answer=current_answer
        )

    @app.route('/submit-test', methods=['POST'])
    @login_required
    def submit_test():
        test_session_id = request.form.get('test_session_id')

        if not test_session_id:
            flash('Invalid request.', 'danger')
            return redirect(url_for('user_test'))

        # Verify that this test session belongs to the current user
        test_session = TestSession.query.filter_by(
            id=test_session_id,
            user_id=current_user.id
        ).first_or_404()

        # If test is already completed, redirect to results
        if test_session.status != 'in_progress':
            flash('This test is already completed.', 'info')
            return redirect(url_for('test_results', test_session_id=test_session.id))

        # Get all answers for this test session
        answers = TestAnswer.query.filter_by(test_session_id=test_session_id).all()
        total_questions = len(answers)
        correct_answers = sum(1 for answer in answers if answer.selected_answer and answer.is_correct)

        # Calculate score based on answered questions
        answered_questions = sum(1 for answer in answers if answer.selected_answer is not None)
        if answered_questions > 0:
            score = int((correct_answers / total_questions) * 100)
        else:
            score = 0

        # Update test session
        test_session.completed_at = datetime.datetime.utcnow()
        test_session.score = score
        test_session.status = 'completed'

        # Update test type statistics
        test_type = TestType.query.get(test_session.test_type_id)
        test_type.total_attempts = (test_type.total_attempts or 0) + 1
        if score >= 70:
            test_type.passed_attempts = (test_type.passed_attempts or 0) + 1
        else:
            test_type.failed_attempts = (test_type.failed_attempts or 0) + 1

        # Update test allocation status
        allocation = TestAllocation.query.filter_by(
            user_id=current_user.id,
            test_type_id=test_session.test_type_id,
            status='allocated'
        ).first()

        if allocation:
            allocation.status = 'completed'

        db.session.commit()

        flash('Test completed successfully!', 'success')
        return redirect(url_for('test_results', test_session_id=test_session.id))

    @app.route('/test-results/<int:test_session_id>')
    @login_required
    def test_results(test_session_id):
        # Verify that this test session belongs to the current user
        test_session = TestSession.query.filter_by(
            id=test_session_id,
            user_id=current_user.id
        ).first_or_404()

        test_type = TestType.query.get(test_session.test_type_id)
        answers = TestAnswer.query.filter_by(test_session_id=test_session_id).all()

        return render_template(
            'test_results.html',
            test_session=test_session,
            test_type=test_type,
            answers=answers
        )

    @app.route('/reports')
    @login_required
    def reports():
        # Get statistics
        total_students = User.query.count()
        test_sessions = TestSession.query.filter_by(status='completed').all()
        total_attempts = len(test_sessions)
        passed_attempts = sum(1 for session in test_sessions if session.score >= 70)
        failed_attempts = total_attempts - passed_attempts

        stats = {
            'total_students': total_students,
            'total_attempts': total_attempts,
            'passed_attempts': passed_attempts,
            'failed_attempts': failed_attempts
        }

        # Get test results with related data
        results = TestSession.query.filter_by(status='completed')\
            .order_by(TestSession.completed_at.desc())\
            .all()

        return render_template('reports.html', stats=stats, results=results)

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
        # Get the current year
        current_year = datetime.datetime.utcnow().year

        # Get the counts of users registered by month for the current year
        month_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_data = [0] * 12  # Initialize with zeros

        # Get all users registered this year
        users_this_year = User.query.filter(
            db.extract('year', User.created_at) == current_year
        ).all()

        # Count users by month
        for user in users_this_year:
            month_index = user.created_at.month - 1  # Adjust for 0-indexed list
            month_data[month_index] += 1

        data = {
            'labels': month_labels,
            'datasets': [{
                'label': 'User Registrations',
                'data': month_data,
                'borderColor': '#6f42c1',
                'backgroundColor': 'transparent',
                'tension': 0.4
            }]
        }
        return jsonify(data)