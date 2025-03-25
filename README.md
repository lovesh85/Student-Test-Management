# Student Test App

## Project Overview
The **Student Test App** is a web-based platform for conducting online examinations, built using **Flask** and **PostgreSQL**. It enables students to register, take tests, and track their performance, while administrators can manage users, test types, and monitor analytics through an interactive dashboard.

## Features
### User Registration & Authentication
- Email verification to prevent spam accounts
- Secure password hashing
- User session management with Flask-Login

### Test Management
- Create and manage different test types
- Add and edit questions
- Auto-scoring system for quick results

### Examination Process
- Select and attempt tests
- Submit answers and receive instant results
- Time tracking for tests

### Dashboard & Analytics
- Students: View past test scores and progress trends
- Admins: Monitor test performance, user activity, and statistics
- Interactive charts using **Chart.js**

### Reports & Insights
- Track test attempts and student performance
- Generate pass/fail summaries
- Identify trends in test performance

## Technologies Used
- **Backend:** Flask (Python), Flask-Mail, Flask-Login, SQLAlchemy
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** PostgreSQL
- **Security:** Password Hashing, Secure Sessions

## Installation Guide

### Prerequisites
- Python (>=3.8)
- PostgreSQL
- Virtual Environment (recommended)

### Setup Instructions
1. Download the project files and extract them into a folder.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   ```
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up the database:
   - Create a PostgreSQL database.
   - Update `config.py` with your database and email credentials.
   - Run database migrations:
     ```bash
     flask db init
     flask db migrate -m "Initial migration"
     flask db upgrade
     ```
5. Run the application:
   ```bash
   flask run
   ```
   The app will be accessible at `http://127.0.0.1:5000/`.

## Configuration
Update the `config.py` file with your PostgreSQL and email SMTP settings:
```python
class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost/student_test_db'
    MAIL_SERVER = 'smtp.yourmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your-email@example.com'
    MAIL_PASSWORD = 'your-email-password'
```

## Folder Structure
```
/student-test-app
│── /static          # Static assets (CSS, JS, images)
│── /templates       # HTML templates
│── config.py        # Application configuration
│── extensions.py    # Flask extensions setup
│── models.py        # Database models
│── app.py           # Main application file
│── requirements.txt # Dependencies list
│── README.md        # Documentation
```

## Future Enhancements
- Role-based access control (Admin, Student, Teacher)
- Timer-based test attempts
- Advanced analytics with AI-driven insights
- Multi-language support
- Export test results as PDFs

---
### Author: [LOVESH SHARMA]  
### GitHub: [Student-Test-Management](https://github.com/lovesh85/Student-Test-Management)
