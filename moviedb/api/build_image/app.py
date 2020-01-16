from flask import Flask, request
from flask_restful import Resource, Api
import mysql.connector
from flask import jsonify
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
CORS(app)

cnx = None
def get_cnx():
    global cnx
    if cnx and cnx.is_connected():
        return cnx
    else:
        cnx = mysql.connector.connect(
            host='mysqlsvc',
            user='movie_db_user',
            passwd='movie_db_pwd',
            database='movie_db',
            auth_plugin='mysql_native_password'
        )
        return cnx

class MovieById(Resource):
    def get(self, movie_id):
        cur = get_cnx().cursor(buffered=True)
        try:
            query = "select * from movietable where id =%d "  %int(movie_id)
        except:
            resp = {
                'status': 'fail',
                'message': 'Movie Id should be an integer'
            }
            return resp, 500
        cur.execute(query)
        records = cur.fetchall()
        return jsonify(records)

class MovieList(Resource):
    def get(self):
        startstr = request.args.get('start',0)
        try:
            start = int(startstr)
        except:
            start = 0
        limit = 20
        cur = get_cnx().cursor(buffered=True)
        query = (
            "select id, title"
            " from movietable"
            " order by vote_average desc"
            " limit %d, %d" %(start, limit)
        )
        app.logger.info('query: ' + query)
        cur.execute(query)
        records = cur.fetchall()
        list_movies = [{'id': r[0], 'title': r[1]} for r in records]
        return jsonify(movies=list_movies)

class Search(Resource):
    def get(self):
        filter = (
            '%' + request.args.get('title', '') + '%',
            '%' + request.args.get('genre', '') + '%'
        )
        cur = get_cnx().cursor(buffered=True)
        query = (
            "select id, title"
            " from movietable"
            " where title like %s"
            "  and genres like %s"
            " order by vote_average desc"
            " limit 20"
        )
        cur.execute(query, filter)
        records = cur.fetchall()
        return jsonify(records)


api.add_resource(MovieById, '/movie/<movie_id>')
api.add_resource(MovieList, '/getlist')
api.add_resource(Search, '/search')
