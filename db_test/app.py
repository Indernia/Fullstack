from flask import Flask
from restaurantAPI import restaurant_api_blueprint
from flasgger import Swagger
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

app = Flask(__name__)

# Register the API blueprint
app.register_blueprint(restaurant_api_blueprint)

swagger = Swagger(app)

CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"])

if __name__ == '__main__':
    app.run(port=8000)


app.config["JWT_SECRET_KEY"] = "your_secret_key"
Bcrypt.init_app(app)
jwt = JWTManager(app)