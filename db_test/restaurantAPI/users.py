from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from

users_blueprint = Blueprint('users', __name__)


@users_blueprint.route('/users', methods=["GET"])
@swag_from({
    'tags': ['Users'],
    'responses': {
        200: {
            'description': 'All users',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'The ID of the user'
                        },
                        'name': {
                            'type': 'string',
                            'description': 'The name of the user'
                        },
                        'email': {
                            'type': 'string',
                            'description': 'The email of the user'
                        }
                    }
                }
            }
        }
    }
})
def get_users():
    users = query_db("SELECT * FROM user")
    return jsonify(users)


@users_blueprint.route('/users/adduser', methods=["POST"])
@swag_from({
    'tags': ['Users'],
    'responses': {
        200: {
            'description': 'User added successfully'
        },
        400: {
            'description': 'Name and email are required'
        }
    },
    'parameters': [{
        'name': 'body',
        'description': 'User object',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'The name of the user'
                },
                'email': {
                    'type': 'string',
                    'description': 'The email of the user'
                }
            }
        }
    }]
})
def add_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    insert_db('INSERT INTO user (name, email) VALUES (%s, %s)',
              args=(name, email))
    return jsonify({"message": "User added successfully"}), 200


@users_blueprint.route('/users/<user_id>/update', methods=["PUT"])
@swag_from({
    'tags': ['Users'],
    'responses': {
        200: {
            'description': 'User updated successfully'
        },
        400: {
            'description': 'Name and email are required'
        }},
    'parameters': [{
        'name': 'user_id',
        'description': 'The ID of the user to update',
        'type': 'integer',
        'required': True
    },
        {
            'name': 'body',
            'description': 'User object',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'The name of the user'
                    },
                    'email': {
                        'type': 'string',
                        'description': 'The email of the user'
                    }
                }
            }
        }]
})
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    insert_db("""UPDATE user SET name = %s, email = %s WHERE id = %s""",
              args=(name, email, user_id))
    return jsonify({"message": "User updated successfully"}), 200


@users_blueprint.route('/users/<user_id>', methods=["DELETE"])
@swag_from({
    'tags': ['Users'],
    'responses': {
        200: {
            'description': 'User deleted successfully'
        }
    },
    'parameters': [{
        'name': 'user_id',
        'description': 'The ID of the user to delete',
        'type': 'integer',
        'required': True
    }]
})
def delete_user(user_id):
    try:
        insert_db('DELETE FROM user WHERE id = %s', args=(user_id,))
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
