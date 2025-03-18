from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from

menu_items_blueprint = Blueprint('menu_items', __name__)


@menu_items_blueprint.route('/menuItems/<itemID>', methods=["GET"])
@swag_from({
    'tags': ['Menu Items'],
    'responses': {
        200: {
            'description': 'A single menu item',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'integer',
                        'description': 'The ID of the menu item'
                    },
                    'sectionID': {
                        'type': 'integer',
                        'description': 'The ID of the menu section this item belongs to'
                    },
                    'photoLink': {
                        'type': 'string',
                        'description': 'A link to a photo of the menu item'
                    },
                    'description': {
                        'type': 'string',
                        'description': 'A description of the menu item'
                    },
                    'name': {
                        'type': 'string',
                        'description': 'The name of the menu item'
                    },
                    'price': {
                        'type': 'number',
                        'description': 'The price of the menu item'
                    },
                    'type': {
                        'type': 'string',
                        'description': 'The type of the menu item'
                    }
                }
            }
        },
        404: {
            'description': 'Menu item not found'
        }},
    'parameters': [{
        'name': 'itemID',
        'description': 'The ID of the menu item to retrieve',
        'in': 'path',
        'type': 'integer',
        'required': True
            }
        ]})
def get_menu_item(itemID):
    request_data = query_db("SELECT * FROM MenuItem WHERE id = %s", args=(itemID,))
    return jsonify(request_data)


@menu_items_blueprint.route('/menuItems/section/<sectionID>', methods=["GET"])
@swag_from({
    'tags': ['Menu Items'],
    'description': 'Get all menu items in a menu section',
    'parameters': [
        {
            'name': 'sectionID',
            'description': 'The ID of the menu section to retrieve menu items from',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ]
})
def get_menu_items_by_section(sectionID):
    request_data = query_db("SELECT * FROM MenuItem WHERE sectionID = %s",
                            args=(sectionID,))
    return jsonify(request_data)


@menu_items_blueprint.route('/menuItems/add', methods=["POST"])
@swag_from({
    'tags': ['Menu Items'],
    'description': 'Add a new menu item',
    'parameters': [
        {
            'name': 'body',
            'description': 'Menu item object',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'sectionID': {
                        'type': 'integer',
                        'description': 'The ID of the menu section this item belongs to'
                    },
                    'photoLink': {
                        'type': 'string',
                        'description': 'A link to a photo of the menu item'
                    },
                    'description': {
                        'type': 'string',
                        'description': 'A description of the menu item'
                    },
                    'name': {
                        'type': 'string',
                        'description': 'The name of the menu item'
                    },
                    'price': {
                        'type': 'number',
                        'description': 'The price of the menu item'
                    },
                    'type': {
                        'type': 'string',
                        'description': 'The type of the menu item'
                    }
                }
            }
        }
    ],
    })
def add_menu_item():
    data = request.get_json()
    sectionID = data.get("sectionID")
    photoLink = data.get("photoLink")
    description = data.get("description")
    name = data.get("name")
    price = data.get("price")
    type = data.get("type")

    insert_db('INSERT INTO MenuItem (sectionID, photoLink, description, name, price, type) VALUES (%s, %s, %s, %s, %s, %s)', 
              args=(sectionID, photoLink, description, name, price, type))
    return jsonify({"message": "Menu item added successfully"}), 200


@menu_items_blueprint.route('/menuItems/<itemID>/update', methods=["PUT"])
@swag_from({
    'tags': ['Menu Items'],
    'description': 'Update a menu item',
    'parameters': [
        {
            'name': 'body',
            'description': 'Menu item object',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {
                        'type': 'string',
                        'description': 'The name of the menu item'
                    },
                    'price': {
                        'type': 'number',
                        'description': 'The price of the menu item'
                    },
                    'type': {
                        'type': 'string',
                        'description': 'The type of the menu item'
                    },
                    'sectionID': {
                        'type': 'integer',
                        'description': 'The ID of the menu section this item belongs to'
                    }
                }
            }
        }
    ],
    })
def update_menu_item(itemID):
    data = request.get_json()
    name = data.get("name")
    price = data.get("price")
    type = data.get("type")
    sectionID = data.get("sectionID")

    if not name or not price or not type or not sectionID:
        return jsonify({"error": "Name, price, type, and sectionID are required"}), 400

    insert_db("""UPDATE MenuItem SET name = %s, price = %s, type = %s, sectionID = %s WHERE id = %s""", 
               args=(name, price, type, sectionID, itemID))
    return jsonify({"message": "Menu Item updated successfully"}), 200


@menu_items_blueprint.route('/menuItems/<itemID>', methods=["DELETE"])
@swag_from({
    'tags': ['Menu Items'],
    'description': 'Delete a menu item',
    'parameters': [
        {
            'name': 'itemID',
            'description': 'The ID of the menu item to delete',
            'in': 'path',
            'type': 'integer',
            'required': True
        }],
    'responses': {
        200: {
            'description': 'Menu item deleted successfully'
        },
        500: {
            'description': 'An error occurred while deleting the menu item'
        }
    }
})
def delete_menu_item(itemID):
    try:
        insert_db('DELETE FROM MenuItem WHERE id = %s', args=(itemID,))
        return jsonify({"message": "Menu Item deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
