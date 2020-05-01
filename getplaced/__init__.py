#!/usr/bin/env python3

import os
from pymongo import MongoClient

from flask import Flask, redirect, render_template, request, url_for, jsonify, abort

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

db = MongoClient(os.getenv('MONGO_URL'))[os.getenv('DATABASE')]


@app.route('/')
def index():
    return render_template('d3trial.html')


@app.route('/dashboard', methods=['GET'])
def dashboard():
    return render_template('dashboard.html')