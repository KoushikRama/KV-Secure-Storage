from flask import Flask, request, jsonify , session
from flask_cors import CORS
import psycopg2
import hashlib
import hmac
import struct
import os
import binascii
from psycopg2 import sql

"""

pbkdf2_hmac_sha256() is a PBKDF2 implementation using HMAC-SHA256
as the pseudorandom function.

Arguments:
1) password: The input password (as bytes)
2) salt: The salt value (as bytes)
3) iterations: Number of iterations 


"""
def pbkdf2_hmac_sha256(password: bytes, salt: bytes, iterations: int) -> bytes:
    
    # Precompute the HMAC key if password is longer than block size
    if len(password) > hashlib.sha256().block_size:
        password = hashlib.sha256(password).digest()
    
    # Pad the password if needed
    password = password + b'\x00' * (hashlib.sha256().block_size - len(password))
    
    # Inner and outer padded keys for HMAC
    iKP = bytes(x ^ 0x36 for x in password)
    oKP = bytes(x ^ 0x5c for x in password)
    
    # Single block needed for 32-byte output, since SHA-256 produces 32-byte (256-bit) hashes
    block_number = 1
    msg = salt + struct.pack('>I', block_number)
    
    # Initial iteration
    U = hmac.new(iKP, msg, hashlib.sha256).digest()
    U = hmac.new(oKP, U, hashlib.sha256).digest()
    result = U
    
    # Subsequent iterations
    for _ in range(1, iterations):
        U = hmac.new(iKP, U, hashlib.sha256).digest()
        U = hmac.new(oKP, U, hashlib.sha256).digest()
        result = bytes(x ^ y for x, y in zip(result, U))
    
    return result[:32]  # Explicitly return first 32 bytes

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
    return pbkdf2_hmac_sha256(password.encode('utf-8'), salt, 100000)

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
    salt = generate_salt()
    hashed_password = hash_password(password, salt)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        sql.SQL("INSERT INTO users (username, password, salt, user_type) VALUES (%s, %s, %s, 'user')"),
        [username, binascii.hexlify(hashed_password).decode(), binascii.hexlify(salt).decode()]
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/auth/login/', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, password, salt, user_type FROM users WHERE username = %s', [username])
    user = cur.fetchone()
    if user is None:
        return jsonify({'error': 'Invalid username or password'}), 400
    stored_hash = binascii.unhexlify(user[2])
    salt = binascii.unhexlify(user[3])
    if verify_password(stored_hash, password, salt):
        cur.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = %s", [user[0]])
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'message': 'Login successful', 'username': username, 'user_type': user[4]}), 200
    else:
        cur.close()
        conn.close()
        return jsonify({'error': 'Invalid username or password'}), 400
    
@app.route('/user/type', methods=['GET'])
def get_user_type():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username is required'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_type FROM users WHERE username = %s", [username])
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:
        return jsonify({'user_type': result[0]})
    else:
        return jsonify({'error': 'User not found'}), 404
    
@app.route('/user/apps', methods=['GET'])
def get_user_apps():
    username = request.args.get('username')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT app_name, app_username, app_password, created_at 
        FROM app_passwords 
        WHERE user_id = (SELECT id FROM users WHERE username = %s)
    """, [username])
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'app_name': r[0], 'app_username': r[1], 'app_password': r[2], 'created_at': r[3]} for r in rows])

@app.route('/admin/users', methods=['GET'])
def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, created_at, last_login FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify([{'username': r[0], 'created_at': r[1], 'last_login': r[2]} for r in rows])

@app.route('/user/apps', methods=['POST'])
def add_user_app():
    data = request.get_json()
    username = data.get('username')
    app_name = data.get('app_name')
    app_password = data.get('app_password')
    app_username = data.get('app_username')

    if not (username and app_name and app_password and app_username):
        return jsonify({'error': 'All fields are required'}), 400

    salt = generate_salt()
    hashed_app_password = binascii.hexlify(hash_password(app_password, salt)).decode()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO app_passwords (user_id, app_name, app_password, app_username) VALUES ((SELECT id FROM users WHERE username = %s), %s, %s, %s)",
        [username, app_name, hashed_app_password, app_username]
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'App added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True, port=8000)
