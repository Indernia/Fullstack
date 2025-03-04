from flask import Blueprint, jsonify, request
from database import query_db, insert_db

menus_blueprint = Blueprint('menus', __name__)

@menus_blueprint.route('/menus/<menuID>', methods=["GET"])
def get_menu(menuID):
    request_data = query_db("SELECT * FROM Menu WHERE id = ?", args=(menuID,))
    return jsonify(request_data)

@menus_blueprint.route('/menus/add', methods=["POST"])
def add_menu():
    data = request.get_json()
    restaurantID = data.get("restaurantID")
    description = data.get("description")

    insert_db('INSERT INTO Menu (restaurantID, description) VALUES (?, ?)', args=(restaurantID, description))
    return jsonify({"message": "Menu added successfully"}), 200


@menus_blueprint.route('/menus/<menuID>/update', methods=["PUT"])
def update_menu(menuID):
    data = request.get_json()
    description = data.get("description")
    restaurantID = data.get("restaurantID")

    if not description or not restaurantID:
        return jsonify({"error": "Description and restaurantID are required"}), 400

    insert_db("""UPDATE Menu SET description = ?, restaurantID = ? WHERE id = ?""", 
               args=(description, restaurantID, menuID))
    return jsonify({"message": "Menu updated successfully"}), 200


@menus_blueprint.route('/menus/<menuID>', methods=["DELETE"])
def delete_menu(menuID):
    try:
        query_db('DELETE FROM Menu WHERE id = ?', args=(menuID,))
        return jsonify({"message": "Menu deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
