Since you implemented **email verification using Google's App Password method**, you should document this in your `README.md`. Here’s how you can update the **"Installation & Setup"** section to include email verification.

---

### **Updated `README.md` for Email Verification**
```md
# Student Test App

## 📌 Overview
Student Test App is a web-based application built using **Flask** for the backend, **HTML & CSS** for the frontend, and **PostgreSQL** as the database. The application allows students to take tests and view their results.

## 🚀 Features
- User authentication (Login & Signup)
- Email verification using Google App Password
- Create and manage tests
- Submit answers and get instant results
- Admin panel for managing tests and students

## 🛠️ Tech Stack
- **Frontend:** HTML, CSS
- **Backend:** Flask
- **Database:** PostgreSQL
- **Authication** Google
- **Hosting:** Replit

## 🔧 Installation & Setup

### Clone the Repository
```sh
git clone https://github.com/lovesh85/Student-App.git
cd Student-App
```

### Install Dependencies
Create a virtual environment (optional but recommended) and install dependencies:
```sh
pip install -r requirements.txt
```

### Configure Environment Variables
Create a `.env` file in the project root and add the following:

```ini
DATABASE_URL=your_postgresql_connection_string
SECRET_KEY=your_secret_key

# Email Configuration (For Google App Password)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_google_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com
```

### **How to Get a Google App Password**
Since Google no longer allows less secure apps, you need to generate an **App Password**:
1. Go to **[Google Account Security](https://myaccount.google.com/security)**.
2. Scroll down to **"Signing in to Google"** and enable **2-Step Verification**.
3. After enabling, go to **"App Passwords"** and generate a new one.
4. Use the generated password in the `MAIL_PASSWORD` variable above.

### Run the Application
```sh
flask run
```
The app will be available at **`http://127.0.0.1:5000/`**.

## 📧 Email Verification Process
1. After signing up, the user receives a **verification email** with a unique activation link.
2. The user must click the **activation link** to verify their account.
3. If the user doesn’t verify within a certain period, they must request a **new verification email**.
4. Only verified users can log in.

## 📸 Screenshots
*(Add screenshots of your email verification page and the app here if possible)*

## 🤝 Contributing
If you want to contribute, feel free to fork the repository and submit a pull request.

## 📜 License
This project is licensed under the MIT License.

---

### **Next Steps**
✅ **Manually update the `README.md` file**  
✅ **Copy & paste the updated content**  
✅ **Save the file and commit it**  
✅ **Push it to GitHub using `git push origin main`**  

Let me know if you need any refinements! 🚀
