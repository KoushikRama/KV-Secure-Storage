from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import hashlib
import os
import binascii
from psycopg2 import sql

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database connection parameters
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'SecurePasswordStorage'
DB_USER = 'postgres'
DB_PASSWORD = '1673'

# Establish database connection
def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn

# Utility function to generate salt and hash password
def generate_salt():
    return os.urandom(16)  # 16 bytes salt

def hash_password(password, salt):
    """Return the hashed password and salt using PBKDF2"""
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)

# Utility function to verify password
def verify_password(stored_hash, password, salt):
    """Verify the password against the stored hash"""
    hashed_password = hash_password(password, salt)
    return stored_hash == hashed_password

# Register endpoint
@app.route('/auth/register/', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Generate salt and hashed password
    salt = generate_salt()
    hashed_password = hash_password(password, salt)

    # Store the username, hashed password, and salt in the database
    conn = get_db_connection()
    cur = conn.cursor()

    # Avoid try-except here, handle any issues directly
    cur.execute(
        sql.SQL("INSERT INTO users (username, password, salt) VALUES (%s, %s, %s)"),
        [username, binascii.hexlify(hashed_password).decode(), binascii.hexlify(salt).decode()]
    )
    conn.commit()
    
    cur.close()
    conn.close()
    
    return jsonify({'message': 'User registered successfully'}), 201

# Login endpoint
@app.route('/auth/login/', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    # Retrieve user from database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT username, password, salt FROM users WHERE username = %s', [username])
    user = cur.fetchone()

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
