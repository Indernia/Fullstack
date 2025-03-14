from flask import Blueprint, jsonify
from database import query_db
from flasgger import swag_from

restaurant_chains_blueprint = Blueprint('restaurant_chains', __name__)


@restaurant_chains_blueprint.route('/restaurantchains', methods=["GET"])
@swag_from({
    'tags': ['Restaurant Chains'],
    'responses': {
        200: {
            'description': 'All restaurant chains',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'The ID of the restaurant chain'
                        },
                        'name': {
                            'type': 'string',
                            'description': 'The name of the restaurant chain'
                        }
                    }
                }
            }
        },
        500: {
            'description': 'An error occurred while trying to retrieve the restaurant chains'
        }
    }
})
def get_restaurant_chains():
    chains = query_db('SELECT * FROM RestaurantChain')

    return jsonify(chains)
