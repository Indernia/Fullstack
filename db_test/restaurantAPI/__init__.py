from flask import Blueprint
from .users import users_blueprint
from .restaurants import restaurants_blueprint
from .menus import menus_blueprint
from .menu_sections import menu_sections_blueprint
from .menu_items import menu_items_blueprint
from .restaurant_chains import restaurant_chains_blueprint
from .ratings import ratings_blueprint

# Create a blueprint for the entire API to register it in `app.py`
restaurant_api_blueprint = Blueprint('restaurantAPI', __name__)

# Register individual blueprints
restaurant_api_blueprint.register_blueprint(users_blueprint)
restaurant_api_blueprint.register_blueprint(restaurants_blueprint)
restaurant_api_blueprint.register_blueprint(menus_blueprint)
restaurant_api_blueprint.register_blueprint(menu_sections_blueprint)
restaurant_api_blueprint.register_blueprint(menu_items_blueprint)
restaurant_api_blueprint.register_blueprint(restaurant_chains_blueprint)
restaurant_api_blueprint.register_blueprint(ratings_blueprint)
