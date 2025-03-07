from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from

menu_sections_blueprint = Blueprint('menu_sections', __name__)


@menu_sections_blueprint.route('/menuSections/<sectionID>', methods=["GET"])
@swag_from({
    'tags': ['Menu Sections'],
    'responses': {
        200: {
            'description': 'A single menu section',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer',
                        'description': 'The ID of the menu section'
                    },
                    'menuID': {
                        'type': 'integer',
                        'description': 'The ID of the menu this section belongs to'
                    },
                    'name': {
                        'type': 'string',
                        'description': 'The name of the menu section'
                    }
                }
            }
        },
        404: {
            'description': 'Menu section not found'
        }},
    'parameters': [{
        'name': 'sectionID',
        'description': 'The ID of the menu section to retrieve',
        'in': 'path',
        'type': 'integer',
        'required': True
            }
        ]})
def get_menu_section(sectionID):
    request_data = query_db("SELECT * FROM MenuSection WHERE id = ?", args=(sectionID,))
    return jsonify(request_data)


@menu_sections_blueprint.route('/menuSections/add', methods=["POST"])
@swag_from({
    'tags': ['Menu Sections'],
    'responses': {
        200: {
            'description': 'Menu section added successfully'
        },
        400: {
            'description': 'Name and menuID are required'
        }},
    'parameters': [{
        'name': 'body',
        'description': 'Menu section object',
        'in': 'body',
        'required': True,
        'schema': {
            'properties': {
                'menuID': {
                    'type': 'integer',
                    'description': 'The ID of the menu this section belongs to'
                },
                'name': {
                    'type': 'string',
                    'description': 'The name of the menu section'
                }
            }
        }
    }]
})
def add_menu_section():
    data = request.get_json()
    menuID = data.get("menuID")
    name = data.get("name")

    insert_db('INSERT INTO MenuSection (menuID, name) VALUES (?, ?)', args=(menuID, name))
    return jsonify({"message": "Menu section added successfully"}), 200


@menu_sections_blueprint.route('/menuSections/<sectionID>/update', methods=["PUT"])
@swag_from({
    'tags': ['Menu Sections'],
    'responses': {
        200: {
            'description': 'Menu section updated successfully'
        },
        400: {
            'description': 'Name and menuID are required'
        }},
    'parameters': [{
        'name': 'sectionID',
        'description': 'The ID of the menu section to update',
        'in': 'path',
        'type': 'integer',
        'required': True
    }, {
        'name': 'body',
        'description': 'Menu section object',
        'in': 'body',
        'required': True,
        'schema': {
            'properties': {
                'menuID': {
                    'type': 'integer',
                    'description': 'The ID of the menu this section belongs to'
                },
                'name': {
                    'type': 'string',
                    'description': 'The name of the menu section'
                }
            }
        }
    }]
})
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
@swag_from({
    'tags': ['Menu Sections'],
    'responses': {
        200: {
            'description': 'Menu section deleted successfully'
        }},
    'parameters': [{
        'name': 'sectionID',
        'description': 'The ID of the menu section to delete',
        'in': 'path',
        'type': 'integer',
        'required': True
    }]
})
def delete_menu_section(sectionID):
    try:
        query_db('DELETE FROM MenuSection WHERE id = ?', args=(sectionID,))
        return jsonify({"message": "Menu Section deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
