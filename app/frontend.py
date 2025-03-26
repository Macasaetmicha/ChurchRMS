import re

from flask import Flask, Blueprint, render_template, redirect, request, abort, flash, jsonify, url_for
import flask_login
from flask_login import login_required, current_user

import app.db as db
from app.db_connection import get_db_connection
import app.fidosession as fidosession

import mysql.connector
from mysql.connector import Error

bp = Blueprint('frontend', __name__)

@bp.route('/')
def index():
    if flask_login.current_user.is_authenticated:
        return redirect(url_for('frontend.dashboard'))
        
    else: 
        return render_template('out/login.html', is_logged_in=False)
    
@bp.route('/register', methods=['POST', 'GET'])
def register():
    #if flask_login.current_user.is_authenticated:
        #return redirect('/')

    if request.method == 'POST':
        return post_register()
    else:
        return render_template('out/register.html')
    
def post_register():
    firstname = request.form['firstname']
    middlename = request.form['middlename']
    lastname = request.form['lastname']
    username = request.form['username']
    contact_number = request.form['contact_number']
    print(f"fname: {firstname}, mname: {middlename}, lname: {lastname}, username: {username}, contact number: {contact_number}")

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

        new_user = db.create_user(firstname, middlename, lastname, username, contact_number)
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
    return render_template('out/register_fido.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """This route is used to log in with username and password."""

    if request.method == 'POST':
        return post_login()
    else:
        return render_template('out/login.html')


def post_login():
    # extract form fields
    user_name = request.form['username']

    # validate input
    if user_name == "":
        print("WARNING: Got a request with invalid input which should have been validated by the client. This "
              'might indicate that an attacker is sending manipulated requests.')
        return render_template('out/login.html', error="Invalid input")
    print(user_name)
    # load user and check credentials
    user = db.authenticate_user(user_name)
    if user is None:
        error_msg = "Invalid Credentials 1."
        flash(error_msg)
        return redirect('/login')
    print(user)
    # is fido enabled?
    if user.fido_info == "":
        # fido is not enabled. Create a new session and ask the user if he wants to enable fido
        flask_login.login_user(user)
        return redirect('/register-fido')
        
    else:
        # fido is enabled. Start a temporary fido-session and redirect the user to the fido-login page.
        # (The fidosession module describes why the fido-session is necessary)
        fidosession.start_fido_session(user.user_id)
        print('FIDO LOGIN INITATE')
        return redirect('/login-fido')

@bp.route('/login-fido')
def login_fido():
    """This route returns the HTML for the fido-login page. This page can only be accessed if the user has a valid
    fido-session."""

    # logged-in users don't have to log in
    if flask_login.current_user.is_authenticated:
        return redirect("/")

    # check if there is a fido-session
    user_id = fidosession.get_user_id()
    print('USER ID CHECK2')
    print(user_id)
    if user_id is None:
        return redirect('/login')

    return render_template('out/login_fido.html')

@bp.route('/logout', methods=["POST"])
def logout():
    # we don't have to check weather the user is logged in or not
    # if the user thinks he is logged in but he is no longer logged in (e.g. because his session expired) this route
    # will be called. We want to redirect all users to the landing page
    flask_login.logout_user()
    return redirect("/")

@bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if flask_login.current_user.is_authenticated:
        ceremony_count = db.get_ceremony_count()
        print('\n\nThis is the retrieved Ceremony Count', ceremony_count)
        return render_template('in/dashboard.html', is_logged_in=True)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if flask_login.current_user.is_authenticated:
        return render_template('in/settings.html', is_logged_in=True)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/settings/user', methods=['GET'])
def get_accnt_record():
    if flask_login.current_user.is_authenticated:
        user_id = current_user.user_id 
        accnt_record = db.view_accnt(user_id)  
        print('\n\nThis is the retrieved User Records')
        print(accnt_record)

        print('\n\nThis is the retrieved User ID')
        print(user_id)
        if accnt_record:
            return jsonify(accnt_record) 
        else:
            return jsonify({'error': 'Record not found'}), 404
    else:
        return jsonify({'error': 'Unauthorized access'}), 401

@bp.route('/settings/update/recoveryNumber', methods=['PUT'])
def updateRecovNumber():
    print('Update Recovery Data')
    if request.method == "PUT":
        print('Found Data')
        user_id = current_user.user_id 
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request (update): {data}')
        
        # Extract values from data
        recovery_number = data.get('new-recov-num')

        try:
            print('Data:', {recovery_number})
            db.update_recovery_number(user_id, recovery_number)
            print("Priest data updated successfully.")

            return jsonify({'message': 'Data Updated Successfully'})
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'message': f"Error: {str(e)}"}), 500

@bp.route('/settings/update/authentication', methods=['PUT'])
def updateAuthentication():
    print('Update Authentication Data')
    if request.method == "PUT":
        print('Found Data')
        user_id = current_user.user_id 
        
        try:
            db.deleteFidoInfo(user_id)
            print("FIDO data deleted successfully.")

            return jsonify({'message': 'Data Deleted Successfully'})
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'message': f"Error: {str(e)}"}), 500


