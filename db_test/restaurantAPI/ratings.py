from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from

ratings_blueprint = Blueprint('ratings', __name__)


@ratings_blueprint.route('/ratings', methods=["GET"])
@swag_from({
    'tags': ['Ratings'],
    'responses': {
        200: {
            'description': 'All ratings',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer',
                            'description': 'The ID of the rating'
                        },
                        'rating': {
                            'type': 'integer',
                            'description': 'The rating value'
                        },
                        'restaurantID': {
                            'type': 'integer',
                            'description': 'The ID of the restaurant this rating belongs to'
                        },
                        'text': {
                            'type': 'string',
                            'description': 'The text of the rating'
                        }
                    }
                }
            }
        },
        500: {
            'description': 'An error occurred while trying to retrieve the ratings'
        }
    }
})
def get_ratings():
    try:
        ratings = query_db('SELECT * FROM Rating')
        return jsonify(ratings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ratings_blueprint.route('/ratings', methods=["POST"])
@swag_from({
    'tags': ['Ratings'],
    'responses': {
        200: {
            'description': 'Rating added successfully'
        },
        400: {
            'description': 'Rating and restaurantID are required'
        }},
    'parameters': [{
        'name': 'body',
        'description': 'Rating object',
        'in': 'body',
        'schema': {
            'type': 'object',
            'properties': {
                'rating': {
                    'type': 'integer',
                    'description': 'The rating value'
                },
                'restaurantID': {
                    'type': 'integer',
                    'description': 'The ID of the restaurant this rating belongs to'
                },
                'text': {
                    'type': 'string',
                    'description': 'The text of the rating'
                }
            }
        }
    }
    ]
})
def add_rating():
    data = request.get_json()
    rating_value = data.get("rating")
    restaurant_id = data.get("restaurantID")
    text = data.get("text")

    if not rating_value or not restaurant_id:
        return jsonify({"error": "Rating and restaurantID are required"}), 400

    insert_db('INSERT INTO Rating (rating, restaurantID, text) VALUES (%s, %s, %s)',
              args=(rating_value, restaurant_id, text))
    return jsonify({"message": "Rating added successfully"}), 200


@ratings_blueprint.route('/ratings/<rating_id>', methods=["PUT"])
@swag_from({
    'tags': ['Ratings'],
    'responses': {
        200: {
            'description': 'Rating updated successfully'
        },
        400: {
            'description': 'Rating is required'
        }},
    'parameters': [{
        'name': 'rating_id',
        'description': 'The ID of the rating to update',
        'type': 'integer',
        'required': True
    },
        {
            'name': 'body',
            'description': 'Rating object',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'rating': {
                        'type': 'integer',
                        'description': 'The rating value'
                    },
                    'text': {
                        'type': 'string',
                        'description': 'The text of the rating'
                    }}}}]
    })
def update_rating(rating_id):
    data = request.get_json()
    rating_value = data.get("rating")
    text = data.get("text")

    if not rating_value:
        return jsonify({"error": "Rating is required"}), 400

    try:
        insert_db('UPDATE Rating SET rating = %s, text = %s WHERE id = %s',
                  args=(rating_value, text, rating_id))
        return jsonify({"message": "Rating updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@ratings_blueprint.route('/ratings/<rating_id>', methods=["DELETE"])
@swag_from({
    'tags': ['Ratings'],
    'responses': {
        200: {
            'description': 'Rating deleted successfully'
        },
        500: {
            'description': 'An error occurred while trying to delete the rating'
        }
    }
})
def delete_rating(rating_id):
    try:
        insert_db('DELETE FROM Rating WHERE id = %s', args=(rating_id,))
        return jsonify({"message": "Rating deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
