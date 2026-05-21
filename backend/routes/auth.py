from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from extensions import mysql

import bcrypt
import os
import json

auth_bp = Blueprint('auth', __name__)

# Mock users JSON file path
MOCK_USERS_FILE = os.path.join(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    ),
    'mock_users.json'
)


# -------------------------------
# LOAD MOCK USERS
# -------------------------------
def load_mock_users():

    default_users = [
        {
            "Customer_ID": 1,
            "Name": "Sadhik Sarithala",
            "Email": "sadhiksarithala2005@gmail.com",
            "Password": bcrypt.hashpw(
                "password123".encode('utf-8'),
                bcrypt.gensalt()
            ).decode('utf-8'),
            "Phone": "9876543210",
            "Address": "Hyderabad, India"
        }
    ]

    # Create file if not exists
    if not os.path.exists(MOCK_USERS_FILE):

        try:
            with open(MOCK_USERS_FILE, 'w') as f:
                json.dump(default_users, f, indent=4)

            return default_users

        except Exception:
            return default_users

    # Read file
    try:
        with open(MOCK_USERS_FILE, 'r') as f:
            return json.load(f)

    except Exception:
        return default_users


# -------------------------------
# SAVE MOCK USERS
# -------------------------------
def save_mock_users(users):

    try:
        with open(MOCK_USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)

    except Exception:
        pass


# -------------------------------
# REGISTER
# -------------------------------
@auth_bp.route('/register', methods=['POST'])
def register():

    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone', '')
    address = data.get('address', '')

    # Validations
    if not name or not email or not password:

        return jsonify({
            "error": "Name, email and password are required"
        }), 400

    if len(password) < 8:

        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    try:

        cur = mysql.connection.cursor()

        # Check existing email
        cur.execute(
            "SELECT * FROM Customers WHERE Email = %s",
            (email,)
        )

        existing_user = cur.fetchone()

        if existing_user:

            cur.close()

            return jsonify({
                "error": "Email already exists"
            }), 409

        # Hash password
        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )

        # Insert user
        cur.execute("""
            INSERT INTO Customers
            (Name, Email, Password, Phone, Address)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            name,
            email,
            hashed_password.decode('utf-8'),
            phone,
            address
        ))

        mysql.connection.commit()

        customer_id = cur.lastrowid

        cur.close()

        return jsonify({
            "message": "User registered successfully",
            "customer_id": customer_id
        }), 201

    except Exception as e:

        # Mock fallback
        mock_users = load_mock_users()

        existing_user = next(
            (u for u in mock_users if u['Email'] == email),
            None
        )

        if existing_user:

            return jsonify({
                "error": "Email already exists"
            }), 409

        hashed_password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )

        customer_id = len(mock_users) + 1

        new_user = {
            "Customer_ID": customer_id,
            "Name": name,
            "Email": email,
            "Password": hashed_password.decode('utf-8'),
            "Phone": phone,
            "Address": address
        }

        mock_users.append(new_user)

        save_mock_users(mock_users)

        return jsonify({
            "message": "User registered successfully (mock fallback)",
            "customer_id": customer_id,
            "note": "Using mock data"
        }), 201


# -------------------------------
# LOGIN
# -------------------------------
@auth_bp.route('/login', methods=['POST'])
def login():

    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:

        return jsonify({
            "error": "Email and password are required"
        }), 400

    try:

        cur = mysql.connection.cursor()

        cur.execute(
            "SELECT * FROM Customers WHERE Email = %s",
            (email,)
        )

        user = cur.fetchone()

        cur.close()

        if user and bcrypt.checkpw(
            password.encode('utf-8'),
            user['Password'].encode('utf-8')
        ):

            access_token = create_access_token(
                identity=user['Customer_ID']
            )

            user.pop('Password')

            return jsonify({
                "message": "Login successful",
                "token": access_token,
                "user": user
            }), 200

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    except Exception as e:

        # Mock fallback
        mock_users = load_mock_users()

        user = next(
            (u for u in mock_users if u['Email'] == email),
            None
        )

        if user and bcrypt.checkpw(
            password.encode('utf-8'),
            user['Password'].encode('utf-8')
        ):

            access_token = create_access_token(
                identity=user['Customer_ID']
            )

            user_response = user.copy()

            user_response.pop('Password')

            return jsonify({
                "message": "Login successful (mock fallback)",
                "token": access_token,
                "user": user_response,
                "note": "Using mock data"
            }), 200

        return jsonify({
            "error": "Invalid email or password"
        }), 401


# -------------------------------
# PROFILE
# -------------------------------
@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():

    current_user_id = get_jwt_identity()

    try:

        cur = mysql.connection.cursor()

        cur.execute("""
            SELECT
                Customer_ID,
                Name,
                Email,
                Phone,
                Address,
                Created_At
            FROM Customers
            WHERE Customer_ID = %s
        """, (current_user_id,))

        user = cur.fetchone()

        cur.close()

        if user:
            return jsonify(user), 200

        return jsonify({
            "error": "User not found"
        }), 404

    except Exception as e:

        # Mock fallback
        try:
            user_id_int = int(current_user_id)

        except ValueError:
            user_id_int = current_user_id

        mock_users = load_mock_users()

        user = next(
            (u for u in mock_users if u['Customer_ID'] == user_id_int),
            None
        )

        if user:

            user_response = user.copy()

            user_response.pop('Password')

            return jsonify(user_response), 200

        return jsonify({
            "error": "User not found"
        }), 404