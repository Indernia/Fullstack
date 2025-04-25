from flask import Blueprint
from .users import users_blueprint
from .restaurants import restaurants_blueprint
from .menus import menus_blueprint
from .menu_sections import menu_sections_blueprint
from .menu_items import menu_items_blueprint
from .ratings import ratings_blueprint
from .admin_users import admin_users_blueprint
from .orders import orders_blueprint
from .api_keys import api_keys_blueprint
from .sas_url import sas_url_blueprint
from .tags import tags_blueprint

# Create a blueprint for the entire API to register it in `app.py`
restaurant_api_blueprint = Blueprint('restaurantAPI', __name__)

# Register individual blueprints
restaurant_api_blueprint.register_blueprint(users_blueprint)
restaurant_api_blueprint.register_blueprint(restaurants_blueprint)
restaurant_api_blueprint.register_blueprint(menus_blueprint)
restaurant_api_blueprint.register_blueprint(menu_sections_blueprint)
restaurant_api_blueprint.register_blueprint(menu_items_blueprint)
restaurant_api_blueprint.register_blueprint(ratings_blueprint)
restaurant_api_blueprint.register_blueprint(admin_users_blueprint)
restaurant_api_blueprint.register_blueprint(api_keys_blueprint)
restaurant_api_blueprint.register_blueprint(orders_blueprint)
restaurant_api_blueprint.register_blueprint(sas_url_blueprint)
restaurant_api_blueprint.register_blueprint(tags_blueprint)
