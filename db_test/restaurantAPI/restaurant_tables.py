from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from flasgger import swag_from
from database import query_db, insert_db

restaurant_tables_blueprint = Blueprint('restaurant_tables', __name__)

@restaurant_tables_blueprint.route('/restaurantTables/<tableID>', methods=["GET"])
@swag_from({
    'tags': ['Restaurant Tables'],
    'description': 'Get a single restaurant table by ID',
    'parameters': [
        {
            'name': 'tableID',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the table to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'A single table',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'restaurantID': {'type': 'integer'},
                    'tableNumber': {'type': 'integer'},
                    'name': {'type': 'string'}
                }
            }
        },
        404: {'description': 'Table not found'}
    }
})
def get_table(tableID):
    table = query_db('SELECT * FROM RestaurantTable WHERE id = %s AND isDeleted = False', args=(tableID,), one=True)
    if not table:
        return jsonify({"error": "Table not found"}), 404
    return jsonify(table), 200


@restaurant_tables_blueprint.route('/restaurantTables/restaurant/<restaurantID>', methods=["GET"])
@swag_from({
    'tags': ['Restaurant Tables'],
    'description': 'Get all tables for a restaurant',
    'parameters': [
        {
            'name': 'restaurantID',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the restaurant'
        }
    ],
    'responses': {
        200: {
            'description': 'List of tables',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'restaurantID': {'type': 'integer'},
                        'tableNumber': {'type': 'integer'},
                        'name': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_tables_by_restaurant(restaurantID):
    tables = query_db('SELECT * FROM RestaurantTable WHERE restaurantID = %s AND isDeleted = False', args=(restaurantID,))
    return jsonify(tables), 200


@restaurant_tables_blueprint.route('/restaurantTables/add', methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Restaurant Tables'],
    'description': 'Add a new restaurant table',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'restaurantID': {'type': 'integer'},
                    'tableNumber': {'type': 'integer'},
                    'name': {'type': 'string'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Table added successfully'}
    }
})
def add_table():
    data = request.get_json()
    restaurantID = data.get('restaurantID')
    tableNumber = data.get('tableNumber')
    name = data.get('name')

    insert_db('INSERT INTO RestaurantTable (restaurantID, tableNumber, name) VALUES (%s, %s, %s)', 
              args=(restaurantID, tableNumber, name))
    return jsonify({"message": "Table added successfully"}), 200


@restaurant_tables_blueprint.route('/restaurantTables/<tableID>/update', methods=["PUT"])
@jwt_required()
@swag_from({
    'tags': ['Restaurant Tables'],
    'description': 'Update a restaurant table',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'tableNumber': {'type': 'integer'},
                    'name': {'type': 'string'},
                    'restaurantID': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {'description': 'Table updated successfully'},
        400: {'description': 'Missing required fields'}
    }
})
def update_table(tableID):
    data = request.get_json()
    tableNumber = data.get('tableNumber')
    name = data.get('name')
    restaurantID = data.get('restaurantID')

    if not tableNumber or not restaurantID:
        return jsonify({"error": "restaurantID and tableNumber are required"}), 400

    insert_db("""UPDATE RestaurantTable 
                 SET tableNumber = %s, name = %s, restaurantID = %s 
                 WHERE id = %s""",
              args=(tableNumber, name, restaurantID, tableID))
    return jsonify({"message": "Table updated successfully"}), 200


@restaurant_tables_blueprint.route('/restaurantTables/<tableID>', methods=["DELETE"])
@jwt_required()
@swag_from({
    'tags': ['Restaurant Tables'],
    'description': 'Soft delete a restaurant table',
    'parameters': [
        {
            'name': 'tableID',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the table to delete'
        }
    ],
    'responses': {
        200: {'description': 'Table deleted successfully'},
        500: {'description': 'Internal server error'}
    }
})
def delete_table(tableID):
    try:
        insert_db('UPDATE RestaurantTable SET isDeleted = True WHERE id = %s', args=(tableID,))
        return jsonify({"message": "Table deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
