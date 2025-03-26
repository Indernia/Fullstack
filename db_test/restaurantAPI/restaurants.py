from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager


restaurants_blueprint = Blueprint('restaurants', __name__)


@restaurants_blueprint.route('/restaurants/<restaurantID>', methods=["GET"])
@swag_from({
    'tags': ['Restaurants'],
    'responses': {
        200: {
            'description': 'A single restaurant',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer',
                        'description': 'The ID of the restaurant'
                    },
                    'name': {
                        'type': 'string',
                        'description': 'The name of the restaurant'
                    },
                    'chainID': {
                        'type': 'integer',
                        'description': 'The ID of the chain this restaurant belongs to'
                    },
                    'latitude': {
                        'type': 'number',
                        'description': 'The latitude of the restaurant'
                    },
                    'longitude': {
                        'type': 'number',
                        'description': 'The longitude of the restaurant'
                    }
                }
            }
        },
        404: {
            'description': 'Restaurant not found'
        }},
    'parameters': [{
        'name': 'restaurantID',
        'description': 'The ID of the restaurant to retrieve',
        'in': 'path',
        'type': 'integer',
        'required': True
            }
        ]})
def get_restaurant(restaurantID):
    request_data = query_db("SELECT * FROM restaurant WHERE id = %s", args=(restaurantID,))
    return jsonify(request_data)

@restaurants_blueprint.route('/restaurants', methods=["GET"])
@swag_from({
    'tags': ['Restaurants'],
    'responses': {
        200: {
            'description': 'A list of all restaurants',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'The ID of the restaurant'
                        },
                        'name': {
                            'type': 'string',
                            'description': 'The name of the restaurant'
                        },
                        'chainID': {
                            'type': 'integer',
                            'description': 'The ID of the chain this restaurant belongs to'
                        },
                        'latitude': {
                            'type': 'number',
                            'description': 'The latitude of the restaurant'
                        },
                        'longitude': {
                            'type': 'number',
                            'description': 'The longitude of the restaurant'
                        }
                    }
                }
            }
        },
        500: {
            'description': 'Internal Server Error'
        }
    }
})
def get_all_restaurants():
    try:
        restaurants = query_db("SELECT * FROM restaurant")
        return jsonify(restaurants), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@restaurants_blueprint.route('/restaurant/add', methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Restaurants'],
    'responses': {
        200: {
            'description': 'Restaurant added successfully'
        },
        400: {
            'description': 'Name, chainID, latitude, and longitude are required'
        }},
    'parameters': [{
        'name': 'body',
        'description': 'Restaurant object',
        'in': 'body',
        'schema': {
            'properties': {
                'name': {
                    'type': 'string',
                    'description': 'The name of the restaurant'
                },
                'chainID': {
                    'type': 'integer',
                    'description': 'The ID of the chain this restaurant belongs to'
                },
                'latitude': {
                    'type': 'number',
                    'description': 'The latitude of the restaurant'
                },
                'longitude': {
                    'type': 'number',
                    'description': 'The longitude of the restaurant'
                }
            }
        }
    }]})
def add_restaurant():
    data = request.get_json()
    name = data.get("name")
    chainID = data.get("chainID")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    insert_db('INSERT INTO restaurant (name, chainID, latitude, longitude) VALUES (%s, %s, %s, %s)',
              args=(name, chainID, latitude, longitude))
    return jsonify({"message": "Restaurant added successfully"}), 200


@restaurants_blueprint.route('/<restaurant_id>/update', methods=["PUT"])
@swag_from({
    'tags': ['Restaurants'],
    'responses': {
        200: {
            'description': 'Restaurant updated successfully'
        },
        400: {
            'description': 'Name, chainID, latitude, and longitude are required'
        }},
    'parameters': [{
        'name': 'restaurant_id',
        'description': 'The ID of the restaurant to update',
        'type': 'integer',
        'required': True
    }]})
def update_restaurant(restaurant_id):
    data = request.get_json()
    name = data.get("name")
    chain_id = data.get("chainID")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not name or not chain_id or not latitude or not longitude:
        return jsonify({"error": "Missing required fields"}), 400

    insert_db("UPDATE restaurant SET name = %s, chainID = %s, latitude = %s, longitude = %s WHERE id = %s", 
              args=(name, chain_id, latitude, longitude, restaurant_id))
    return jsonify({"message": "Restaurant updated successfully"}), 200


@restaurants_blueprint.route('/restaurants/<restaurantID>', methods=["DELETE"])
@swag_from({
    'tags': ['Restaurants'],
    'responses': {
        200: {
            'description': 'Restaurant deleted successfully'
        },
        500: {
            'description': 'An error occurred while deleting the restaurant'
        }},
    'parameters': [{
        'name': 'restaurantID',
        'description': 'The ID of the restaurant to delete',
        'type': 'integer',
        'required': True
    }]
})
def delete_restaurant(restaurantID):
    try:
        insert_db('DELETE FROM restaurant WHERE id = %s', args=(restaurantID,))
        return jsonify({"message": "Restaurant deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
