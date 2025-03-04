from flask import Blueprint, jsonify, request
from database import query_db, insert_db

restaurant_chains_blueprint = Blueprint('restaurant_chains', __name__)

@restaurant_chains_blueprint.route('/restaurantchains', methods=["GET"])
def get_restaurant_chains():
    chains = query_db('SELECT * FROM RestaurantChain')
    
    return jsonify(chains)