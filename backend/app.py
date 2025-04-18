from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import hashlib
import os
import binascii
from psycopg2 import sql

app = Flask(__name__)
CORS(app)  # We need CORS to connect 2 different domains localhost:8000( backend ) with localhost:3000 (frontend)

# Database connections Variables
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'SecurePasswordStorage'
DB_USER = 'postgres'
DB_PASSWORD = '1673'

# Establishing the database connection
def get_db_connection():
    conn = psycopg2.connect(  # We use psycopg2 to connect to postgres database
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Generating random salt
def generate_salt():
    return os.urandom(16)  # 16 bytes salt  In Python, urandom is a function provided by the os module that generates random bytes suitable for cryptographic use.
    # It reads from the operating system's source of randomness, which is typically more secure and unpredictable than other random number generators.

def hash_password(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)

def verify_password(stored_hash, password, salt):
    hashed_password = hash_password(password, salt)
    return stored_hash == hashed_password

# Register Request endpoint
@app.route('/auth/register/', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Generating the salt and hashing the password
    salt = generate_salt()
    hashed_password = hash_password(password, salt)

    conn = get_db_connection()
    cur = conn.cursor()
    '''A cursor allows you to execute SQL commands and queries, and fetch data from the database.

        Creating a Connection: First, you need to establish a connection to the database.
        Creating a Cursor: Once you have a connection, you create a cursor object using the connection.'''

    # we'll be stroring the username, hashed password, and salt in the database
    cur.execute(
        sql.SQL("INSERT INTO users (username, password, salt) VALUES (%s, %s, %s)"),
        [username, binascii.hexlify(hashed_password).decode(), binascii.hexlify(salt).decode()]
    )
    conn.commit()
    
    cur.close()
    conn.close()
    
    return jsonify({'message': 'User registered successfully'}), 201

# Login Request endpoint
@app.route('/auth/login/', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Retrieving user data from database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT username, password, salt FROM users WHERE username = %s', [username]) #The password stored is hashed passwword
    user = cur.fetchone() #This method retrieves the next row of a query result set, returning a single sequence, or None if no more rows are available.

    if user is None:
        return jsonify({'error': 'Invalid username or password'}), 400

    stored_hash = binascii.unhexlify(user[1])  # Stored password hash
    salt = binascii.unhexlify(user[2])  # Stored salt

    # Verify password
    if verify_password(stored_hash, password, salt):
        cur.close()
        conn.close()
        return jsonify({'message': 'Login successful'}), 200
    else:
        cur.close()
        conn.close()
        return jsonify({'error': 'Invalid username or password'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=8000)