@bp.route('/records', methods=['GET', 'POST'])
def records():
    if flask_login.current_user.is_authenticated:
        existing_clients = db.get_records()
        print('\nFrom /records in frontend.py')
        print(f"EXISTING Clients: {existing_clients}")

        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON data for AJAX requests
            print('Got JSON Request Records\n\n')
            return jsonify(existing_clients)
        else:
            # Render HTML template for regular requests
            return render_template('in/records.html', is_logged_in=True, existing_clients=existing_clients)
    else:
        return render_template('out/login.html', is_logged_in=False)



@bp.route('/baptism', methods=['GET', 'POST'])
def baptism():
    if flask_login.current_user.is_authenticated:
        exisitng_baptism = db.get_baptism()
        print('\nFrom /baptism in frontend.py')
        print(f"EXISTING BAPTISM: {exisitng_baptism}")
       
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON data for AJAX requests
            print('Got JSON Request\n\n')
            return jsonify(exisitng_baptism)
        else:
            # Render HTML template for regular requests
            return render_template('in/baptism.html', is_logged_in=True, exisitng_baptism=exisitng_baptism)
    else:
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/baptism/<int:baptism_id>', methods=['GET'])
def get_baptism_record(baptism_id):
    if flask_login.current_user.is_authenticated:
        baptism_record = db.view_baptism(baptism_id)  
        if baptism_record:
            return jsonify(baptism_record) 
        else:
            return jsonify({'error': 'Record not found'}), 404
    else:
        return jsonify({'error': 'Unauthorized access'}), 401

@bp.route('/baptism/add', methods=['GET'])
def new_bapt():
    if flask_login.current_user.is_authenticated:
        priests = db.get_priests()
        return render_template('in/bapt_add.html', is_logged_in=True, priests=priests,)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/baptism/insert', methods=['POST'])
def insert_bapt():
    print('Insert Data')
    if request.method == "POST":
        print('Found Data')
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request: {data}')

        # Extract values from data
        first_name = data.get('fname')
        middle_name = data.get('mname')
        last_name = data.get('lname')
        birthday = data.get('birthday')
        birthplace = data.get('birthplace')
        ligitivity = data.get('ligitivity')
        address = data.get('address')
        status = data.get('status')

        mother_fname = data.get('mother-fname')
        mother_mname = data.get('mother-mname')
        mother_lname = data.get('mother-lname')
        mother_birthday = data.get('mother-birthday')
        mother_birthplace = data.get('mother-bplace')
        mother_address = data.get('mother-address')
        father_fname = data.get('father-fname')
        father_mname = data.get('father-mname')
        father_lname = data.get('father-lname')
        father_birthday = data.get('father-birthday')
        father_birthplace = data.get('father-bplace')
        father_address = data.get('father-address')

        baptism_date = data.get('baptism-date')
        priest = data.get('priest')
        sponsor1 = data.get('sponsor1')
        sponsor1_residence = data.get('sponsor1-residence')
        sponsor2 = data.get('sponsor2')
        sponsor2_residence = data.get('sponsor2-residence')

        bapt_index = data.get('baptism-index')
        bapt_book = data.get('baptism-book')
        bapt_page = data.get('baptism-page')
        bapt_line = data.get('baptism-line')

        print(bapt_index, bapt_book, bapt_page, bapt_line)
    
        # Call the function to insert the data into the database
        try:
            # Check if client already exists
            existing_user = db.check_existing_client(first_name, last_name, birthday)
            if existing_user:
                client_id = existing_user['id']
                print(f"Client already exists with ID: {client_id}")
            else:
                # Check if parents already exist
                existing_parents = db.check_existing_parents(mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace, father_fname, father_mname, father_lname, father_birthday, father_birthplace)

                mother_id = existing_parents['mother']['parent_id'] if existing_parents['mother'] else None
                father_id = existing_parents['father']['parent_id'] if existing_parents['father'] else None

                # Insert mother if not exists
                if mother_id is None:
                    mother_id = db.insert_parent(mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace, mother_address, 'mother')

                # Insert father if not exists
                if father_id is None:
                    father_id = db.insert_parent(father_fname, father_mname, father_lname, father_birthday, father_birthplace, father_address, 'father')

                # Insert client data
                client_id = db.insert_client(first_name, middle_name, last_name, birthday, ligitivity, birthplace, address, status, mother_id, father_id)
                print("Data inserted successfully, here is the client ID: ", client_id)
           
            # Insert baptism data
            db.insert_baptism(client_id, baptism_date, sponsor1, sponsor1_residence, sponsor2, sponsor2_residence, priest, bapt_index, bapt_book, bapt_page, bapt_line)

            return jsonify({'message': 'Data Inserted Successfully'})
        
        except Exception as e:
            return jsonify({'message': f"Error: {str(e)}"}), 500

@bp.route('/baptism/edit/<int:id>', methods=['GET', 'POST'])
def edit_bapt(id):
    if flask_login.current_user.is_authenticated:
        priests = db.get_priests()
        return render_template('in/bapt_edit.html', is_logged_in=True, id=id, priests=priests,)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/baptism/update', methods=['PUT'])
