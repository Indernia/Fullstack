from flask import Blueprint, jsonify, request
from database import query_db, insert_db

ratings_blueprint = Blueprint('ratings', __name__)

@ratings_blueprint.route('/ratings', methods=["GET"])
def get_ratings():
    try:
        ratings = query_db('SELECT * FROM Rating')
        return jsonify(ratings), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@ratings_blueprint.route('/ratings', methods=["POST"])
def add_rating():
    data = request.get_json()
    rating_value = data.get("rating")
    restaurant_id = data.get("restaurantID")
    text = data.get("text")

    if not rating_value or not restaurant_id:
        return jsonify({"error": "Rating and restaurantID are required"}), 400
    
    insert_db('INSERT INTO Rating (rating, restaurantID, text) VALUES (?, ?, ?)', 
               args=(rating_value, restaurant_id, text))
    return jsonify({"message": "Rating added successfully"}), 200

@ratings_blueprint.route('/ratings/<rating_id>', methods=["PUT"])
def update_rating(rating_id):
    data = request.get_json()
    rating_value = data.get("rating")
    text = data.get("text")

    if not rating_value:
        return jsonify({"error": "Rating is required"}), 400

    try:
        insert_db('UPDATE Rating SET rating = ?, text = ? WHERE id = ?', 
                  args=(rating_value, text, rating_id))
        return jsonify({"message": "Rating updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@ratings_blueprint.route('/ratings/<rating_id>', methods=["DELETE"])
def delete_rating(rating_id):
    try:
        query_db('DELETE FROM Rating WHERE id = ?', args=(rating_id,))
        return jsonify({"message": "Rating deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


