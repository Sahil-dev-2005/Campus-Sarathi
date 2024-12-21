from flask import Flask, render_template, request, redirect, url_for, session
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'Ilove2005'
bcrypt = Bcrypt(app)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'sql@2023sahil'
app.config['MYSQL_DB'] = 'campus_sarathi'

mysql = MySQL(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, userid, role):
        self.id = userid
        self.role = role  # To distinguish between student and admin

@login_manager.user_loader
def load_user(userid):
    role = session.get('role')
    if role == 'student':
        return User(userid, 'student')
    elif role == 'admin':
        return User(userid, 'admin')
    return None

@app.route('/')
def mainpage():
    return render_template("index.html")  # Renders the role selection page

@app.route('/select_role', methods=['POST'])
def select_role():
    role = request.form.get('role')  # Get role from form submission
    if role not in ['student', 'admin']:
        return render_template("error.html", error="INVALID ROLE")
    session['role'] = role  # Save role in session
    return redirect(url_for('login', role=role))  # Redirect to the login page with role

@app.route('/login', methods=['GET', 'POST'])
def login():
    role = session.get('role')  # Retrieve role from session
    if not role:
        return redirect(url_for('mainpage'))  # Redirect to main page if role is missing

    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']

        # Determine table based on role
        table = 'student' if role == 'student' else 'admin'

        # Query database for user
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT password FROM {table} WHERE userid = %s", (userid,))
        result = cursor.fetchone()
        cursor.close()

        if result and bcrypt.check_password_hash(result[0], password):
            user = User(userid, role)
            login_user(user)
            return redirect(url_for(f"{role}_dashboard"))  # Redirect to the dashboard based on role
        else:
            return render_template("error.html", error="INVALID CREDENTIALS")
    return render_template("login.html", role=role)

@app.route('/student-register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        # Get data from form
        userid = request.form['userid']
        name = request.form['name']
        email = request.form['email']
        branch = request.form['branch']
        semester = request.form['semester']
        section = request.form['section']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        # Insert data into student table (existing table)
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO student (userid, name, email, branch, sem, sec, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (userid, name, email, branch, semester, section, password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))  # Redirect to login page after successful registration

    return render_template('student_register.html')


@app.route('/admin-register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        # Get data from form
        userid = request.form['userid']
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        # Insert data into admin table (existing table)
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO admin (userid, name, email, password)
            VALUES (%s, %s, %s, %s)
        """, (userid, name, email, password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))  # Redirect to login page after successful registration

    return render_template('admin_register.html')


@app.route('/student_dashboard')
@login_required
def student_dashboard():
    if current_user.role == 'student':
        return "Welcome to the Student Dashboard!"
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role == 'admin':
        return "Welcome to the Admin Dashboard!"
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('mainpage'))

if __name__ == "__main__":
    app.run(debug=True)