def update_bapt():
    print('Update Baptism Data')
    if request.method == "PUT":
        print('Found Data')
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request (update): {data}')
        
        # Extract values from data
        baptism_id = data.get('id')
        client_id = data.get('client_id')
        first_name = data.get('fname')
        middle_name = data.get('mname')
        last_name = data.get('lname')
        birthday = data.get('birthday')
        birthplace = data.get('birthplace')
        ligitivity = data.get('ligitivity')
        address = data.get('address')
        status = data.get('status')
        mother_fname = data.get('mother-fname')
        mother_mname = data.get('mother-mname')
        mother_lname = data.get('mother-lname')
        mother_birthday = data.get('mother-birthday')
        mother_birthplace = data.get('mother-bplace')
        mother_address = data.get('mother-address')
        father_fname = data.get('father-fname')
        father_mname = data.get('father-mname')
        father_lname = data.get('father-lname')
        father_birthday = data.get('father-birthday')
        father_birthplace = data.get('father-bplace')
        father_address = data.get('father-address')
        date = data.get('baptism-date')
        priest = data.get('priest')
        sponsor1 = data.get('sponsor1')
        sponsor1_residence = data.get('sponsor1-residence')
        sponsor2 = data.get('sponsor2')
        sponsor2_residence = data.get('sponsor2-residence')

        try:
            # Get parent IDs
            mother_id = db.get_parent_id(client_id, 'mother')
            father_id = db.get_parent_id(client_id, 'father')

            # Update parents data
            if mother_id:
                db.update_parent(mother_id, mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace, mother_address)
                print("Mother data updated successfully.")
            if father_id:
                db.update_parent(father_id, father_fname, father_mname, father_lname, father_birthday, father_birthplace, father_address)
                print("Father data updated successfully.")

            # Update client data
            db.update_client(client_id, first_name, middle_name, last_name, birthday, ligitivity, birthplace, address, status)
            print("Client data updated successfully.")

            # Update baptism data
            print('Data for the baptism:', {baptism_id, date, sponsor1, sponsor1_residence, sponsor2, sponsor2_residence, priest})
            db.update_baptism_record(baptism_id, date, sponsor1, sponsor1_residence, sponsor2, sponsor2_residence, priest)
            print("Baptism data updated successfully.")

            return jsonify({'message': 'Data Updated Successfully'})
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'message': f"Error: {str(e)}"}), 500
        
@bp.route('/baptism/delete/<int:id>', methods=['DELETE'])
def delete_bapt(id):
    print('Delete Data')
    try:
        # Call the function to delete the baptism data from the database
        db.delete_baptism(id)
        return jsonify({'message': 'Data Deleted Successfully'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f"Error: {str(e)}"}), 500




@bp.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    if flask_login.current_user.is_authenticated:
        exisitng_confirmation = db.get_confirmation()
        print('\nFrom \n confirmation.py')
        print(f"EXISTING CONFIRMATION: {exisitng_confirmation}")

        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON data for AJAX requests
            print('Got JSON Request\n\n')
            return jsonify(exisitng_confirmation)
        else:
            # Render HTML template for regular requests
            return render_template('in/confirmation.html', is_logged_in=True, exisitng_confirmation=exisitng_confirmation)
    else:
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/confirmation/<int:confirmation_id>', methods=['GET'])
def get_confirmation_record(confirmation_id):
    if flask_login.current_user.is_authenticated:
        confirmation_record = db.view_confirmation(confirmation_id)  
        if confirmation_record:
            return jsonify(confirmation_record) 
        else:
            return jsonify({'error': 'Record not found'}), 404
    else:
        return jsonify({'error': 'Unauthorized access'}), 401

@bp.route('/confirmation/add', methods=['GET'])
def new_conf():
    if flask_login.current_user.is_authenticated:
        priests = db.get_priests()
        return render_template('in/conf_add.html', is_logged_in=True, priests=priests,)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/confirmation/insert', methods=['POST'])
def insert_conf():
    print('Insert Data Confirmation')
    if request.method == "POST":
        print('Found Data')
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request Confirmation: {data}')

        # Extract values from data
        first_name = data.get('fname')
        middle_name = data.get('mname')
        last_name = data.get('lname')
        birthday = data.get('birthday')
        birthplace = data.get('birthplace')
        ligitivity = data.get('ligitivity')
        address = data.get('address')
        church_baptized = data.get('church_bapt')

        mother_fname = data.get('mother-fname')
        mother_mname = data.get('mother-mname')
        mother_lname = data.get('mother-lname')
        mother_birthday = data.get('mother-birthday')
        mother_birthplace = data.get('mother-bplace')
        mother_address = data.get('mother-address')
        father_fname = data.get('father-fname')
        father_mname = data.get('father-mname')
        father_lname = data.get('father-lname')
        father_birthday = data.get('father-birthday')
        father_birthplace = data.get('father-bplace')
        father_address = data.get('father-address')

        confirmation_date = data.get('conf-date')
        priest = data.get('priest')
        sponsor1 = data.get('sponsor1')
        sponsor2 = data.get('sponsor2')

        conf_index = data.get('conf-index')
        conf_book = data.get('conf-book')
        conf_page = data.get('conf-page')
        conf_line = data.get('conf-line')
    
        # Call the function to insert the data into the database
        try:
            # Check if client already exists
            existing_user = db.check_existing_client(first_name, last_name, birthday)
            if existing_user:
                client_id = existing_user['id']
                print(f"Client already exists with ID: {client_id}")
            else:
                # Check if parents already exist
                existing_parents = db.check_existing_parents(mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace, father_fname, father_mname, father_lname, father_birthday, father_birthplace)

                mother_id = existing_parents['mother']['parent_id'] if existing_parents['mother'] else None
                father_id = existing_parents['father']['parent_id'] if existing_parents['father'] else None

                # Insert mother if not exists
                if mother_id is None:
                    mother_id = db.insert_parent(mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace, mother_address, 'mother')

                # Insert father if not exists
                if father_id is None:
                    father_id = db.insert_parent(father_fname, father_mname, father_lname, father_birthday, father_birthplace, father_address, 'father')

                # Insert client data
                client_id = db.insert_client(first_name, middle_name, last_name, birthday, ligitivity, birthplace, address, mother_id, father_id)
                print("Data inserted successfully, here is the client ID: ", client_id)
           
            # Insert baptism data
            db.insert_confirmation(client_id, confirmation_date, church_baptized, sponsor1, sponsor2, priest, conf_index, conf_book, conf_page, conf_line)

            return jsonify({'message': 'Data Inserted Successfully'})
        
        except Exception as e:
            return jsonify({'message': f"Error: {str(e)}"}), 500

