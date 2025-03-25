from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager


admin_users_blueprint = Blueprint('admin_users', __name__)

@admin_users_blueprint.route('/adminUsers/<int:adminID>', methods=["GET"])
@swag_from({
    'tags': ['Admin Users'],
    'description': 'Get a specific admin user by ID',
    'parameters': [{
        'name': 'adminID',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'Admin user ID'
    }],
    'responses': {
        200: {'description': 'Admin user found'},
        404: {'description': 'Admin user not found'}
    }
})
def get_admin_user(adminID):
    admin_user = query_db("SELECT * FROM adminuser WHERE id = %s", args=(adminID,), one=True)
    if admin_user:
        return jsonify(admin_user), 200
    return jsonify({"error": "Admin user not found"}), 404

@admin_users_blueprint.route('/adminUsers', methods=["POST"])
@swag_from({
    'tags': ['Admin Users'],
    'description': 'Create a new admin user',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'example': 'John Doe'},
                'email': {'type': 'string', 'example': 'john@example.com'},
                'password': {'type': 'string', 'example': 'securepassword'}
            },
            'required': ['name', 'email', 'password']
        }
    }],
    'responses': {
        201: {'description': 'Admin user created'},
        400: {'description': 'Invalid request'}
    }
})
def add_admin_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if not name or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400
    
    #Hashing the password for secure sotrage.
    hashed_password = Bcrypt.generate_password_hash(password).decode('utf-8')


    insert_db("INSERT INTO adminuser (name, email, password) VALUES (%s, %s, %s)", args=(name, email, hashed_password))
    return jsonify({"message": "Admin user created successfully"}), 201

# 🔹 Login Admin (JWT Authentication)
@admin_users_blueprint.route('/adminUsers/login', methods=["POST"])
@swag_from({
    'tags': ['Admin Users'],
    'description': 'Login admin user and get a JWT token',
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'schema': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'example': 'admin@example.com'},
                'password': {'type': 'string', 'example': 'password123'}
            },
            'required': ['email', 'password']
        }
    }],
    'responses': {
        200: {'description': 'Login successful, JWT token returned'},
        401: {'description': 'Invalid credentials'}
    }
})
def admin_login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = query_db("SELECT id, password FROM AdminUser WHERE email = ?", args=(email,), one=True)
    
    if not user or not Bcrypt.check_password_hash(user['password'], password):
        return jsonify({"error": "email or password may be incorrect"}), 401

    # 🔹 Generate JWT token
    access_token = create_access_token(identity={"id": user["id"], "email": email})
    return jsonify(access_token=access_token), 200

@admin_users_blueprint.route('/adminUsers/<int:adminID>', methods=["PUT"])
@swag_from({
    'tags': ['Admin Users'],
    'description': 'Update an existing admin user',
    'parameters': [{
        'name': 'adminID',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'Admin user ID'
    }, {
        'name': 'body',
        'in': 'body',
        'schema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'example': 'Updated Name'},
                'email': {'type': 'string', 'example': 'updated@example.com'},
                'password': {'type': 'string', 'example': 'newpassword'}
            }
        }
    }],
    'responses': {
        200: {'description': 'Admin user updated'},
        400: {'description': 'Invalid request'},
        404: {'description': 'Admin user not found'}
    }
})
def update_admin_user(adminID):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    existing_user = query_db("SELECT id FROM adminuser WHERE id = %s", args=(adminID,), one=True)
    if not existing_user:
        return jsonify({"error": "Admin user not found"}), 404
    
    hashed_password = Bcrypt.generate_password_hash(password).decode('utf-8')

    insert_db("UPDATE adminuser SET name = %s, email = %s, password = %s WHERE id = %s", args=(name, email, hashed_password, adminID))
    return jsonify({"message": "Admin user updated successfully"}), 200

@admin_users_blueprint.route('/adminUsers/<int:adminID>', methods=["DELETE"])
@swag_from({
    'tags': ['Admin Users'],
    'description': 'Delete an admin user',
    'parameters': [{
        'name': 'adminID',
        'in': 'path',
        'type': 'integer',
        'required': True,
        'description': 'Admin user ID'
    }],
    'responses': {
        200: {'description': 'Admin user deleted'},
        404: {'description': 'Admin user not found'}
    }
})
def delete_admin_user(adminID):
    existing_user = query_db("SELECT id FROM adminuser WHERE id = %s", args=(adminID,), one=True)
    if not existing_user:
        return jsonify({"error": "Admin user not found"}), 404

    insert_db("DELETE FROM adminuser WHERE id = %s", args=(adminID,))
    return jsonify({"message": "Admin user deleted successfully"}), 200

