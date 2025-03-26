import mysql.connector
import bcrypt
import flask_login
from dataclasses import dataclass
from mysql.connector import Error
from app.db_connection import get_db_connection


class UsernameAlreadyExistsException(Exception):
    pass


@dataclass
class User(flask_login.UserMixin):
    """ A representation of a user. It is used by flask-login and can be persisted in the database."""
    user_id: int = None
    username: str = None
    firstname: str = None
    middlename: str = None
    lastname: str = None
    contact_number: str = None
    joined: str = None
    fido_info: str = None

    def get_id(self):
        return self.user_id


def create_user(firstname: str, middlename: str, lastname: str, username: str, contact_number: str) -> User:
    """Creates a new user in the database."""
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if username already exists
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()

    if existing_user:
        raise UsernameAlreadyExistsException("Username already taken")
    
    # Insert new user into the database
    cursor.execute("""
        INSERT INTO users (fname, mname, lname, username, contact_number)
        VALUES (%s, %s, %s, %s, %s)
    """, (firstname, middlename, lastname, username, contact_number))

    connection.commit()

    # Get the newly inserted user
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return User(user_id=user_data['id'], username=user_data['username'], firstname=user_data['fname'],
                middlename=user_data['mname'], lastname=user_data['lname'],  fido_info=user_data.get('fido_info', ''))

def load_user(username: str = '', user_id: int = -1) -> User:
    """Load a user from the database by username or user_id."""
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    cursor = connection.cursor(dictionary=True)

    if user_id >= 0:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
    elif username:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()

    cursor.close()
    connection.close()

    if user_data:
            return User(user_id=user_data['id'], username=user_data['username'], firstname=user_data['fname'],
                middlename=user_data['mname'], lastname=user_data['lname'],  fido_info=user_data.get('fido_info', ''))
    else:
        return None

def set_fido_info(user_id: int, fido_info: str):
    """Add fido info to an existing user."""
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    cursor = connection.cursor()
    cursor.execute("UPDATE users SET fido_info = %s WHERE id = %s", (fido_info, user_id))

    connection.commit()
    cursor.close()
    connection.close()

def authenticate_user(username: str) -> User:
    """Authenticate the user based on username."""
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()

    cursor.close()
    connection.close()
    
    if user_data:
            return User(user_id=user_data['id'], username=user_data['username'], firstname=user_data['fname'],
                middlename=user_data['mname'], lastname=user_data['lname'],  fido_info=user_data.get('fido_info', ''))
    else:
        return None
    
def view_accnt(user_id):
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()

    cursor.close()
    connection.close()

    print('USER DATA')
    print(user_data)
    
    if user_data:
            return User(user_id=user_data['id'], username=user_data['username'], firstname=user_data['fname'],
                middlename=user_data['mname'], lastname=user_data['lname'],  contact_number=user_data['contact_number'], 
                joined=user_data['created_at'])
    else:
        return None

def update_recovery_number(user_id, contact_number):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        UPDATE users
        SET contact_number = %s
        WHERE id = %s
    """, (contact_number, user_id))
    connection.commit()
    cursor.close()
    connection.close()

def deleteFidoInfo(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        UPDATE users
        SET fido_info = NULL
        WHERE id = %s
    """, (user_id,))
    connection.commit()
    cursor.close()
    connection.close()


def get_ceremony_count():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
                SELECT 'baptism' AS ceremony, COUNT(*) AS record_count FROM baptism
                UNION ALL
                SELECT 'confirmation', COUNT(*) FROM confirmation
                UNION ALL
                SELECT 'wedding', COUNT(*) FROM wedding
                UNION ALL
                SELECT 'death', COUNT(*) FROM death;
                   """)
   
    ceremony_count = cursor.fetchall()

    for row in ceremony_count:
        print(row)
    cursor.close()
    connection.close()
    return ceremony_count                                      


def get_priests():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM priest")
    priests = cursor.fetchall()
    cursor.close()
    connection.close()
    return priests

def view_priest(priest_id):
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    print("This is the priest ID: ", {priest_id})
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    SELECT * FROM `priest` WHERE id= %s;
                    ''', (priest_id,))
    additional_priest_info = cursor.fetchone()

    print('EXISTING PRIEST')
    print(additional_priest_info)
    
    if additional_priest_info:
        return additional_priest_info
    else:
        return None 

def insert_priest(name, church, position):
    print(f"Inserting priest with data: name = {name}, church = {church}, position = {position}")
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO priest (name, church, position)
        VALUES (%s, %s, %s)
    """, (name, church, position))
    connection.commit()
    cursor.close()
    connection.close()