@bp.route('/confirmation/edit/<int:id>', methods=['GET', 'POST'])
def edit_conf(id):
    if flask_login.current_user.is_authenticated:
        priests = db.get_priests()
        return render_template('in/conf_edit.html', is_logged_in=True, id=id, priests=priests,)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/confirmation/update', methods=['PUT'])
def update_conf():
    print('Update Confirmation Data')
    if request.method == "PUT":
        print('Found Data')
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request (update): {data}')
        
        # Extract values from data
        confirmation_id = data.get('id')
        client_id = data.get('client_id')
        first_name = data.get('fname')
        middle_name = data.get('mname')
        last_name = data.get('lname')
        birthday = data.get('birthday')
        birthplace = data.get('birthplace')
        ligitivity = data.get('ligitivity')
        address = data.get('address')
        church_baptized = data.get('church_bapt')
        mother_fname = data.get('mother-fname')
        mother_mname = data.get('mother-mname')
        mother_lname = data.get('mother-lname')
        mother_birthday = data.get('mother-birthday')
        mother_birthplace = data.get('mother-bplace')
        mother_address = data.get('mother-address')
        father_fname = data.get('father-fname')
        father_mname = data.get('father-mname')
        father_lname = data.get('father-lname')
        father_birthday = data.get('father-birthday')
        father_birthplace = data.get('father-bplace')
        father_address = data.get('father-address')
        date = data.get('conf-date')
        priest = data.get('priest')
        sponsor1 = data.get('sponsor1')
        sponsor2 = data.get('sponsor2')

        try:
            # Get parent IDs
            mother_id = db.get_parent_id(client_id, 'mother')
            father_id = db.get_parent_id(client_id, 'father')

            # Update parents data
            if mother_id:
                db.update_parent(mother_id, mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace, mother_address)
                print("Mother data updated successfully.")
            if father_id:
                db.update_parent(father_id, father_fname, father_mname, father_lname, father_birthday, father_birthplace, father_address)
                print("Father data updated successfully.")

            # Update client data
            db.update_client(client_id, first_name, middle_name, last_name, birthday, ligitivity, birthplace, address)
            print("Client data updated successfully.")

            # Update baptism data
            db.update_confirmation_record(confirmation_id, church_baptized, date, sponsor1, sponsor2, priest)
            print("Confirmation data updated successfully.")

            return jsonify({'message': 'Data Updated Successfully'})
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'message': f"Error: {str(e)}"}), 500
        
@bp.route('/confirmation/delete/<int:id>', methods=['DELETE'])
def delete_conf(id):
    print('Delete Data')
    try:
        # Call the function to delete the baptism data from the database
        db.delete_confirmation(id)
        return jsonify({'message': 'Data Deleted Successfully'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f"Error: {str(e)}"}), 500



@bp.route('/wedding', methods=['GET', 'POST'])
def wedding():
    if flask_login.current_user.is_authenticated:
        exisitng_wedding = db.get_wedding()
        print('\nFrom /wedding in frontend.py')
        print(f"EXISTING WEDDING: {exisitng_wedding}")
       
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON data for AJAX requests
            print('Got JSON Request\n\n')
            return jsonify(exisitng_wedding)
        else:
            # Render HTML template for regular requests
            return render_template('in/wedding.html', is_logged_in=True, exisitng_wedding=exisitng_wedding)
    else:
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/wedding/<int:wedding_id>', methods=['GET'])
def get_wedding_record(wedding_id):
    if flask_login.current_user.is_authenticated:
        wedding_record = db.view_wedding(wedding_id)  
        if wedding_record:
            print('Wedding Record found succesfully for display')
            return jsonify(wedding_record) 
        else:
            print('/n/nNo record found')
            return jsonify({'error': 'Record not found'}), 404
    else:
        return jsonify({'error': 'Unauthorized access'}), 401

@bp.route('/wedding/add', methods=['GET'])
def new_wedd():
    if flask_login.current_user.is_authenticated:
        priests = db.get_priests()
        return render_template('in/wedd_add.html', is_logged_in=True, priests=priests,)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

    print('Delete Data')
    try:
        # Call the function to delete the baptism data from the database
        db.delete_baptism(id)
        return jsonify({'message': 'Data Deleted Successfully'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f"Error: {str(e)}"}), 500

