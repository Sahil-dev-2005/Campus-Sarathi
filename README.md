# Campus-Sarathi

Campus Sarathi is a web application designed to manage campus activities efficiently. 
It includes features for student and admin authentication, dashboards, and role-based access.

## Features
- **Role-based Authentication**: Separate login for students and admins.
- **Dashboards**: Dedicated dashboards for students and admins.
- **Secure Authentication**: Password hashing using Flask-Bcrypt.
- **User Management**: Stores user data in MySQL, including roles, emails, and personal details.

## Tech Stack
- **Backend**: Flask
- **Frontend**: HTML, CSS
- **Database**: MySQL
- **Libraries**: Flask-Bcrypt, Flask-Login, Flask-MySQLdb

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/campus-sarathi.git
   cd campus-sarathi
2. install
pip install -r requirements.txt
3. setup mysql
   mysql -u root -p campus_sarathi < schema.sql
4. python app.py


---

### **6. Usage**
```markdown
## Usage
1. Open the application in a browser.
2. Select a role (Student/Admin) on the homepage.
3. Log in with your credentials.
4. Access the respective dashboard based on your role.

## Folder Structure
campus-sarathi/
│
├── static/
│   ├── css/
│   ├── images/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── error.html
│   ├── student_dashboard.html
│   ├── admin_dashboard.html
│
├── app.py
├── requirements.txt
└── README.md



