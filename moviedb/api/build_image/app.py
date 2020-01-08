from flask import Flask, request
from flask_restful import Resource, Api
import mysql.connector
from json import dumps
from flask import jsonify

cnx = mysql.connector.connect(
    host='mysqlsvc',
    user='movie_db_user',
    passwd='movie_db_pwd',
    database='movie_db',
    auth_plugin='mysql_native_password'
)
app = Flask(__name__)
api = Api(app)

class MovieById(Resource):
    def get(self, movie_id):
        cur = cnx.cursor(buffered=True)
        query = "select * from movietable where id =%d "  %int(movie_id)
        cur.execute(query)
        records = cur.fetchall()
        return jsonify(records)

class MovieList(Resource):
    def get(self):
        cur = cnx.cursor(buffered=True)
        query = "select id, title from movietable"
        cur.execute(query)
        records = cur.fetchall()
        return jsonify(records)

api.add_resource(MovieById, '/movie/<movie_id>')
api.add_resource(MovieList, '/getlist')


if __name__ == '__main__':
     app.run(port='5002',host='0.0.0.0')