@bp.route('/wedding/insert', methods=['POST'])
def insert_wedd():
    print('Insert Data')
    if request.method == "POST":
        print('Found Data')
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request: {data}')

        # Extract values from data
        groom_fname = data.get('groom-fname')
        groom_mname = data.get('groom-mname')
        groom_lname = data.get('groom-lname')
        groom_bday = data.get('groom-bday')
        groom_bplace = data.get('groom-bplace')
        groom_ligitivity = data.get('groom-ligitivity')
        groom_address = data.get('groom-address')
        groom_status = data.get('groom-status')

        groom_mother_fname = data.get('groom-mother-fname')
        groom_mother_mname = data.get('groom-mother-mname')
        groom_mother_lname = data.get('groom-mother-lname')
        groom_mother_birthday = data.get('groom-mother-bday')
        groom_mother_birthplace = data.get('groom-mother-bplace')
        groom_mother_address = data.get('groom-mother-address')
        groom_father_fname = data.get('groom-father-fname')
        groom_father_mname = data.get('groom-father-mname')
        groom_father_lname = data.get('groom-father-lname')
        groom_father_birthday = data.get('groom-father-bday')
        groom_father_birthplace = data.get('groom-father-bplace')
        groom_father_address = data.get('groom-father-address')

        bride_fname = data.get('bride-fname')
        bride_mname = data.get('bride-mname')
        bride_lname = data.get('bride-lname')
        bride_bday = data.get('bride-bday')
        bride_bplace = data.get('bride-bplace')
        bride_ligitivity = data.get('bride-ligitivity')
        bride_address = data.get('bride-address')
        bride_status = data.get('bride-status')

        bride_mother_fname = data.get('bride-mother-fname')
        bride_mother_mname = data.get('bride-mother-mname')
        bride_mother_lname = data.get('bride-mother-lname')
        bride_mother_birthday = data.get('bride-mother-bday')
        bride_mother_birthplace = data.get('bride-mother-bplace')
        bride_mother_address = data.get('bride-mother-address')
        bride_father_fname = data.get('bride-father-fname')
        bride_father_mname = data.get('bride-father-mname')
        bride_father_lname = data.get('bride-father-lname')
        bride_father_birthday = data.get('bride-father-bday')
        bride_father_birthplace = data.get('bride-father-bplace')
        bride_father_address = data.get('bride-father-address')

        wedding_date = data.get('wedding-date')
        priest = data.get('priest')
        sponsor1 = data.get('sponsor1')
        sponsor2 = data.get('sponsor2')

        license_number = data.get('licenseNumber')
        civil_date = data.get('civilDate')
        civil_place = data.get('civilPlace')
        
        wedd_index = data.get('wedding-index')
        wedd_book = data.get('wedding-book')
        wedd_page = data.get('wedding-page')
        wedd_line = data.get('wedding-line')

  
        # Call the function to insert the data into the database
        try:
            # Check if client already exists
            exisiting_groom = db.check_existing_client(groom_fname, groom_lname, groom_bday)
            exisiting_bride = db.check_existing_client(bride_fname, bride_lname, bride_bday)
            if exisiting_groom or exisiting_bride:
                groom_id = exisiting_groom['id']
                bride_id = exisiting_bride['id']
                print(f"Groom already exists with ID: {groom_id}")
                print(f"Bride already exists with ID: {bride_id}")
            else:
                # Check if parents already exist
                print('Checking Parents')
                groom_existing_parents = db.check_existing_parents(groom_mother_fname, groom_mother_mname, groom_mother_lname, groom_mother_birthday, groom_mother_birthplace, 
                                                             groom_father_fname, groom_father_mname, groom_father_lname, groom_father_birthday, groom_father_birthplace)

                groom_mother_id = groom_existing_parents['mother']['parent_id'] if groom_existing_parents['mother'] else None
                groom_father_id = groom_existing_parents['father']['parent_id'] if groom_existing_parents['father'] else None

                bride_existing_parents = db.check_existing_parents(bride_mother_fname, bride_mother_mname, bride_mother_lname, bride_mother_birthday, bride_mother_birthplace, 
                                                             bride_father_fname, bride_father_mname, bride_father_lname, bride_father_birthday, bride_father_birthplace)

                bride_mother_id = bride_existing_parents['mother']['parent_id'] if bride_existing_parents['mother'] else None
                bride_father_id = bride_existing_parents['father']['parent_id'] if bride_existing_parents['father'] else None

                # Insert mother if not exists
                if groom_mother_id is None:
                    groom_mother_id = db.insert_parent(groom_mother_fname, groom_mother_mname, groom_mother_lname, groom_mother_birthday, groom_mother_birthplace, groom_mother_address, 'mother')

                # Insert father if not exists
                if groom_father_id is None:
                    groom_father_id = db.insert_parent(groom_father_fname, groom_father_mname, groom_father_lname, groom_father_birthday, groom_father_birthplace, groom_father_address, 'father')

                if bride_mother_id is None:
                    bride_mother_id = db.insert_parent(bride_mother_fname, bride_mother_mname, bride_mother_lname, bride_mother_birthday, bride_mother_birthplace, bride_mother_address, 'mother')
                
                if bride_father_id is None:
                    bride_father_id = db.insert_parent(bride_father_fname, bride_father_mname, bride_father_lname, bride_father_birthday, bride_father_birthplace, bride_father_address, 'father')

                # Insert client data
                groom_client_id = db.insert_client(groom_fname, groom_mname, groom_lname, groom_bday, groom_ligitivity, groom_bplace, groom_address, groom_status, groom_mother_id, groom_father_id)
                print("Data inserted successfully, here is the client ID: ", groom_client_id)

                bride_client_id = db.insert_client(bride_fname, bride_mname, bride_lname, bride_bday, bride_ligitivity, bride_bplace, bride_address, bride_status, bride_mother_id, bride_father_id)
                print("Data inserted successfully, here is the client ID: ", bride_client_id)
           
            # Insert baptism data
            print('Inserting Wedding')
            db.insert_wedding(groom_client_id, bride_client_id, wedding_date, sponsor1, sponsor2, priest, license_number, civil_date, civil_place, wedd_index, wedd_book, wedd_page, wedd_line)

            return jsonify({'message': 'Data Inserted Successfully'})
        
        except Exception as e:
            return jsonify({'message': f"Error: {str(e)}"}), 500

