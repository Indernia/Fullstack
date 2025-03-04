from flask import Blueprint, jsonify, request
from database import query_db, insert_db

menu_sections_blueprint = Blueprint('menu_sections', __name__)

@menu_sections_blueprint.route('/menuSections/<sectionID>', methods=["GET"])
def get_menu_section(sectionID):
    request_data = query_db("SELECT * FROM MenuSection WHERE id = ?", args=(sectionID,))
    return jsonify(request_data)

@menu_sections_blueprint.route('/menuSections/add', methods=["POST"])
def add_menu_section():
    data = request.get_json()
    menuID = data.get("menuID")
    name = data.get("name")

    insert_db('INSERT INTO MenuSection (menuID, name) VALUES (?, ?)', args=(menuID, name))
    return jsonify({"message": "Menu section added successfully"}), 200


@menu_sections_blueprint.route('/menuSections/<sectionID>/update', methods=["PUT"])
def update_menu_section(sectionID):
    data = request.get_json()
    name = data.get("name")
    menuID = data.get("menuID")

    if not name or not menuID:
        return jsonify({"error": "Name and menuID are required"}), 400

    insert_db("""UPDATE MenuSection SET name = ?, menuID = ? WHERE id = ?""", 
               args=(name, menuID, sectionID))
    return jsonify({"message": "Menu Section updated successfully"}), 200


@menu_sections_blueprint.route('/menuSections/<sectionID>', methods=["DELETE"])
def delete_menu_section(sectionID):
    try:
        query_db('DELETE FROM MenuSection WHERE id = ?', args=(sectionID,))
        return jsonify({"message": "Menu Section deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
