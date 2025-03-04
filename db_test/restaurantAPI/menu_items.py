from flask import Blueprint, jsonify, request
from database import query_db, insert_db

menu_items_blueprint = Blueprint('menu_items', __name__)

@menu_items_blueprint.route('/menuItems/<itemID>', methods=["GET"])
def get_menu_item(itemID):
    request_data = query_db("SELECT * FROM MenuItem WHERE id = ?", args=(itemID,))
    return jsonify(request_data)

@menu_items_blueprint.route('/menuItems/add', methods=["POST"])
def add_menu_item():
    data = request.get_json()
    sectionID = data.get("sectionID")
    photoLink = data.get("photoLink")
    description = data.get("description")
    name = data.get("name")
    price = data.get("price")
    type = data.get("type")

    insert_db('INSERT INTO MenuItem (sectionID, photoLink, description, name, price, type) VALUES (?, ?, ?, ?, ?, ?)', 
              args=(sectionID, photoLink, description, name, price, type))
    return jsonify({"message": "Menu item added successfully"}), 200


@menu_items_blueprint.route('/menuItems/<itemID>/update', methods=["PUT"])
def update_menu_item(itemID):
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")
    type = data.get("type")
    sectionID = data.get("sectionID")

    if not name or not price or not type or not sectionID:
        return jsonify({"error": "Name, price, type, and sectionID are required"}), 400

    insert_db("""UPDATE MenuItem SET name = ?, price = ?, type = ?, sectionID = ? WHERE id = ?""", 
               args=(name, price, type, sectionID, itemID))
    return jsonify({"message": "Menu Item updated successfully"}), 200


@menu_items_blueprint.route('/menuItems/<itemID>', methods=["DELETE"])
def delete_menu_item(itemID):
    try:
        query_db('DELETE FROM MenuItem WHERE id = ?', args=(itemID,))
        return jsonify({"message": "Menu Item deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
