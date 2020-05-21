#!/usr/bin/env python3

import os
from json import dumps

from flask import Flask, redirect, render_template, request, url_for, flash, abort
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)
from flask_pymongo import PyMongo

from getplaced.models.Users import Student, Hirer

from getplaced.utils import get_current_id, is_safe_url

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

app.config["MONGO_URI"] = os.getenv('MONGO_URL')
mongo = PyMongo(app).db

db_fields = {
    'name': 'Name',
    'sex': 'Sex',
    'perOS': 'Percentage in Operating Systems',
    'perAL': 'Percentage in Algorithms',
    'perPC': 'Percentage in Programming Concepts',
    'perSE': 'Percentage in Software Engineering',
    'perCN': 'Percentage in Computer Networks',
    'perES': 'Percentage in Electronics Subjects',
    'perCA': 'Percentage in Computer Architecture',
    'perMA': 'Percentage in Mathematics',
    'perCO': 'Percentage in Communication skills',
    'hrs_per_day': 'Hours working per day',
    'logic_quo': 'Logical quotient rating',
    'hackathons': 'Hackathons',
    'code_skills': 'Coding skills rating',
    'public_speak': 'Public speaking points',
    'work_log': 'Can work long time before system',
    'selflearn_cap': 'Self-learning capability',
    'extra_courses': 'Extra-courses did',
    'certs': 'Certifications',
    'workshops': 'Workshops',
    'tal_tests': 'Talent tests taken',
    'olympiads': 'Olympiads',
    'rw_skills': 'Reading and writing skills',
    'mem_capacity': 'Memory capability score',
    'intst_subject': 'Interested subjects',
    'intst_career': 'Interested career area',
    'job_highstud': 'Job / Higher Studies',
    'settle_comp': 'Type of company want to settle in',
    'games_intst': 'Interested in games',
    'intst_books': 'Interested Type of Books',
    'rel_stat': 'In a Relationship',
    'behavior': 'Gentle or Stubborn behavior',
    'mgmt_tech': 'Management or Technical',
    'hard_smart': 'Hard/Smart worker',
    'work_teams': 'Ever worked in teams',
    'introvert': 'Introvert',
    'suggested_job': 'Suggested Job Role'
}


@login_manager.user_loader
def load_user(user_email):
    """Return `User` object for the corresponding `user_id`"""
    user = mongo.users.find_one({"email": user_email})
    if user is None:
        return None
    elif user['type'] == 'hirer':
        return Hirer(**user)
    else:
        return Student(**user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Displays a login page on a GET request
    For POST, it checks the `email` and `password` provided and accordingly redirects to the respective page
    """
    if request.method == 'POST':
        if 'email' not in request.form:
            return 'Email is required!'
        if 'password' not in request.form:
            return 'Password is required!'

        user = mongo.users.find_one({"email": request.form['email']})
        # Ensure user exists in the database
        if user is not None:
            user = Student(**user) if user.get('type') == 'student' else Hirer(**user)
            password = request.form['password']
            # Check the password against the hash stored in the database
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                next = request.args.get('next')
                if not is_safe_url(next):
                    return abort(400)
                return redirect(next or url_for('dashboard') if user.type == 'hirer' else url_for('d3'))
            return f'Wrong password for {user.email}!'
        return f"{request.form['email']} doesn't exist!"
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Displays a registration page on a GET request
    For POST, it checks `name`, `email`, 'company' and `password` provided for HIRER
    and accordingly registers account
    Password is hashed before being stored in the database

    Only a Hirer can signup, students already have their accounts
    """
    if request.method == 'POST':
        required_fields = ('name', 'email', 'password', 'company')
        for field in required_fields:
            if field not in request.form:
                return f'{field.capitalize()} is required!', 400

        if mongo.users.find_one({"email": request.form['email']}) is not None:
            return f"{request.form['email']} already exists! <a href='{url_for('login')}'>Sign in</a> instead.", 400

        data = dict()
        data['_id'] = get_current_id(mongo.users)
        data.update(request.form)
        data['password'] = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        data['type'] = 'hirer'

        # Add the user object to the database
        try:
            mongo.users.insert_one(data)
        except Exception as e:
            return f'Please enter valid data!', 400
        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/changepassword', methods=['GET', 'POST'])
@login_required
def change_password():
    """
       Displays a page to enter current and a new password on a GET request
       For POST, changes the password if current one matches and logs you out
    """
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']

        # If current password is correct, update and store the new hash
        if bcrypt.check_password_hash(current_user.password, current_password):
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            mongo.users.update_one({'email': current_user.email}, {'$set': {'password': current_user.password}})
        else:
            return 'Current password you entered is wrong! Please try again!'
        flash('Password updated successfully')

        # Log the user out, and redirect to login page
        logout_user()
        return redirect(url_for('login'))
    return render_template('d3trial.html')


@app.route('/logout')
@login_required
def logout():
    """Logs the current user out"""
    name = current_user.name
    email = current_user.email
    logout_user()
    flash(f"Logged out of {name} ({email})'s account!")
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    if current_user.type == 'hirer':
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('d3'))


@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """Shows the Dashboard to any Hirer"""
    if current_user.type == 'hirer':
        json_data = list(mongo.studentinfo.find())
        return render_template('dashboard.html', json_data=json_data)
    else:
        return 'This page is available only to Hirers', 401


@app.route('/d3', methods=['GET'])
@login_required
def d3():
    """Shows the student info  to the respective student meh"""
    if current_user.type == 'student':
        return render_template('d3trial.html')
    else:
        return '<marquee>Nothing here for you!</marquee><br><br>' \
               f'Head over to <a href="{url_for("dashboard")}">Dashboard.</a>'
