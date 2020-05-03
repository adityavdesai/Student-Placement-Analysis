#!/usr/bin/env python3

import os

from flask import Flask, redirect, render_template, request, url_for, jsonify, abort
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

from getplaced.utils import users_to_json

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

app.config["MONGO_URI"] = os.getenv('MONGO_URL')
mongo = PyMongo(app)


@login_manager.user_loader
def load_user(user_id):
    """Return `User` object for the corresponding `user_id`"""
    return mongo.db.users.find_one({"_id": user_id})


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

        user = mongo.db.users.find_one({"email": request.form['email']})
        # Ensure user exists in the database
        if user is not None:
            user = Student(**user) if user.get('type') == 'student' else Hirer(**user)
            password = request.form['password']
            # Check the password against the hash stored in the database
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                print(user.type)
                if user.type == 'hirer':
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('d3'))
            return f'Wrong password for {user.email}!'
        return f"{request.form['email']} doesn't exist!"
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Displays a registration page on a GET request
    For POST, it checks:-
         i.) `name`, `email` and `password` provided for STUDENT and accordingly registers account
        ii.) IDR what all was asked for HIRER hehe
    Password is hashed before being stored in the database
    """
    if request.method == 'POST':
        required_fields = ('name', 'password', 'email')
        for field in required_fields:
            if field not in request.form:
                return jsonify({'response': f'{field} is required!'}), 400

        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Create user object
        u = Student(
            name=name,
            password=bcrypt.generate_password_hash(password).decode('utf-8'),
            email=email,
        )
        # Add the user object to the database and commit the transaction
        if mongo.db.users.find_one({"email": u.email}) is not None:
            return jsonify({'response': f'{u.email} already exists! Sign in instead.'}), 400

        try:
            mongo.db.users.insert_one(users_to_json(u))
        except Exception as e:
            return (
                jsonify(
                    {
                        'response': f'{e}<br><br>Please re-check your data!'
                    }
                ),
                400,
            )
        return f"Hello {email}, your account has been successfully created."
    return render_template('signup.html')


@app.route('/')
def index():
    return render_template('d3trial.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')


@app.route('/d3', methods=['GET'])
def d3():
    return render_template('d3trial.html')
