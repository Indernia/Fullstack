from flask import Blueprint, request, jsonify
from database import query_db, insert_db
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import bcrypt, decrypt
import stripe 
import os
import hashlib

orders_blueprint = Blueprint('orders', __name__)


@orders_blueprint.route('/orders/byrestaurant', methods=["GET"])
@swag_from({
    'tags': ['Orders'],
    'summary': 'Get all orders for a specific restaurant',
    'description': 'This endpoint retrieves all incomplete orders for a specific restaurant, based on the provided API key. The orders are grouped with their respective menu items.',
    'parameters': [
        {
            'name': 'Authorization',
            'in': 'header',
            'description': 'API key for the restaurant (Bearer token format)',
            'required': True,
            'type': 'string',
            'example': 'Bearer YOUR_API_KEY'
        }
    ],
    'responses': {
        200: {
            'description': 'All orders for the restaurant retrieved successfully',
            'schema': {
                'type': 'array',
                'items': {
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
                        },
                        'menuItems': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'menuItemId': {
                                        'type': 'integer',
                                        'description': 'The ID of the menu item'
                                    },
                                    'menuItemName': {
                                        'type': 'string',
                                        'description': 'The name of the menu item'
                                    },
                                    'menuItemPrice': {
                                        'type': 'number',
                                        'description': 'The price of the menu item'
                                    }
                                }
                            },
                            'description': 'List of menu items included in the order'
                        }
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized access - Missing or invalid API key'
        },
        404: {
            'description': 'No orders found for the given restaurant'
        }
    }
})
def get_orders():
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing authorization header"}), 401

    try:
        apikey = auth_header.split(" ")[1]
    except IndexError:
        return jsonify({"error": "Invalid authorization header format"}), 401

    hashed_key = hashlib.sha256(apikey.encode()).hexdigest()

    request_data = query_db("""
    WITH restaurant AS (
        SELECT restaurantID
        FROM apikeys
        WHERE apikey = %s 
        LIMIT 1
    )
    SELECT
        o.*,
        json_agg(mi.*) AS menuItems
    FROM orders o
    LEFT JOIN orderincludesmenuitem oim ON oim.orderID = o.id
    LEFT JOIN menuitem mi ON oim.menuItemID = mi.id
    WHERE o.restaurantID = (SELECT restaurantID FROM restaurant)
    AND orderComplete = false
    GROUP BY o.id
    """,
    args=(hashed_key,)
    )
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

    return jsonify({"message": f"Order created: {orderID}"}), 201

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
            'description': 'Order marked as complete',
            'examples': {
                'application/json': {
                    'message': 'Order marked as complete'
                }
            }
        },
        401: {
            'description': 'Unauthorized request due to incorrect API key or missing API key',
            'examples': {
                'application/json': {
                    'error': 'Incorrect key given'
                }
            }
        },
        404: {
            'description': 'Order not found',
            'examples': {
                'application/json': {
                    'error': 'Order not found'
                }
            }
        }
    }
})
def mark_order_complete(orderID):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return jsonify({"error": "Missing authorization header"}), 401

    try:
        apikey = auth_header.split(" ")[1]
    except IndexError:
        return jsonify({"error": "Invalid authorization header format"}), 401

    hashed_key = hashlib.sha256(apikey.encode()).hexdigest()

    order_details = query_db("""
        SELECT o.restaurantID
        FROM orders o
        WHERE o.id = %s AND o.isDeleted = false
    """, args=(orderID,), one=True)

    if not order_details:
        return jsonify({"error": "Order not found"}), 404
    
    restaurantID = order_details['restaurantid']
    storedkeys = query_db("""
        SELECT apikey
        FROM apikeys
        WHERE restaurantID = %s AND isDeleted = false
    """, args=(restaurantID,))

    for storedkey in storedkeys:
        if storedkey['apikey'] == hashed_key:
            insert_db("UPDATE orders SET orderComplete = TRUE WHERE id = %s", args=(orderID,))
            return jsonify({"message": "Order marked as complete"}), 200
        
    return jsonify({"message": "Incorrect key given"}), 401

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
        }
    }
})
def get_order_items(orderID):
    request_data = query_db("""
        SELECT 
            mi.id, 
            mi.name, 
            mi.description, 
            mi.price, 
            COUNT(*) AS quantity
        FROM OrderIncludesMenuItem oim
        JOIN MenuItem mi ON oim.menuItemID = mi.id
        WHERE oim.orderID = %s
        GROUP BY mi.id, mi.name, mi.description, mi.price
    """, args=(orderID,))
    return jsonify(request_data)


