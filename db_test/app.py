from flask import Flask
from restaurantAPI import restaurant_api_blueprint
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__)

# Register the API blueprint
app.register_blueprint(restaurant_api_blueprint)

swagger = Swagger(app)

CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"])

if __name__ == '__main__':
    app.run(port=8080)
