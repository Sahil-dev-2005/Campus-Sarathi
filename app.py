from flask import Flask,render_template,request, redirect, url_for, flash

app = Flask(__name__)

@app.route('/')
def mainpage():
    return render_template("index.html")

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        # Add your login validation logic here (e.g., check the database)
        if userid == "admin" and password == "password":  # Example validation
            return "welcome to the future"  # Redirect to home page or dashboard
        else:
            return render_template("error.html",error="INVALID CREDENTIALS")
    return render_template('login.html')