def update_priest_record(priest_id, name, church, position, status):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        UPDATE priest
        SET name = %s, church = %s, position = %s, status = %s
        WHERE id = %s
    """, (name, church, position, status, priest_id))
    connection.commit()
    cursor.close()
    connection.close()

def delete_priest(priest_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        DELETE FROM priest
        WHERE id = %s
    """, (priest_id,))
    connection.commit()
    cursor.close()
    connection.close()


def check_existing_client(fname, lname, birthday):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM client 
        WHERE fname = %s AND lname = %s AND birthday = %s;
    """, (fname, lname, birthday))
    existing_user = cursor.fetchone()
    cursor.close()
    connection.close()
    return existing_user

def check_existing_parents(mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace, 
                           father_fname, father_mname, father_lname, father_birthday, father_birthplace):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Check for mother
    cursor.execute("""
        SELECT id AS parent_id
        FROM parents
        WHERE fname = %s AND mname = %s AND lname = %s AND birthday = %s AND birthplace = %s AND role = 'mother'
    """, (mother_fname, mother_mname, mother_lname, mother_birthday, mother_birthplace))
    mother = cursor.fetchone()

    # Check for father
    cursor.execute("""
        SELECT id AS parent_id
        FROM parents
        WHERE fname = %s AND mname = %s AND lname = %s AND birthday = %s AND birthplace = %s AND role = 'father'
    """, (father_fname, father_mname, father_lname, father_birthday, father_birthplace))
    father = cursor.fetchone()
    
    cursor.close()
    connection.close()
    return {'mother': mother, 'father': father}


def get_records():
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    SELECT 
                        c.*, 
                        mother.fname AS mother_fname,
                        mother.mname AS mother_mname,
                        mother.lname AS mother_lname,
                        mother.birthday AS mother_birthday,
                        mother.birthplace AS mother_bplace,
                        mother.address AS mother_address,
                        father.fname AS father_fname,
                        father.mname AS father_mname,
                        father.lname AS father_lname,
                        father.birthday AS father_birthday,
                        father.birthplace AS father_bplace,
                        father.address AS father_address,
                        b.rec_index AS bapt_index, 
                        b.rec_book AS bapt_book, 
                        b.rec_page AS bapt_page, 
                        b.rec_line AS bapt_line,
                        conf.rec_index AS conf_index, 
                        conf.rec_book AS conf_book, 
                        conf.rec_page AS conf_page, 
                        conf.rec_line AS conf_line 
                    FROM 
                        client c
                    LEFT JOIN 
                        baptism b ON c.id = b.client_id
                   LEFT JOIN 
                        confirmation conf ON c.id = conf.client_id
                    LEFT JOIN 
                        parents mother ON c.mother_id = mother.id
                    LEFT JOIN 
                        parents father ON c.father_id = father.id;
                    ''')
    existing_clients = cursor.fetchall()

    print('EXISTING CLIENTS from db.py')
    print(existing_clients)
    
    if existing_clients:
        return existing_clients
    else:
        return None

def get_parent_id(client_id, role):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    column = 'mother_id' if role == 'mother' else 'father_id'
    cursor.execute(f"SELECT {column} AS parent_id FROM client WHERE id = %s", (client_id,))
    parent = cursor.fetchone()
    cursor.close()
    connection.close()
    return parent['parent_id'] if parent else None

def insert_parent(fname, mname, lname, birthday, birthplace, address, role):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO parents (fname, mname, lname, birthday, birthplace, address, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (fname, mname, lname, birthday, birthplace, address, role))
    connection.commit()
    parent_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return parent_id

def insert_client(fname, mname, lname, birthday, ligitivity, birthplace, address, status, mother, father):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO client (fname, mname, lname, birthday, ligitivity, birthplace, address, status, mother_id, father_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (fname, mname, lname, birthday, ligitivity, birthplace, address, status, mother, father))
    connection.commit()
    client_id = cursor.lastrowid
    cursor.close()
    connection.close()
    return client_id

def update_client(client_id, fname, mname, lname, birthday, ligitivity, birthplace, address, status):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        UPDATE client
        SET fname = %s, mname = %s, lname = %s, birthday = %s, ligitivity = %s, birthplace = %s, address = %s, status = %s
        WHERE id = %s
    """, (fname, mname, lname, birthday, ligitivity, birthplace, address, status, client_id))
    connection.commit()
    cursor.close()
    connection.close()

