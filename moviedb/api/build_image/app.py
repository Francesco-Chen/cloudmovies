from flask import Flask, request
from flask_restful import Resource, Api
import mysql.connector
import ast
from flask import jsonify
from flask_cors import CORS
import json

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

fields = [
    'budget','genres','homepage','id','keywords','original_language',
    'original_title','overview','popularity','production_companies',
    'production_countries','release_date','revenue','runtime',
    'spoken_languages','status','tagline','title','vote_average','vote_count', 'actors', 'director'
]

class MovieById(Resource):
    def get(self, movie_id):
        cur = get_cnx().cursor(buffered=True)
        try:
            query = " select mt.*, ct.actors, ct.directors from movietable as mt inner join casttable as ct on mt.id = ct.id where mt.id=%d"  %int(movie_id)
        except:
            resp = {
                'status': 'fail',
                'message': 'Movie Id should be an integer'
            }
            return resp, 500
        cur.execute(query)
        record = cur.fetchone()
        if record:
            d = {key: value for key, value in zip(fields, record)}

            d['genres'] = ast.literal_eval(d['genres'])
            d['keywords'] = ast.literal_eval(d['keywords'])
            d['spoken_languages'] = ast.literal_eval(d['spoken_languages'])
            d['production_companies'] = ast.literal_eval(d['production_companies'])
            d['production_countries'] = ast.literal_eval(d['production_countries'])
            d['actors'] = json.loads(d['actors'])

            d['genres'] = [genre['name'] for genre in d['genres']]
            d['keywords'] = [keyword['name'] for keyword in d['keywords']]
            d['spoken_languages'] = [lang['name'] for lang in d['spoken_languages']]
            d['production_companies'] = [comp['name'] for comp in d['production_companies']]
            d['production_countries'] = [countr['name'] for countr in d['production_countries']]
            d['actors'] = [actor['name'] for actor in d['actors']]
        else:
            d = []
        return jsonify(info=d)

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
        if request.args.get('id', ''):
            string_id = request.args['id']
            list_id = string_id.split(',')
            try:
                list_id = [int(e) for e in list_id]
            except:
                resp = {
                    'status': 'fail',
                    'message': 'Movie Id should be integers'
                }
                return resp, 500
            
            cur = get_cnx().cursor(buffered=True)
            query = (
                "select id, title"
                " from movietable"
                " where id in (%s)"
                %string_id
            )
            cur.execute(query)
            records = cur.fetchall()
            list_movies = [{'id': r[0], 'title': r[1]} for r in records]
            return jsonify(movies=list_movies)
        
        else:
            # extract start parameter
            startstr = request.args.get('start',0)
            try:
                start = int(startstr)
            except:
                start = 0
            limit = 20

            # extract genres param from url and convert it to list
            genres = request.args.get('genres', '').split(',')

            # construct filter tuple
            filter = (
                '%' + request.args.get('title', '') + '%',
            )
            for genre in genres:
                filter += ('%' + genre + '%',)
            app.logger.info('filter: ' + str(filter))

            cur = get_cnx().cursor(buffered=True)
            query = ' '.join([
                "select id, title",
                "from movietable",
                "where title like %s",
                " and genres like %s" * len(genres),
                "order by vote_average desc",
                "limit %d, %d" %(start, limit)
            ])
            cur.execute(query, filter)
            records = cur.fetchall()
            list_movies = [{'id': r[0], 'title': r[1]} for r in records]
            return jsonify(movies=list_movies)


api.add_resource(MovieById, '/movie/<movie_id>')
api.add_resource(MovieList, '/getlist')
api.add_resource(Search, '/search')
