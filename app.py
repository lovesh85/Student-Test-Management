import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
mail = Mail()

def create_app():
    # Create Flask application
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('config.Config')
    
    # Ensure upload directory exists
    os.makedirs(os.path.join(app.root_path, app.config['UPLOAD_FOLDER']), exist_ok=True)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'login'
    login_manager.login_message_category = 'info'
    
    with app.app_context():
        # Import routes and models here to avoid circular imports
        from routes import register_routes
        
        # Register blueprints/routes
        register_routes(app)
        
        # Create database tables
        db.create_all()
    
    return app

# Create the app instance
app = create_app()
