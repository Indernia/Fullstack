from flask import Blueprint, jsonify, request
from database import query_db, insert_db

restaurants_blueprint = Blueprint('restaurants', __name__)

@restaurants_blueprint.route('/restaurants/<restaurantID>', methods=["GET"])
def get_restaurant(restaurantID):
    request_data = query_db("SELECT * FROM Restaurant WHERE id = ?", args=(restaurantID,))
    return jsonify(request_data)

@restaurants_blueprint.route('/restaurant/add', methods=["POST"])
def add_restaurant():
    data = request.get_json()
    name = data.get("name")
    chainID = data.get("chainID")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    insert_db('INSERT INTO Restaurant (name, chainID, latitude, longitude) VALUES (?, ?, ?, ?)', 
              args=(name, chainID, latitude, longitude))
    return jsonify({"message": "Restaurant added successfully"}), 200

@restaurants_blueprint.route('/<restaurant_id>/update', methods=["PUT"])
def update_restaurant(restaurant_id):
    data = request.get_json()
    name = data.get("name")
    chain_id = data.get("chainID")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not name or not chain_id or not latitude or not longitude:
        return jsonify({"error": "Missing required fields"}), 400

    insert_db("UPDATE Restaurant SET name = ?, chainID = ?, latitude = ?, longitude = ? WHERE id = ?", 
              args=(name, chain_id, latitude, longitude, restaurant_id))
    return jsonify({"message": "Restaurant updated successfully"}), 200


@restaurants_blueprint.route('/restaurants/<restaurantID>', methods=["DELETE"])
def delete_restaurant(restaurantID):
    try:
        query_db('DELETE FROM Restaurant WHERE id = ?', args=(restaurantID,))
        return jsonify({"message": "Restaurant deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
