from flask import Flask
from restaurantAPI import restaurant_api_blueprint

app = Flask(__name__)

# Register the API blueprint
app.register_blueprint(restaurant_api_blueprint)

if __name__ == '__main__':
    app.run(port=8080)
