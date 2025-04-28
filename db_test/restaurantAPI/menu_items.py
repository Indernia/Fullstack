from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from
from flask_jwt_extended import jwt_required
from azure.storage.blob import BlobServiceClient
from urllib.parse import urlparse
import os

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
                    },
                    'tags': {
                        'type': 'object',
                        'description': 'A list of tags for the given item'
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
    request_data = query_db("""SELECT mi.*,
                            json_agg(t) AS tags
                            FROM
                            menuitem mi
                            LEFT JOIN menuitemhastag mit on mi.id = mit.menuitemid
                            LEFT JOIN tag t ON mit.tagid = t.id
                            WHERE mi.id = %s
                            GROUP BY mi.id
                            """
                            , args=(itemID,))
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
    request_data = query_db("SELECT * FROM menuitem WHERE sectionID = %s AND isDeleted = False",
                            args=(sectionID,))
    return jsonify(request_data)


@menu_items_blueprint.route('/menuItems/add', methods=["POST"])
@jwt_required()
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
    photoLink = "https://jamnawmenu.blob.core.windows.net/menu-items/pexels-chanwalrus-958545.jpg"
    description = data.get("description")
    name = data.get("name")
    price = data.get("price")
    type = data.get("type")

    insert_db('INSERT INTO menuitem (sectionID, photoLink, description, name, price, type) VALUES (%s, %s, %s, %s, %s, %s)', 
              args=(sectionID, photoLink, description, name, price, type))
    return jsonify({"message": "Menu item added successfully"}), 200


@menu_items_blueprint.route('/menuItems/<itemID>/update', methods=["PUT"])
@jwt_required()
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

    insert_db("""UPDATE menuitem SET name = %s, price = %s, type = %s, sectionID = %s WHERE id = %s""", 
               args=(name, price, type, sectionID, itemID))
    return jsonify({"message": "Menu Item updated successfully"}), 200


@menu_items_blueprint.route('/menuItems/<itemID>', methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['Menu Items'],
    'summary': 'Delete a menu item and its associated image from Blob Storage',
    'description': 'This endpoint deletes a menu item and its associated image from Azure Blob Storage.',
    'parameters': [
        {
            'name': 'itemID',
            'in': 'path',
            'description': 'The ID of the menu item to delete',
            'required': True,
            'type': 'integer'
        }
    ],
    'responses': {
        '200': {
            'description': 'Menu item and blob deleted successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Menu Item deleted successfully and blob storage'
                    }
                }
            }
        },
        '500': {
            'description': 'An error occurred while deleting the menu item or blob',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Error message'
                    }
                }
            }
        }
    }
})
def delete_menu_item(itemID):
    try:
        insert_db('UPDATE menuitem SET isDeleted = True WHERE id = %s', args=(itemID,))

        menu_item = query_db('SELECT photoLink FROM menuitem WHERE id = %s', args=(itemID,), one=True)
        if menu_item and menu_item['photoLink']:
            photo_link = menu_item['photoLink']     

            # 3. Parse the blob name from the full URL
            parsed_url = urlparse(photo_link)
            blob_name = parsed_url.path.split('menu-items/', 1)[-1]

            container_name = "menu-items"
            account_name = os.getenv("AZURE_STORAGE_ACCOUNT")
            account_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")

            # 4. Connect to Azure Blob Storage
            blob_service_client = BlobServiceClient(
                account_url=f"https://{account_name}.blob.core.windows.net",
                credential=account_key
            )

            blob_client = blob_service_client.get_blob_client(
            container=container_name,
            blob=blob_name
            )

            # Delete the blob
            blob_client.delete_blob()

        return jsonify({"message": "Menu Item deleted successfully and blob storage"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
