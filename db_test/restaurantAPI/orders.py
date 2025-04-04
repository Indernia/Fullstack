from flask import Blueprint, request, jsonify
from database import query_db, insert_db
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity


orders_blueprint = Blueprint('orders', __name__)


@orders_blueprint.route('/orders/byrestaurant/<restaurantId>/', methods=["GET"])
@jwt_required()
@swag_from({
    'tags': ['Orders'],
    'responses': {
        200: {
            'description': 'All orders for a restaurant',
            'schema': {
                'type': 'object',
                'properties': {
                    'orderId': {
                        'type': 'integer',
                        'description': 'The ID of the order'
                    },
                    'restaurantId': {
                        'type': 'integer',
                        'description': 'The ID of the restaurant this order is for'
                    },
                    'customerId': {
                        'type': 'integer',
                        'description': 'The ID of the customer who placed the order'
                    },
                    'orderTable': {
                        'type': 'integer',
                        'description': 'The table number the order is for'
                    },
                    'orderTotal': {
                        'type': 'number',
                        'description': 'The total cost of the order'
                    }
                }
            }
        },
        401: {
            'description': 'Not autherized'
            },
        404: {
            'description': 'Orders not found'
        }},
    })
def get_orders(restaurantId):
    token = request.headers.get('Authorization')

    print(token)
    userid = get_jwt_identity()["id"]
    print(userid)

    restaurantsForUser = query_db("""
                                  SELECT R.ownerid
                                  FROM restaurant R
                                  WHERE R.id = %s
                                  LIMIT 1
                                  """, args=(restaurantId), one=True)

    if userid != restaurantsForUser["ownerid"]:
        print(restaurantsForUser)
        print(userid)
        return jsonify({"message": "you do not have access to this restaurant"}), 401

    request_data = query_db("""
                            SELECT
                            o.*,
                            json_agg(mi) AS menuItems
                            FROM orders o
                            LEFT JOIN orderincludesmenuitem oim ON oim.orderID = o.id
                            LEFT JOIN menuitem mi ON oim.menuItemID = mi.id
                            WHERE o.restaurantID = %s
                            AND orderComplete = false
                            GROUP BY o.id
                            """
                            , args=(restaurantId))
    return jsonify(request_data)


@orders_blueprint.route('/orders/byorderId/<orderId>/', methods=["GET"])
@swag_from({
    'tags': ['Orders'],
    'responses': {
        200: {
            'description': 'A single order',
            'schema': {
                'type': 'object',
                'properties': {
                    'orderId': {
                        'type': 'integer',
                        'description': 'The ID of the order'
                    },
                    'restaurantId': {
                        'type': 'integer',
                        'description': 'The ID of the restaurant this order is for'
                    },
                    'customerId': {
                        'type': 'integer',
                        'description': 'The ID of the customer who placed the order'
                    },
                    'orderTable': {
                        'type': 'integer',
                        'description': 'The table number the order is for'
                    },
                }
            }
        },
        404: {
            'description': 'Order not found'
        }},
    })
def get_order(orderId):
    request_data = query_db("SELECT * FROM orders WHERE orderId = %s AND orderComplete = false"
                            , args=(orderId))
    return jsonify(request_data)


@orders_blueprint.route('/orders/add', methods=["POST"])
@swag_from({
    'tags': ['Orders'],
    'parameters': [{
        'in': 'body',
        'name': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'restaurantId': {
                    'type': 'integer',
                    'description': 'The ID of the restaurant this order is for'
                },
                'userId': {
                    'type': 'integer',
                    'description': 'The ID of the customer who placed the order'
                },
                'orderTable': {
                    'type': 'integer',
                    'description': 'The table number the order is for'
                },
                'orderTime': {
                    'type': 'string',
                    'description': 'The time the order was placed'
                },
                'comments': {
                    'type': 'string',
                    'description': 'any comments there may be for the order, can be blank'
                },
                'menuItems': {
                    'type': 'array',
                    'items': {
                        'type': 'integer',
                        'description': 'The ID of a menu item'
                    }
                }
            }
        }
    }],
    'responses': {
        201: {
            'description': 'Order created'
        },
        400: {
            'description': 'Bad request'
        }},
    })
def add_order():
    # TODO: Add better rollback for none existing menu items
    request_data = request.get_json()
    restaurantId = request_data['restaurantId']
    userId = request_data['userId']
    orderTable = request_data['orderTable']
    menuItems = request_data['menuItems']
    comments = request_data.get('comments', "no comments")
    orderTotal = 0
    for item in menuItems:
        item_data = query_db("SELECT price FROM menuitem WHERE id = %s",
                             args=(item,))
        orderTotal += item_data[0]['price']
        print(orderTotal)

    orderID = insert_db("""INSERT INTO orders
                        (restaurantId, userID, tableID, orderCost, orderComplete, orderTime, comments)
                        VALUES (%s, %s, %s, %s, False, now(), %s)
                        RETURNING id""",
                        args=(restaurantId, userId, orderTable, orderTotal, comments))

    for item in menuItems:
        insert_db("INSERT INTO orderincludesmenuitem (orderID, menuItemID) VALUES (%s, %s)",
                  args=(orderID, item))

    return jsonify({"message": "Order created"}), 201


@orders_blueprint.route('/orders/markComplete/<orderID>/', methods=["PUT"])
@swag_from({
    'tags': ['Orders'],
    'parameters': [{
        'name': 'orderId',
        'in': 'path',
        'description': 'The ID of the order to mark as complete',
        'required': True,
        'type': 'integer'
    }],
    'responses': {
        200: {
            'description': 'Order marked as complete'
        },
        404: {
            'description': 'Order not found'
        }},
    })
def mark_order_complete(orderID):
    insert_db("UPDATE orders SET orderComplete = TRUE WHERE id = %s", args=(orderID,))
    return jsonify({"message": "Order marked as complete"}), 200



@orders_blueprint.route('/orders/items/<orderId>/', methods=["GET"])
@swag_from({
    'tags': ['Orders'],
    'parameters': [{
        'name': 'orderId',
        'in': 'path',
        'description': 'The ID of the order to get items from',
        'required': True,
        'type': 'integer'
    }],
    'responses': {
        200: {
            'description': 'Items in the order',
            'schema': {
                'type': 'object',
                'properties': {
                    'menuItemID': {
                        'type': 'integer',
                        'description': 'The ID of the menu item'
                    }
                }
            }
        },
        404: {
            'description': 'Order not found'
        }},
    })
def get_order_items(orderId):
    request_data = query_db("""
                            SELECT mi.*
                            FROM orderincludesmenuitem oim
                            LEFT JOIN menuitem mi ON oim.orderID = mi.id
                            WHERE orderID = %s
                            """,
                            args=(orderId,))
    return jsonify(request_data)











