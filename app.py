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
            session['userid'] = userid
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
        cursor = mysql.connection.cursor()

        # Fetch upcoming events
        cursor.execute("SELECT * FROM events WHERE event_date >= CURDATE()")
        events = cursor.fetchall()

        # Fetch student's complaints
        #cursor.execute("SELECT * FROM complaints WHERE student_id = %s", (current_user.id,))
        #complaints = cursor.fetchall()

        # Fetch attendance records
        cursor.execute("SELECT * FROM attendance WHERE student_id = %s", (current_user.id,))
        attendance = cursor.fetchall()

        cursor.close()

        return render_template(
            'student_dashboard.html',
            events=events,
            attendance=attendance
        )
    return redirect(url_for('login'))


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role == 'admin':
        cursor = mysql.connection.cursor()

        # Fetch all complaints
        cursor.execute("SELECT * FROM complaints")
        complaints = cursor.fetchall()

        # Fetch all events
        cursor.execute("SELECT * FROM events")
        events = cursor.fetchall()

        cursor.close()

        return render_template(
            'admin_dashboard.html',
            complaints=complaints,
            events=events
        )
    return redirect(url_for('login'))

@app.route('/past-events')
@login_required
def past_events():
    if current_user.role == 'student' or current_user.role == 'admin':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM events WHERE event_date < CURDATE()")  # Fetch past events
        past_events = cursor.fetchall()
        cursor.close()

        return render_template('past_events.html', events=past_events)
    return redirect(url_for('login'))

@app.route('/view-complaints')
@login_required
def view_complaints():
    if current_user.role == 'student':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM complaints WHERE student_id = %s", (current_user.id,))
        complaints = cursor.fetchall()
        cursor.close()
        return render_template('complaints.html', complaints=complaints)
    elif current_user.role == 'admin':
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM complaints")
        complaints = cursor.fetchall()
        cursor.close()
        return render_template('complaints.html', complaints=complaints)
    return redirect(url_for('login'))

@app.route('/profile')
@login_required
def profile():
    if current_user.role == 'student':
        # Fetch student details from the database
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT userid, name, email, branch, sem, sec 
            FROM student 
            WHERE userid = %s
        """, (current_user.id,))
        student_data = cursor.fetchone()
        cursor.close()

        # Ensure data exists for the current user
        if not student_data:
            return render_template("error.html", error="Profile not found")

        # Pass the data to the template
        return render_template('student_profile.html', student=student_data)
    elif current_user.role == 'admin':
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT userid, name, email,
            FROM admin 
            WHERE userid = %s
        """, (current_user.id,))
        admin_data = cursor.fetchone()
        cursor.close()

        # Ensure data exists for the current user
        if not admin_data:
            return render_template("error.html", error="Profile not found")

        # Pass the data to the template
        return render_template('admin_profile.html', admin=admin_data)

    return redirect(url_for('login'))

@app.route('/join_team', methods=['POST'])
def join_team():
    event_id = request.form.get('event_id')
    cursor = mysql.connection.cursor(dictionary=True) 
    query = """
    SELECT s.name, s.branch, s.sem, s.email 
    FROM team_search t
    JOIN students s ON t.userid = s.userid
    WHERE t.event_id = %s
    """
    cursor.execute(query, (event_id,))
    students = cursor.fetchall()
    cursor.close()
    return render_template('look_for_team.html', event_id=event_id, students=students)

@app.route('/add_to_team', methods=['POST'])
def add_to_team():
    event_id = request.form.get('event_id')
    userid = session.get('userid')  # Assuming the user ID is stored in the session

    if not userid:
        return redirect('/login')  # Redirect to login if the user is not logged in

    cursor = mysql.connection.cursor()
    query = "INSERT IGNORE INTO team_search (event_id, userid) VALUES (%s, %s)"
    cursor.execute(query, (event_id, userid))
    mysql.connection.commit()
    cursor.close()

    return redirect('/student_dashboard')


@app.route('/remove_from_team', methods=['POST'])
def remove_from_team():
    event_id = request.form.get('event_id')
    userid = session.get('userid')  # Assuming the user ID is stored in the session

    if not userid:
        return redirect('/login')  # Redirect to login if the user is not logged in

    cursor = mysql.connection.cursor()
    query = "DELETE FROM team_search WHERE event_id = %s AND userid = %s"
    cursor.execute(query, (event_id, userid))
    mysql.connection.commit()
    cursor.close()

    return redirect('/student_dashboard')

@app.route('/add-event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        event_id = request.form.get('event_id')
        event_name = request.form.get('event_name')
        event_date = request.form.get('event_date')
        participation_mode = request.form.get('participation_mode')
        coordinator = session.get('userid')  # Assuming the admin's user ID is stored in the session

        if not coordinator:
            return redirect('/login')  # Redirect to login if the user is not logged in

        cursor = mysql.connection.cursor()
        query = """
        INSERT INTO events (event_id, event_name, event_date, participation_mode, coordinator) 
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (event_id, event_name, event_date, participation_mode, coordinator))
        mysql.connection.commit()
        cursor.close()

        return redirect('/admin_dashboard')  # Redirect to dashboard after adding the event

    return render_template('add_event.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('mainpage'))

if __name__ == "__main__":
    app.run(debug=True)