@bp.route('/wedding/edit/<int:id>', methods=['GET', 'POST'])
def edit_wedd(id):
    if flask_login.current_user.is_authenticated:
        priests = db.get_priests()
        return render_template('in/wedd_edit.html', is_logged_in=True, id=id, priests=priests,)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/wedding/update', methods=['PUT'])
def update_wedd():
    print('Update Wedding Data')
    if request.method == "PUT":
        print('Found Data')
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request (update): {data}')
        
        # Extract values from data
        wedding_id = data.get('id')
        groom_client_id = data.get('Groomclient_id')
        groom_first_name = data.get('groom-fname')
        groom_middle_name = data.get('groom-mname')
        groom_last_name = data.get('groom-lname')
        groom_bday = data.get('groom-bday')
        groom_bplace = data.get('groom-bplace')
        groom_ligitivity = data.get('groom-ligitivity')
        groom_address = data.get('groom-address')
        groom_status = data.get('groom-status')
        
        groom_mother_fname = data.get('groom-mother-fname')
        groom_mother_mname = data.get('groom-mother-mname')
        groom_mother_lname = data.get('groom-mother-lname')
        groom_mother_birthday = data.get('groom-mother-bday')
        groom_mother_birthplace = data.get('groom-mother-bplace')
        groom_mother_address = data.get('groom-mother-address')
        groom_father_fname = data.get('groom-father-fname')
        groom_father_mname = data.get('groom-father-mname')
        groom_father_lname = data.get('groom-father-lname')
        groom_father_birthday = data.get('groom-father-bday')
        groom_father_birthplace = data.get('groom-father-bplace')
        groom_father_address = data.get('groom-father-address')

        bride_client_id = data.get('Brideclient_id')
        bride_first_name = data.get('bride-fname')
        bride_middle_name = data.get('bride-mname')
        bride_last_name = data.get('bride-lname')
        bride_bday = data.get('bride-bday')
        bride_bplace = data.get('bride-bplace')
        bride_ligitivity = data.get('bride-ligitivity')
        bride_address = data.get('bride-address')
        bride_status = data.get('bride-status')
        
        bride_mother_fname = data.get('bride-mother-fname')
        bride_mother_mname = data.get('bride-mother-mname')
        bride_mother_lname = data.get('bride-mother-lname')
        bride_mother_birthday = data.get('bride-mother-bday')
        bride_mother_birthplace = data.get('bride-mother-bplace')
        bride_mother_address = data.get('bride-mother-address')
        bride_father_fname = data.get('bride-father-fname')
        bride_father_mname = data.get('bride-father-mname')
        bride_father_lname = data.get('bride-father-lname')
        bride_father_birthday = data.get('bride-father-bday')
        bride_father_birthplace = data.get('bride-father-bplace')
        bride_father_address = data.get('bride-father-address')


        date = data.get('wedd-date')
        priest = data.get('priest')
        sponsor1 = data.get('sponsor1')
        sponsor2 = data.get('sponsor2')
        licenseNumber = data.get('licenseNumber')
        civilDate = data.get('civilDate')
        civilPlace = data.get('civilPlace')

        try:
            # Get parent IDs
            groom_mother_id = db.get_parent_id(groom_client_id, 'mother')
            groom_father_id = db.get_parent_id(groom_client_id, 'father')

            # Update parents data
            if groom_mother_id:
                db.update_parent(groom_mother_id, groom_mother_fname,  groom_mother_mname,  groom_mother_lname,  groom_mother_birthday,  groom_mother_birthplace,  groom_mother_address)
                print("Mother data updated successfully.")
            if groom_father_id:
                db.update_parent(groom_father_id,  groom_father_fname,  groom_father_mname,  groom_father_lname,  groom_father_birthday,  groom_father_birthplace,  groom_father_address)
                print("Father data updated successfully.")

            # Get parent IDs
            bride_address_mother_id = db.get_parent_id(groom_client_id, 'mother')
            bride_father_id = db.get_parent_id(groom_client_id, 'father')

            # Update parents data
            if bride_address_mother_id:
                db.update_parent(bride_address_mother_id, bride_mother_fname,  bride_mother_mname,  bride_mother_lname,  bride_mother_birthday,  bride_mother_birthplace,  bride_mother_address)
                print("Mother data updated successfully.")
            if bride_father_id:
                db.update_parent(bride_father_id,  bride_father_fname,  bride_father_mname,  bride_father_lname,  bride_father_birthday,  bride_father_birthplace,  bride_father_address)
                print("Father data updated successfully.")

            # Update client data
            db.update_client(groom_client_id, groom_first_name, groom_middle_name, groom_last_name, groom_bday, groom_ligitivity, groom_bplace, groom_address, groom_status)
            print("Client data updated successfully.")

            db.update_client(bride_client_id, bride_first_name, bride_middle_name, bride_last_name, bride_bday, bride_ligitivity, bride_bplace, bride_address, bride_status)
            print("Client data updated successfully.")

            # Update baptism data
            db.update_wedding_record(wedding_id, date, sponsor1, sponsor2, licenseNumber, civilDate, civilPlace, priest)
            print("Confirmation data updated successfully.")

            return jsonify({'message': 'Data Updated Successfully'})
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'message': f"Error: {str(e)}"}), 500

