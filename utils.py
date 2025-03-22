import os
import uuid
from flask import current_app, url_for, render_template
from flask_mail import Message
from werkzeug.utils import secure_filename
from app import mail
from models import VerificationToken, db

def save_profile_picture(file):
    """
    Save a profile picture to the upload folder
    
    Args:
        file: The file from the form
    
    Returns:
        str: The filename of the saved file
    """
    if not file:
        return None
        
    # Create a unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4().hex}_{filename}"
    
    # Save the file
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(os.path.join(current_app.root_path, file_path))
    
    return file_path

def send_verification_email(user):
    """
    Generate a verification token and send a verification email to the user
    
    Args:
        user: The user to send the verification email to
    """
    # Create a verification token
    token = VerificationToken(user_id=user.id)
    db.session.add(token)
    db.session.commit()
    
    # Create the verification URL
    verify_url = url_for('verify_email', token=token.token, _external=True)
    
    # Create the email message
    subject = "Verify Your Email Address"
    html_body = render_template('email/verification.html', 
                               user=user, 
                               verify_url=verify_url)
    
    # Send the email
    msg = Message(subject=subject,
                 recipients=[user.email],
                 html=html_body)
    mail.send(msg)
    
    return token
