from flask import Flask
from flask_bcrypt import Bcrypt
import mysql.connector

app = Flask(__name__)
bcrypt = Bcrypt(app)


cnx = mysql.connector.connect(
    host='userdbsvc',
    user='userdb_user',
    passwd='userdb_pwd',
    database='userdb'
)
cursor = cnx.cursor()

from . import auth
app.register_blueprint(auth.auth_blueprint)