@bp.route('/wedding/delete/<int:id>', methods=['DELETE'])
def delete_wedd(id):
    print('Delete Data')
    try:
        # Call the function to delete the baptism data from the database
        db.delete_wedding(id)
        return jsonify({'message': 'Data Deleted Successfully'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f"Error: {str(e)}"}), 500




@bp.route('/death', methods=['GET', 'POST'])
def death():
    if flask_login.current_user.is_authenticated:
        exisiting_death = db.get_death()
        print('\nFrom /death in frontend.py')
        print(f"EXISTING BAPTISM: {exisiting_death}")
       
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON data for AJAX requests
            print('Got JSON Request\n\n')
            return jsonify(exisiting_death)
        else:
            # Render HTML template for regular requests
            return render_template('in/death.html', is_logged_in=True, exisiting_death=exisiting_death)
    else:
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/death/<int:death_id>', methods=['GET'])
def get_death_record(death_id):
    if flask_login.current_user.is_authenticated:
        death_record = db.view_death(death_id)  
        if death_record:
            return jsonify(death_record) 
        else:
            return jsonify({'error': 'Record not found'}), 404
    else:
        return jsonify({'error': 'Unauthorized access'}), 401

@bp.route('/death/add', methods=['GET'])
def new_death():
    if flask_login.current_user.is_authenticated:
        priests = db.get_priests()
        return render_template('in/death_add.html', is_logged_in=True, priests=priests,)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/death/insert', methods=['POST'])
def insert_death():
    print('Insert Data')
    if request.method == "POST":
        print('Found Data')
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request: {data}')

        # Extract values from data
        first_name = data.get('fname')
        middle_name = data.get('mname')
        last_name = data.get('lname')
        birthday = data.get('birthday')
        birthplace = data.get('birthplace')
        ligitivity = data.get('ligitivity')
        address = data.get('address')
        status = data.get('status')

        mother_fname = data.get('mother-fname')
        mother_mname = data.get('mother-mname')
        mother_lname = data.get('mother-lname')
        mother_birthday = data.get('mother-birthday')
        mother_birthplace = data.get('mother-bplace')
        mother_address = data.get('mother-address')
        father_fname = data.get('father-fname')
        father_mname = data.get('father-mname')
        father_lname = data.get('father-lname')
        father_birthday = data.get('father-birthday')
        father_birthplace = data.get('father-bplace')
        father_address = data.get('father-address')

        death_date = data.get('death-date')
        burial_date = data.get('burial-date')
        cause = data.get('death-cause')
        burial_place = data.get('burial-place')
        contact_person = data.get('death-cp')
        address = data.get('death-cpAddress')
        priest = data.get('priest')
        
        death_index = data.get('death-index')
        death_book = data.get('death-book')
        death_page = data.get('death-page')
        death_line = data.get('death-line')
    
        # Call the function to insert the data into the database
        try:
            # Check if client already exists
            existing_user = db.check_existing_client(first_name, last_name, birthday)
            if existing_user:
                client_id = existing_user['id']
                print(f"Client already exists with ID: {client_id}")
            else:
                # Check if parents already exist
                existing_parents = db.check_existing_parents(mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace, father_fname, father_mname, father_lname, father_birthday, father_birthplace)

                mother_id = existing_parents['mother']['parent_id'] if existing_parents['mother'] else None
                father_id = existing_parents['father']['parent_id'] if existing_parents['father'] else None

                # Insert mother if not exists
                if mother_id is None:
                    mother_id = db.insert_parent(mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace, mother_address, 'mother')

                # Insert father if not exists
                if father_id is None:
                    father_id = db.insert_parent(father_fname, father_mname, father_lname, father_birthday, father_birthplace, father_address, 'father')

                # Insert client data
                client_id = db.insert_client(first_name, middle_name, last_name, birthday, ligitivity, birthplace, address, status, mother_id, father_id)
                print("Data inserted successfully, here is the client ID: ", client_id)
           
            # Insert baptism data
            db.insert_death(client_id, death_date, burial_date, cause, burial_place, contact_person, address, priest, death_index, death_book, death_page, death_line)

            return jsonify({'message': 'Data Inserted Successfully'})
        
        except Exception as e:
            return jsonify({'message': f"Error: {str(e)}"}), 500

@bp.route('/death/edit/<int:id>', methods=['GET', 'POST'])
def edit_death(id):
    if flask_login.current_user.is_authenticated:
        priests = db.get_priests()
        return render_template('in/death_edit.html', is_logged_in=True, id=id, priests=priests,)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/death/update', methods=['PUT'])
