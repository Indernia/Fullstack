from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from
from flask_jwt_extended import jwt_required
import secrets
from extensions import bcrypt


api_keys_blueprint = Blueprint('api_keys', __name__)


def generate_api_key():
    return secrets.token_urlsafe(32)


@api_keys_blueprint.route('/apiKeys/create', methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['API Keys'],
    'responses': {
        201: {
            'description': 'API key created successfully',
            'examples': {
                'application/json': {
                    "message": "generated_api_key"
                }
            }
        },
        400: {
            'description': 'Missing required fields'
        }
    }
})
def add_api_key():
    data = request.get_json()
    restaurantID = data.get("restaurantID")
    apikey = generate_api_key()

    hashed_key = bcrypt.generate_password_hash(apikey).decode('utf-8')

    if not restaurantID:
        return jsonify({"error": "Missing required fields"}), 400

    insert_db("INSERT INTO apikeys (apikey, restaurantID) VALUES (%s, %s)", args=(hashed_key, restaurantID))
    return jsonify({"message": apikey}), 201


def validate_api_key(apikey, restaurantID):
    keys = query_db("SELECT * FROM apikeys WHERE restaurantID = %s", args=(restaurantID,))
    for key in keys:
        if bcrypt.check_password_hash(key['apikey'], apikey):
            return True
    return False
