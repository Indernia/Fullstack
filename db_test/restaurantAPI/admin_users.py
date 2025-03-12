from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from

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
    admin_user = query_db("SELECT * FROM AdminUser WHERE id = ?", args=(adminID,), one=True)
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

    insert_db("INSERT INTO AdminUser (name, email, password) VALUES (?, ?, ?)", args=(name, email, password))
    return jsonify({"message": "Admin user created successfully"}), 201

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

    existing_user = query_db("SELECT id FROM AdminUser WHERE id = ?", args=(adminID,), one=True)
    if not existing_user:
        return jsonify({"error": "Admin user not found"}), 404

    insert_db("UPDATE AdminUser SET name = ?, email = ?, password = ? WHERE id = ?", args=(name, email, password, adminID))
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
    existing_user = query_db("SELECT id FROM AdminUser WHERE id = ?", args=(adminID,), one=True)
    if not existing_user:
        return jsonify({"error": "Admin user not found"}), 404

    insert_db("DELETE FROM AdminUser WHERE id = ?", args=(adminID,))
    return jsonify({"message": "Admin user deleted successfully"}), 200