def update_death():
    print('Update Baptism Data')
    if request.method == "PUT":
        print('Found Data')
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request DEATH(update): {data}')
        
        # Extract values from data
        death_id = data.get('id')
        client_id = data.get('client_id')
        first_name = data.get('fname')
        middle_name = data.get('mname')
        last_name = data.get('lname')
        birthday = data.get('birthday')
        birthplace = data.get('birthplace')
        ligitivity = data.get('ligitivity')
        address = data.get('address')
        status = data.get('status')
        mother_fname = data.get('mother-fname')
        mother_mname = data.get('mother-mname')
        mother_lname = data.get('mother-lname')
        mother_birthday = data.get('mother-birthday')
        mother_birthplace = data.get('mother-bplace')
        mother_address = data.get('mother-address')
        father_fname = data.get('father-fname')
        father_mname = data.get('father-mname')
        father_lname = data.get('father-lname')
        father_birthday = data.get('father-birthday')
        father_birthplace = data.get('father-bplace')
        father_address = data.get('father-address')

        death_date = data.get('death_date')
        burial_date = data.get('burial-date')
        cause = data.get('death-cause')
        burial_place = data.get('burial-place')
        contact_person = data.get('death-cp')
        address = data.get('death-cpAddress')
        priest = data.get('priest')
       
        print('\n\n', death_date)
        try:
            # Get parent IDs
            mother_id = db.get_parent_id(client_id, 'mother')
            father_id = db.get_parent_id(client_id, 'father')

            # Update parents data
            if mother_id:
                db.update_parent(mother_id, mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace, mother_address)
                print("Mother data updated successfully.")
            if father_id:
                db.update_parent(father_id, father_fname, father_mname, father_lname, father_birthday, father_birthplace, father_address)
                print("Father data updated successfully.")

            # Update client data
            db.update_client(client_id, first_name, middle_name, last_name, birthday, ligitivity, birthplace, address, status)
            print("Client data updated successfully.")

            # Update baptism data
            db.update_death_record(death_id, death_date, burial_date, cause, burial_place, contact_person, address, priest)
            print("Death data updated successfully.")

            return jsonify({'message': 'Data Updated Successfully'})
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'message': f"Error: {str(e)}"}), 500
        
@bp.route('/death/delete/<int:id>', methods=['DELETE'])
def delete_death(id):
    print('Delete Data')
    try:
        # Call the function to delete the baptism data from the database
        db.delete_death(id)
        return jsonify({'message': 'Data Deleted Successfully'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f"Error: {str(e)}"}), 500




@bp.route('/priest', methods=['GET', 'POST'])
def priest():
    if flask_login.current_user.is_authenticated:
        exisitng_priests = db.get_priests()
        print('\nFrom /priest in frontend.py')
        print(f"EXISTING Priest: {exisitng_priests}")
       
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Return JSON data for AJAX requests
            print('Got JSON Request\n\n')
            return jsonify(exisitng_priests)
        else:
            # Render HTML template for regular requests
            return render_template('in/priest.html', is_logged_in=True, exisitng_priests=exisitng_priests)
    else:
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/priest/<int:priest_id>', methods=['GET'])
def get_priest_record(priest_id):
    if flask_login.current_user.is_authenticated:
        priest_record = db.view_priest(priest_id)  
        print(f"PRIEST RECORD: {priest_record}")
        if priest_record:
            print('Priest Record found succesfully for display')
            return jsonify(priest_record) 
        else:
            return jsonify({'error': 'Record not found'}), 404
    else:
        return jsonify({'error': 'Unauthorized access'}), 401

@bp.route('/priest/insert', methods=['POST'])
def insert_priest():
    print('Insert Data')
    if request.method == "POST":
        print('Found Data')
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request: {data}')

        # Extract values from data
        name = data.get('name')
        church = data.get('church')
        position = data.get('position')
    
        # Call the function to insert the data into the database
        try:
            db.insert_priest(name, church, position)

            return jsonify({'message': 'Data Inserted Successfully'})
        
        except Exception as e:
            return jsonify({'message': f"Error: {str(e)}"}), 500

@bp.route('/priest/add', methods=['GET'])
def new_priest():
    if flask_login.current_user.is_authenticated:
        priests = db.get_priests()
        return render_template('in/priest.html', is_logged_in=True, priests=priests,)
        
    else: 
        return render_template('out/login.html', is_logged_in=False)

@bp.route('/priest/update', methods=['PUT'])
def update_priest():
    print('Update Priest Data')
    if request.method == "PUT":
        print('Found Data')
        # Collect form data
        data = request.get_json()
        print(f'Data from JSON Request (update): {data}')
        
        # Extract values from data
        priest_id = data.get('id')
        name = data.get('name')
        church = data.get('church')
        position = data.get('position')
        status = data.get('status')

        try:
            print('Data for the priest:', {priest_id, name, church, position, status})
            db.update_priest_record(priest_id, name, church, position, status)
            print("Priest data updated successfully.")

            return jsonify({'message': 'Data Updated Successfully'})
        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'message': f"Error: {str(e)}"}), 500
        
@bp.route('/priest/delete/<int:id>', methods=['DELETE'])
def delete_priest(id):
    print('Delete Data')
    try:
        # Call the function to delete the baptism data from the database
        db.delete_priest(id)
        return jsonify({'message': 'Data Deleted Successfully'})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'message': f"Error: {str(e)}"}), 500