@orders_blueprint.route('/orders/<int:orderID>/create-payment-session', methods=['POST'])
@swag_from({
    'tags': ['Orders'],
    'summary': 'Create a payment session for an order',
    'description': 'This endpoint creates a Stripe payment session for an order. It optionally accepts a tip amount that can be added to the order total.',
    'parameters': [
        {
            'name': 'orderID',
            'in': 'path',
            'required': True,
            'type': 'integer',
            'description': 'ID of the order for which the payment session is being created.'
        },
        {
            'name': 'body',
            'in': 'body',
            'required': False,
            'schema': {
                'type': 'object',
                'properties': {
                    'tip': {
                        'type': 'number',
                        'format': 'float',
                        'description': 'Optional tip amount in USD to include in the payment.'
                    }
                }
            }
        }
    ],
    'responses': {
        '200': {
            'description': 'Checkout session URL successfully created.',
            'schema': {
                'type': 'object',
                'properties': {
                    'checkout_url': {
                        'type': 'string',
                        'description': 'URL to the Stripe checkout session.',
                        'example': "https://checkout.stripe.com/pay/cs_test_a1b2c3d4..."
                    }
                }
            }
        },
        '404': {
            'description': 'Order not found.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': "Order not found"
                    }
                }
            }
        },
        '500': {
            'description': 'Internal server error.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': "Internal Server Error"
                    }
                }
            }
        }
    }
})
def create_checkout_session(orderID):
    data = request.get_json()
    order = query_db("SELECT * FROM orders WHERE id = %s", args=(orderID,))
    if not order:
        return jsonify({"error": "Order not found"}), 404
    
    result = query_db("""
        SELECT r.stripekey
        FROM orders o
        JOIN restaurant r ON o.restaurantid = r.id
        WHERE o.id = %s
    """, args=(orderID,), one=True)
    
    stripe.api_key = decrypt(result['stripekey'])

    # Fetch associated menu items and their quantities
    items = query_db("""
        SELECT 
            mi.id, 
            mi.name, 
            mi.description, 
            mi.price, 
            COUNT(*) AS quantity
        FROM OrderIncludesMenuItem oim
        JOIN MenuItem mi ON oim.menuItemID = mi.id
        WHERE oim.orderID = %s
        GROUP BY mi.id, mi.name, mi.description, mi.price
    """, args=(orderID,))

    # Build the line items for Stripe
    line_items = []
    for item in items:
        line_items.append({
            'price_data': {
                'currency': 'dkk',
                'unit_amount': int(item['price'] * 100),  # Convert price to cents (best practice)
                'product_data': {
                    'name': item['name'],
                    'description': item.get('description', '')
                },
            },
            'quantity': item['quantity'],
        })
    
    if data and 'tip' in data:
        tip = data.get('tip')
        line_items.append({
            'price_data': {
                'currency': 'dkk',
                'unit_amount': int(tip * 100),
                'product_data': {
                    'name': "tip",
                    'description': "Tip for the staff"
                },
            },
            'quantity': 1,
        })

    try:
        # Create the Stripe Checkout session
        session = stripe.checkout.Session.create(
            line_items=line_items,
            mode='payment',
            success_url='http://130.225.170.52:10331/payment-success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://130.225.170.52:10331/payment-cancel',
            metadata={
                'orderID': str(orderID),
            }
        )
    except Exception as e:
        return str(e)

    return jsonify({'checkout_url': session.url})


@orders_blueprint.route('/orders/paymentStatus', methods=['PUT'])
def update_payment_status():
    data = request.get_json()
    sessionID = data.get('sessionID')

    try:
        session = stripe.checkout.Session.retrieve(sessionID)
        payment_status = session.payment_status

        if payment_status == "paid":
            orderID = session.metadata.get('orderID')

            insert_db("UPDATE orders SET isPaid = TRUE WHERE id = %s", args=(orderID,))
            return jsonify({'status': payment_status})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500




