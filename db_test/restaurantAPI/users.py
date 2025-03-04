from flask import Blueprint, jsonify, request
from database import query_db, insert_db

users_blueprint = Blueprint('users', __name__)

@users_blueprint.route('/users', methods=["GET"])
def get_users():
    users = query_db("SELECT * FROM User")
    return jsonify(users)


@users_blueprint.route('/users/adduser', methods=["POST"])
def add_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    insert_db('INSERT INTO User (name, email) VALUES (?, ?)', args=(name, email))
    return jsonify({"message": "User added successfully"}), 200


@users_blueprint.route('/users/<user_id>/update', methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    insert_db("""UPDATE User SET name = ?, email = ? WHERE id = ?""", args=(name, email, user_id))
    return jsonify({"message": "User updated successfully"}), 200


@users_blueprint.route('/users/<user_id>', methods=["DELETE"])
def delete_user(user_id):
    try:
        query_db('DELETE FROM User WHERE id = ?', args=(user_id,))
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
