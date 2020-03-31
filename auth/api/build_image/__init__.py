from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS

app = Flask(__name__)
bcrypt = Bcrypt(app)
CORS(app)

from . import auth
app.register_blueprint(auth.auth_blueprint)
