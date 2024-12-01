import re

from flask import Flask, Blueprint, render_template, redirect, request, abort, flash
import flask_login
from flask_login import login_required

import app.db as db
from app.db_connection import get_db_connection
import app.fidosession as fidosession

import mysql.connector
from mysql.connector import Error


bp = Blueprint('frontend', __name__)

@bp.route('/')
def index():
    #if flask_login.current_user.is_authenticated:
        #return render_template('dashboard.html', is_logged_in=True)
    #else: return render_template('login.html', is_logged_in=False)
    return render_template('login.html')

@bp.route('/register', methods=['POST', 'GET'])
def register():
    #if flask_login.current_user.is_authenticated:
        #return redirect('/')

    if request.method == 'POST':
        return post_register()
    else:
        return render_template('register.html')
    
def post_register():
    firstname = request.form['firstname']
    middlename = request.form['middlename']
    lastname = request.form['lastname']
    username = request.form['username']
    print(f"fname: {firstname}, mname: {middlename}, lname: {lastname}, username: {username}")

    # Validate input
    input_lengths = [len(firstname), len(middlename), len(lastname), len(username)]
    if max(input_lengths) > 100 or min(input_lengths) == 0 or re.match(r'^[a-z0-9]+$', username) is None:
        print('WARNING: Got a request with invalid input which should have been validated by the client.')
        return abort(400)

    # Connect to the database using the connection function
    connection = get_db_connection()
    if connection is None:
        flash("Database connection failed.")
        return redirect('/register')

    try:
        cursor = connection.cursor()

        new_user = db.create_user(firstname, middlename, lastname, username)
    except db.UsernameAlreadyExistsException:
        error_msg = f'The chosen username "{username}" is already taken. Please choose another username.'
        flash(error_msg)
        return redirect('/register')

    finally:
        # Ensure the connection is closed
        if connection.is_connected():
            cursor.close()
            connection.close()

    # create a new session for the user
    flask_login.login_user(new_user)

    # ask the user weather he wants to set up fido or not
    return redirect('/register-fido')

@bp.route('/register-fido', methods=['POST', 'GET'])
@login_required
def register_fido():
    return render_template('register_fido.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """This route is used to log in with username and password."""

    # logged-in users don't have to log in
    if flask_login.current_user.is_authenticated:
        return redirect("/")

    if request.method == 'POST':
        return post_login()
    else:
        return render_template('login.html')


def post_login():
    # extract form fields
    user_name = request.form['username']
    password = request.form['password']

    # validate input
    if user_name == "" or password == "":
        print("WARNING: Got a request with invalid input which should have been validated by the client. This "
              'might indicate that an attacker is sending manipulated requests.')
        return render_template('login.html', error="Invalid input")

    # load user and check credentials
    user = db.authenticate_user(user_name, password)
    if user is None:
        error_msg = "Ungültige Zugangsdaten."
        flash(error_msg)
        return redirect('/login')

    # is fido enabled?
    if user.fido_info == "":
        # fido is not enabled. Create a new session and ask the user if he wants to enable fido
        flask_login.login_user(user)
        return redirect('/register-fido')
    else:
        # fido is enabled. Start a temporary fido-session and redirect the user to the fido-login page.
        # (The fidosession module describes why the fido-session is necessary)
        fidosession.start_fido_session(user.user_id)
        return redirect('/login-fido')

