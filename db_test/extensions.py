from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from cryptography.fernet import Fernet
import os

bcrypt = Bcrypt()
jwt = JWTManager()
fernet = Fernet(os.getenv['FERNET_KEY'])


def encrypt(value: str) -> str:
    return fernet.encrypt(value.encode()).decode()

def decrypt(value: str) -> str:
    return fernet.decrypt(value.encode()).decode()