def update_parent(parent_id, fname, mname, lname, birthday, birthplace, address):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        UPDATE parents
        SET fname = %s, mname = %s, lname = %s, birthday = %s, birthplace = %s, address = %s
        WHERE id = %s
    """, (fname, mname, lname, birthday, birthplace, address, parent_id))
    connection.commit()
    cursor.close()
    connection.close()


def get_baptism():
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    SELECT 
                        b.id,
                        c.id AS client_id,
                        c.fname, 
                        c.mname,
                        c.lname,
                        c.birthday,
                        c.address,
                        b.baptism_date,
                        p.id AS priest_id,
                        p.name AS priest_name,
                        mother.fname AS mother_fname,
                        mother.mname AS mother_mname,
                        mother.lname AS mother_lname,
                        father.fname AS father_fname,
                        father.mname AS father_mname,
                        father.lname AS father_lname
                    FROM 
                        baptism b
                    JOIN 
                        client c ON b.client_id = c.id
                    LEFT JOIN 
                        priest p ON b.priest_id = p.id
                    LEFT JOIN 
                        parents mother ON c.mother_id = mother.id
                    LEFT JOIN 
                        parents father ON c.father_id = father.id;
                    ''')
    existing_baptism = cursor.fetchall()

    print('EXISTING BAPTISM')
    print(existing_baptism)
    
    if existing_baptism:
        return existing_baptism
    else:
        return None

def view_baptism(bapt_id):
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    print("This is the baptism ID: ", {bapt_id})
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    SELECT 
                        b.id,
                        c.id AS client_id,
                        c.fname, 
                        c.mname,
                        c.lname,
                        c.birthday,
                        c.birthplace,
                        c.ligitivity,
                        c.address,
                        c.status,
                        b.baptism_date,
                        b.sponsorA,
                        b.residenceA,
                        b.sponsorB,
                        b.residenceB,
                        p.id AS priest_id,
                        p.name AS priest_name,
                        mother.fname AS mother_fname,
                        mother.mname AS mother_mname,
                        mother.lname AS mother_lname,
                        mother.birthday AS mother_birthday,
                        mother.birthplace AS mother_bplace,
                        mother.address AS mother_address,
                        father.fname AS father_fname,
                        father.mname AS father_mname,
                        father.lname AS father_lname,
                        father.birthday AS father_birthday,
                        father.birthplace AS father_bplace,
                        father.address AS father_address,
                        b.rec_index,
                        b.rec_book,
                        b.rec_page,
                        b.rec_line
                    FROM 
                        baptism b
                    JOIN 
                        client c ON b.client_id = c.id
                    LEFT JOIN 
                        priest p ON b.priest_id = p.id
                    LEFT JOIN 
                        parents mother ON c.mother_id = mother.id
                    LEFT JOIN 
                        parents father ON c.father_id = father.id
                    WHERE b.id = %s;
                    ''', (bapt_id,))
    additional_bapt_info = cursor.fetchone()

    print('EXISTING BAPTISM')
    print(additional_bapt_info)
    
    if additional_bapt_info:
        return additional_bapt_info
    else:
        return None

def insert_baptism(client_id, baptism_date, sponsor1, sponsor1_residence, sponsor2, sponsor2_residence, priest_id, bapt_index, bapt_book, bapt_page, bapt_line):
    print(f"Inserting baptism with data: client_id={client_id}, baptism_date={baptism_date}, sponsorA={sponsor1}, residenceA={sponsor1_residence}, sponsorB={sponsor2}, residenceB={sponsor2_residence}, priest_id={priest_id}, rec_index={bapt_index}, rec_book={bapt_book}, rec_page={bapt_page}, rec_line={bapt_line}")
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO baptism (client_id, baptism_date, sponsorA, residenceA, sponsorB, residenceB, priest_id, rec_index, rec_book, rec_page, rec_line)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (client_id, baptism_date, sponsor1, sponsor1_residence, sponsor2, sponsor2_residence, priest_id, bapt_index, bapt_book, bapt_page, bapt_line))
    connection.commit()
    cursor.close()
    connection.close()

def update_baptism_record(baptism_id, date, sponsor1, sponsor1_residence, sponsor2, sponsor2_residence, priest):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        UPDATE baptism
        SET baptism_date = %s, sponsorA = %s, residenceA = %s, sponsorB = %s, residenceB = %s, priest_id = %s
        WHERE id = %s
    """, (date, sponsor1, sponsor1_residence, sponsor2, sponsor2_residence, priest, baptism_id))
    connection.commit()
    cursor.close()
    connection.close()

