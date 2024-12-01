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
    fido_info: str = None

    def get_id(self):
        return self.user_id


def create_user(firstname: str, middlename: str, lastname: str, username: str) -> User:
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
        INSERT INTO users (fname, mname, lname, username)
        VALUES (%s, %s, %s, %s)
    """, (firstname, middlename, lastname, username))

    connection.commit()

    # Get the newly inserted user
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()

    # Close the cursor and connection
    cursor.close()
    connection.close()

    return User(user_id=user_data['id'], username=user_data['username'], firstname=user_data['fname'],
                middlename=user_data['mname'], lastname=user_data['lname'], fido_info='')


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
                middlename=user_data['mname'], lastname=user_data['lname'], fido_info='')
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
    
    return None
