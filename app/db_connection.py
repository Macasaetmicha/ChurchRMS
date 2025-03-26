import mysql.connector
from mysql.connector import Error
from config.config import Config

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        if connection.is_connected():
            print("Database connection successful.")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None