def delete_baptism(baptism_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        DELETE FROM baptism
        WHERE id = %s
    """, (baptism_id,))
    connection.commit()
    cursor.close()
    connection.close()


def get_confirmation():
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    SELECT 
                        conf.id,
                        c.id AS client_id,
                        c.fname, 
                        c.mname,
                        c.lname,
                        c.birthday,
                        c.address,
                        conf.confirmation_date,
                        p.id AS priest_id,
                        p.name AS priest_name,
                        mother.fname AS mother_fname,
                        mother.mname AS mother_mname,
                        mother.lname AS mother_lname,
                        father.fname AS father_fname,
                        father.mname AS father_mname,
                        father.lname AS father_lname
                    FROM 
                        confirmation conf
                    JOIN 
                        client c ON conf.client_id = c.id
                    LEFT JOIN 
                        priest p ON conf.priest_id = p.id
                    LEFT JOIN 
                        parents mother ON c.mother_id = mother.id
                    LEFT JOIN 
                        parents father ON c.father_id = father.id;
                    ''')
    existing_confirmation = cursor.fetchall()

    print('EXISTING CONFIRMATION')
    print(existing_confirmation)
    
    if existing_confirmation:
        return existing_confirmation
    else:
        return None

def view_confirmation(conf_id):
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    print("This is the confirmation ID: ", {conf_id})
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    SELECT 
                        conf.id,
                        c.id AS client_id,
                        c.fname, 
                        c.mname,
                        c.lname,
                        c.birthday,
                        c.birthplace,
                        c.ligitivity,
                        c.address,
                        conf.confirmation_date,
                        conf.church_baptized,
                        conf.sponsorA,
                        conf.sponsorB,
                        p.id AS priest_id,
                        p.name AS priest_name,
                        mother.fname AS mother_fname,
                        mother.mname AS mother_mname,
                        mother.lname AS mother_lname,
                        mother.birthday AS mother_birthday,
                        mother.birthplace AS mother_bplace,
                        mother.address AS mother_address,
                        father.fname AS father_fname,
                        father.mname AS father_mname,
                        father.lname AS father_lname,
                        father.birthday AS father_birthday,
                        father.birthplace AS father_bplace,
                        father.address AS father_address,
                        conf.rec_index,
                        conf.rec_book,
                        conf.rec_page,
                        conf.rec_line
                    FROM 
                        confirmation conf
                    JOIN 
                        client c ON conf.client_id = c.id
                    LEFT JOIN 
                        priest p ON conf.priest_id = p.id
                    LEFT JOIN 
                        parents mother ON c.mother_id = mother.id
                    LEFT JOIN 
                        parents father ON c.father_id = father.id
                    WHERE conf.id = %s;
                    ''', (conf_id,))
    additional_conf_info = cursor.fetchone()

    print('EXISTING CONFIRMATION')
    print(additional_conf_info)
    
    if additional_conf_info:
        return additional_conf_info
    else:
        return None

def insert_confirmation(client_id, confirmation_date, church_baptized, sponsor1, sponsor2, priest_id, conf_index, conf_book, conf_page, conf_line):
    print(f"Inserting confirmation with data: client_id={client_id}, confirmation_date={confirmation_date}, church_baptized={church_baptized}, sponsorA={sponsor1}, sponsorB={sponsor2}, priest_id={priest_id}, rec_index={conf_index}, rec_book={conf_book}, rec_page={conf_page}, rec_line={conf_line}")
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO confirmation (client_id, confirmation_date, church_baptized, sponsorA, sponsorB, priest_id, rec_index, rec_book, rec_page, rec_line)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (client_id, confirmation_date, church_baptized, sponsor1, sponsor2, priest_id, conf_index, conf_book, conf_page, conf_line))
    connection.commit()
    cursor.close()
    connection.close()

def update_confirmation_record(confirmation_id, church_baptized, date, sponsor1, sponsor2, priest):
    connection = get_db_connection()
    print(f"Updating confirmation with data: confirmation_id={confirmation_id}, confirmation_date={date}, church_baptized={church_baptized}, sponsorA={sponsor1}, sponsorB={sponsor2}, priest_id={priest}")
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        UPDATE confirmation
        SET confirmation_date = %s, church_baptized = %s, sponsorA = %s, sponsorB = %s, priest_id = %s
        WHERE id = %s
    """, (date, church_baptized, sponsor1, sponsor2, priest, confirmation_id))
    connection.commit()
    cursor.close()
    connection.close()

