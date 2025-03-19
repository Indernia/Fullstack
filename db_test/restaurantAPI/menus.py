from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from

menus_blueprint = Blueprint('menus', __name__)


@menus_blueprint.route('/menus/<menuID>', methods=["GET"])
@swag_from({
    'tags': ['Menus'],
    'responses': {
        200: {
            'description': 'A single menu',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer',
                        'description': 'The ID of the menu'
                    },
                    'restaurantID': {
                        'type': 'integer',
                        'description': 'The ID of the restaurant this menu belongs to'
                    },
                    'description': {
                        'type': 'string',
                        'description': 'A description of the menu'
                    }
                }
            }
        },
        404: {
            'description': 'Menu not found'
        }},
    'parameters': [{
        'name': 'menuID',
        'description': 'The ID of the menu to retrieve',
        'in': 'path',
        'type': 'integer',
        'required': True
            }
        ]})
def get_menu(menuID):
    request_data = query_db("SELECT * FROM menu WHERE id = %s", args=(menuID,))
    return jsonify(request_data)

@menus_blueprint.route('/menus/restaurant/<restaurantID>', methods=["GET"])
@swag_from({
    'tags': ['Menus'],
    'description': 'Get all menus for a specific restaurant',
    'parameters': [
        {
            'name': 'restaurantID',
            'description': 'The ID of the restaurant to retrieve menus from',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {
            'description': 'A list of menus for the restaurant',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer', 'description': 'The ID of the menu'},
                        'restaurantID': {'type': 'integer', 'description': 'The restaurant this menu belongs to'},
                        'description': {'type': 'string', 'description': 'A description of the menu'}
                    }
                }
            }
        },
        404: {
            'description': 'No menus found for this restaurant'
        }
    }
})
def get_menus_by_restaurant(restaurantID):
    request_data = query_db("SELECT * FROM menu WHERE restaurantID = %s", args=(restaurantID,))
    
    if not request_data:
        return jsonify({"error": "No menus found for this restaurant"}), 404
    
    return jsonify(request_data)

@menus_blueprint.route('/menus/add', methods=["POST"])
@swag_from({
    'tags': ['Menus'],
    'responses': {
        200: {
            'description': 'Menu added successfully'
        },
        400: {
            'description': 'Description and restaurantID are required'
        }},
    'parameters': [{
        'name': 'body',
        'description': 'Menu object',
        'in': 'body',
        'schema': {
            'type': 'object',
            'properties': {
                'restaurantID': {
                    'type': 'integer',
                    'description': 'The ID of the restaurant this menu belongs to'
                },
                'description': {
                    'type': 'string',
                    'description': 'A description of the menu'
                }
            }
        }
            }
        ]})
def add_menu():
    data = request.get_json()
    restaurantID = data.get("restaurantID")
    description = data.get("description")

    insert_db('INSERT INTO menu (restaurantID, description) VALUES (%s, %s)', args=(restaurantID, description))
    return jsonify({"message": "Menu added successfully"}), 200


@menus_blueprint.route('/menus/<menuID>/update', methods=["PUT"])
@swag_from({
    'tags': ['Menus'],
    'responses': {
        200: {
            'description': 'Menu updated successfully'
        },
        400: {
            'description': 'Description and restaurantID are required'
        }},
    'parameters': [{
        'name': 'menuID',
        'description': 'The ID of the menu to update',
        'in': 'path',
        'type': 'integer',
        'required': True
            },
        {
        'name': 'body',
        'description': 'Menu object',
        'in': 'body',
        'schema': {
            'type': 'object',
            'properties': {
                'restaurantID': {
                    'type': 'integer',
                    'description': 'The ID of the restaurant this menu belongs to'
                },
                'description': {
                    'type': 'string',
                    'description': 'A description of the menu'
                }
            }
        }
            }
        ]})
def update_menu(menuID):
    data = request.get_json()
    description = data.get("description")
    restaurantID = data.get("restaurantID")

    if not description or not restaurantID:
        return jsonify({"error": "Description and restaurantID are required"}), 400

    insert_db("UPDATE menu SET description = %s, restaurantID = %s WHERE id = %s",
              args=(description, restaurantID, menuID))
    return jsonify({"message": "Menu updated successfully"}), 200


@menus_blueprint.route('/menus/<menuID>', methods=["DELETE"])
@swag_from({
    'tags': ['Menus'],
    'responses': {
        200: {
            'description': 'Menu deleted successfully'
        }},
    'parameters': [{
        'name': 'menuID',
        'description': 'The ID of the menu to delete',
        'in': 'path',
        'type': 'integer',
        'required': True
            }
        ]})
def delete_menu(menuID):
    try:
        insert_db('DELETE FROM menu WHERE id = %s', args=(menuID,))
        return jsonify({"message": "Menu deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
