from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager
import math


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
            'description': 'Name, latitude, and longitude are required'
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
    ownerID = get_jwt_identity()["id"]
    data = request.get_json()
    name = data.get("name")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    insert_db('INSERT INTO restaurant (name, latitude, longitude, ownerID) VALUES (%s, %s, %s, %s)',
              args=(name, latitude, longitude, ownerID))
    return jsonify({"message": "Restaurant added successfully"}), 200


@restaurants_blueprint.route('/<restaurant_id>/update', methods=["PUT"])
@jwt_required() 
@swag_from({
    'tags': ['Restaurants'],
    'responses': {
        200: {
            'description': 'Restaurant updated successfully'
        },
        400: {
            'description': 'Name, latitude, and longitude are required'
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
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not name or not latitude or not longitude:
        return jsonify({"error": "Missing required fields"}), 400

    insert_db("UPDATE restaurant SET name = %s, latitude = %s, longitude = %s WHERE id = %s", 
              args=(name, latitude, longitude, restaurant_id))
    return jsonify({"message": "Restaurant updated successfully"}), 200


@restaurants_blueprint.route('/restaurants/<restaurantID>', methods=["DELETE"])
@jwt_required()
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


@restaurants_blueprint.route('/restaurants/closest/', methods=["GET"])
@swag_from({
    'tags': ['Restaurants'],
    'responses': {
        200: {
            'description': 'A list of the 10 closest restaurants to the given latitude and longitude',
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
        400: {
            'description': 'Latitude and longitude are required'
        }},
    'parameters': [{
        'name': 'lat',
        'description': 'The latitude of the location to search from',
        'in': 'query',
        'type': 'number',
        'required': True
    }, {
        'name': 'lon',
        'description': 'The longitude of the location to search from',
        'in': 'query',
        'type': 'number',
        'required': True
    }, {
        'name': 'radius_km',
        'description': 'The radius in kilometers to search within',
        'in': 'query',
        'type': 'number',
        'required': False
    }]
})
def get_closest_10_restaurants():
    lat = float(request.args.get('lat'))
    lon = float(request.args.get('lon'))
    radius_km = float(request.args.get('radius_km', 10))
    min_lat, max_lat, min_lon, max_lon = get_bounding_box(lat, lon, radius_km)

    restaurants = query_db("SELECT * FROM restaurant WHERE latitude BETWEEN %s AND %s AND longitude BETWEEN %s AND %s",
                           args=(min_lat, max_lat, min_lon, max_lon))
    restaurants = sorted(restaurants, key=lambda x: haversine(lat, lon, x['latitude'], x['longitude']))
    return jsonify(restaurants[:10])



def get_bounding_box(lat, lon, radius_km):
    # Approximate radius of Earth in km
    R = 6371.0

    # Convert latitude and longitude from degrees to radians
    lat_rad = math.radians(lat)

    # Latitude bounds (1 deg ~ 111 km)
    delta_lat = radius_km / 111.0

    # Longitude bounds (1 deg ~ varies with latitude)
    delta_lon = radius_km / (111.320 * math.cos(lat_rad))

    min_lat = lat - delta_lat
    max_lat = lat + delta_lat
    min_lon = lon - delta_lon
    max_lon = lon + delta_lon

    return min_lat, max_lat, min_lon, max_lon


def haversine(lat1, lon1, lat2, lon2):
    """
    taken from the following source: https://www.geeksforgeeks.org/haversine-formula-to-find-distance-between-two-points-on-a-sphere/
    """
    # distance between latitudes
    # and longitudes
    dLat = (lat2 - lat1) * math.pi / 180.0
    dLon = (lon2 - lon1) * math.pi / 180.0
 
    # convert to radians
    lat1 = (lat1) * math.pi / 180.0
    lat2 = (lat2) * math.pi / 180.0
 
    # apply formulae
    a = (pow(math.sin(dLat / 2), 2) +
         pow(math.sin(dLon / 2), 2) *
         math.cos(lat1) * math.cos(lat2))
    rad = 6371
    c = 2 * math.asin(math.sqrt(a))
    return rad * c


@restaurants_blueprint.route('/restaurants/theme/<themename>', methods=["GET"])
@swag_from({
        'description': "an endpoint for getting a specific theme",
        'tag': ['Restaurants']
    })
def get_restaurant_theme(themename):
    theme = query_db("SELECT * FROM themes WHERE name = %s", args=(themename,), one=True)
    print(theme)
    return jsonify(theme)


@restaurants_blueprint.route('/restaurants/themes', methods=["GET"])
@swag_from({
        'description': "an endpoint for getting all themes",
        'tag': ['Restaurants']
    })
def get_all_restaurant_themes():
    names = query_db("SELECT name FROM themes")
    return jsonify(names)