def delete_confirmation(confirmation_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        DELETE FROM confirmation
        WHERE id = %s
    """, (confirmation_id,))
    connection.commit()
    cursor.close()
    connection.close()


def get_wedding():
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    SELECT 
                        wedd.id,
                        wedd.wedding_date,
                        groom.fname AS groom_fname,
                        groom.mname AS groom_mname,
                        groom.lname AS groom_lname,
                        groom.birthday AS groom_bday,
                        groom.status AS groom_status,
                        groom.address AS groom_address,
                        bride.fname AS bride_fname,
                        bride.mname AS bride_mname,
                        bride.lname AS bride_lname,
                        bride.birthday AS bride_bday,
                        bride.status AS bride_status,
                        bride.address AS bride_address,
                        p.name AS priest_name
                    FROM 
                        wedding wedd
                    LEFT JOIN 
                        client groom ON wedd.groom_client_id = groom.id  
                    LEFT JOIN 
                        client bride ON wedd.bride_client_id = bride.id  
                    LEFT JOIN 
                        priest p ON wedd.priest_id = p.id;
                    ''')
    existing_wedding = cursor.fetchall()

    print('EXISTING WEDDING')
    print(existing_wedding)
    
    if existing_wedding:
        return existing_wedding
    else:
        return None

def view_wedding(wedd_id):
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    print("This is the wedding ID: ", {wedd_id})
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    SELECT 
						wedd.id,
                        wedd.wedding_date,
                        groom.id AS groom_client_id,
                        groom.fname AS groom_fname,
                        groom.mname AS groom_mname,
                        groom.lname AS groom_lname,
                        groom.birthday AS groom_bday,
                        groom.ligitivity AS groom_ligitivity,
                        groom.birthplace AS groom_bplace,
                        groom.status AS groom_status,
                        groom.address AS groom_address,
                        groom_father.fname AS groomFaFname,
                        groom_father.mname AS groomFaMname,
                        groom_father.lname AS groomFaLname,
                        groom_father.birthday AS groomFaBday,
                        groom_father.birthplace AS groomFaBplace,
                        groom_father.address AS groomFaAddress,
                        groom_mother.fname AS groomMoFname,
                        groom_mother.mname AS groomMoMname,
                        groom_mother.lname AS groomMoLname,
                        groom_mother.birthday AS groomMoBday,
                        groom_mother.birthplace AS groomMoBplace,
                        groom_mother.address AS groomMoAddress,
                        bride.id AS bride_client_id,
                        bride.fname AS bride_fname,
                        bride.mname AS bride_mname,
                        bride.lname AS bride_lname,
                        bride.birthday AS bride_bday,
                        bride.ligitivity AS bride_ligitivity,
                        bride.birthplace AS bride_bplace,
                        bride.status AS bride_status,
                        bride.address AS bride_address,
                        bride_father.fname AS brideFaFname,
                        bride_father.mname AS brideFaMname,
                       	bride_father.lname AS brideFaLname,
                        bride_father.birthday AS brideFaBday,
                        bride_father.birthplace AS brideFaBplace,
                        bride_father.address AS brideFaAddress,
                        bride_mother.fname AS brideMoFname,
                        bride_mother.mname AS brideMoMname,
                        bride_mother.lname AS brideMoLname,
                        bride_mother.birthday AS brideMoBday,
                        bride_mother.birthplace AS brideMoBplace,
                        bride_mother.address AS brideMoAddress,
                        wedd.wedding_date,
                        wedd.sponsorA,
                        wedd.sponsorB,
                        wedd.license_number,
                        wedd.civil_date,
                        wedd.civil_place,
                        p.id AS priest_id,
                        p.name AS priest_name,
                        wedd.rec_index,
                        wedd.rec_book,
                        wedd.rec_page,
                        wedd.rec_line
                    FROM 
                        wedding wedd
                    LEFT JOIN 
                        client groom ON wedd.groom_client_id = groom.id  
                    LEFT JOIN 
                        client bride ON wedd.bride_client_id = bride.id  
                    LEFT JOIN 
                   	 	parents groom_father ON groom.father_id = groom_father.id
                    LEFT JOIN 
                    	parents groom_mother ON groom.mother_id = groom_mother.id
                    LEFT JOIN 
                    	parents bride_father ON bride.father_id = bride_father.id
                    LEFT JOIN 
                    	parents bride_mother ON bride.mother_id = bride_mother.id
                    LEFT JOIN 
                        priest p ON wedd.priest_id = p.id
                    WHERE wedd.id = %s;
                    ''', (wedd_id,))
    additional_wedd_info = cursor.fetchone()

    print('EXISTING WEDDING')
    print(additional_wedd_info)
    
    if additional_wedd_info:
        return additional_wedd_info
    else:
        return None

def insert_wedding(groom_client_id, bride_client_id, wedding_date, sponsor1, sponsor2, priest_id, license_number, civil_date, civil_place, wedd_index, wedd_book, wedd_page, wedd_line):
    print(f"Inserting wedding with data: client_id={groom_client_id} and {bride_client_id}, baptism_date={wedding_date}, sponsorA={sponsor1}, sponsorB={sponsor2}, priest_id={priest_id}, license = {license_number}, civil date = {civil_date}, civil place = {civil_place}, rec_index={wedd_index}, rec_book={wedd_book}, rec_page={wedd_page}, rec_line={wedd_line}")
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO wedding (groom_client_id, bride_client_id, wedding_date, sponsorA, sponsorB, priest_id, license_number, civil_date, civil_place, rec_index, rec_book, rec_page, rec_line)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (groom_client_id, bride_client_id, wedding_date, sponsor1, sponsor2, priest_id, license_number, civil_date, civil_place, wedd_index, wedd_book, wedd_page, wedd_line))
    connection.commit()
    cursor.close()
    connection.close()

def update_wedding_record(wedding_id, date, sponsor1, sponsor2, license_number, civilDate, civilPlace, priest):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        UPDATE wedding
        SET wedding_date = %s, sponsorA = %s, sponsorB = %s, license_number =%s, civil_date = %s, civil_place = %s, priest_id = %s
        WHERE id = %s
    """, (date, sponsor1, sponsor2, license_number, civilDate, civilPlace, priest, wedding_id))
    connection.commit()
    cursor.close()
    connection.close()

