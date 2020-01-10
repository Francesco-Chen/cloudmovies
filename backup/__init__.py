from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

from . import auth
app.register_blueprint(auth.auth_blueprint)