def delete_wedding(wedding_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        DELETE FROM wedding
        WHERE id = %s
    """, (wedding_id,))
    connection.commit()
    cursor.close()
    connection.close()




def get_death():
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    SELECT 
                        d.id,
                        c.id AS client_id,
                        c.fname, 
                        c.mname,
                        c.lname,
                        c.birthday,
                        c.address,
                        d.death_date,
                        d.burial_date,
                        p.id AS priest_id,
                        p.name AS priest_name,
                        mother.fname AS mother_fname,
                        mother.mname AS mother_mname,
                        mother.lname AS mother_lname,
                        father.fname AS father_fname,
                        father.mname AS father_mname,
                        father.lname AS father_lname
                    FROM 
                        death d
                    JOIN 
                        client c ON d.client_id = c.id
                    LEFT JOIN 
                        priest p ON d.priest_id = p.id
                    LEFT JOIN 
                        parents mother ON c.mother_id = mother.id
                    LEFT JOIN 
                        parents father ON c.father_id = father.id;
                    ''')
    exisiting_death = cursor.fetchall()

    print('EXISTING DEATH')
    print(exisiting_death)
    
    if exisiting_death:
        return exisiting_death
    else:
        return None

def view_death(death_id):
    connection = get_db_connection()

    if connection is None:
        raise Exception("Could not connect to the database.")

    # Check if name if already exists
    print("This is the death ID: ", {death_id})
    cursor = connection.cursor(dictionary=True)
    cursor.execute('''
                    SELECT 
                        d.id,
                        c.id AS client_id,
                        c.fname, 
                        c.mname,
                        c.lname,
                        c.birthday,
                        c.birthplace,
                        c.ligitivity,
                        c.address,
                        c.status,
                        d.death_date,
                        d.burial_date,
                        d.burial_place,
                        d.cause,
                        d.contact_person,
                        d.cp_address,
                        p.id AS priest_id,
                        p.name AS priest_name,
                        mother.fname AS mother_fname,
                        mother.mname AS mother_mname,
                        mother.lname AS mother_lname,
                        mother.birthday AS mother_birthday,
                        mother.birthplace AS mother_bplace,
                        mother.address AS mother_address,
                        father.fname AS father_fname,
                        father.mname AS father_mname,
                        father.lname AS father_lname,
                        father.birthday AS father_birthday,
                        father.birthplace AS father_bplace,
                        father.address AS father_address,
                        d.rec_index,
                        d.rec_book,
                        d.rec_page,
                        d.rec_line
                    FROM 
                        death d
                    JOIN 
                        client c ON d.client_id = c.id
                    LEFT JOIN 
                        priest p ON d.priest_id = p.id
                    LEFT JOIN 
                        parents mother ON c.mother_id = mother.id
                    LEFT JOIN 
                        parents father ON c.father_id = father.id
                    WHERE d.id = %s;
                    ''', (death_id,))
    additional_death_info = cursor.fetchone()

    print('EXISTING DEATH')
    print(additional_death_info)
    
    if additional_death_info:
        return additional_death_info
    else:
        return None

def insert_death(client_id, death_date, burial_date, cause, burial_place, contact_person, address, priest_id, death_index, death_book, death_page, death_line):
    print(f"Inserting baptism with data: client_id={client_id}, death_date={death_date}, burial_date={burial_date}, cause={cause}, burial_place={burial_place}, contact_person={contact_person}, address={address}, priest_id={priest_id}, rec_index={death_index}, rec_book={death_book}, rec_page={death_page}, rec_line={death_line}")
    
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        INSERT INTO death (client_id, death_date, burial_date, burial_place, cause, contact_person, cp_address, priest_id, rec_index, rec_book, rec_page, rec_line)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (client_id, death_date, burial_date, burial_place, cause, contact_person, address, priest_id, death_index, death_book, death_page, death_line))
    connection.commit()
    cursor.close()
    connection.close()

def update_death_record(death_id, death_date, burial_date, cause, burial_place, contact_person, address, priest_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        UPDATE death
        SET death_date = %s, burial_date = %s, cause = %s, burial_place = %s, contact_person = %s, cp_address = %s, priest_id = %s
        WHERE id = %s
    """, (death_date, burial_date, cause, burial_place, contact_person, address, priest_id, death_id))
    connection.commit()
    cursor.close()
    connection.close()

def delete_death(death_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        DELETE FROM death
        WHERE id = %s
    """, (death_id,))
    connection.commit()
    cursor.close()
    connection.close()
