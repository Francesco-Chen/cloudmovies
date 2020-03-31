from flask import Flask, request, make_response
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
            host='favoritesdbsvc',
            user='favoritesdb_user',
            passwd='favoritesdb_pwd',
            database='favoritesdb'
        )
        return cnx


def check_header(request):
    userid = request.headers.get('Cloudmovie-UserId','')
    if (not userid or not userid.isnumeric()):
        return False
    return True



class addFavorite(Resource):
    def get(self):
        # get user id
        if check_header(request):
            userid = int(request.headers['Cloudmovie-UserId'])
        else:
            responseObject = {
                'status': 'fail',
                'message': 'internal error: user id not found'
            }
            return make_response(jsonify(responseObject), 500)
        
        # get movieid parameter
        try:
            movieid = int(request.args['movieid'])
        except:
            responseObject = {
                'status': 'fail',
                'message': 'parameter incorrect'
            }
            return make_response(jsonify(responseObject), 500)
        
        # get number of favorites
        cur = get_cnx().cursor()
        query = "select count(*) from favorites where userid = %d" %userid
        cur.execute(query)
        num_of_favorites = cur.fetchone()[0]
        
        # insert record
        if (num_of_favorites < 5):
            query = (
                "insert into favorites (userid, movieid, created)"
                "values (%s, %s, now())" %(userid, movieid)
            )
            try:
                cur.execute(query)
                get_cnx().commit()
            except mysql.connector.Error as error:
                responseObject = {
                    'status': 'fail',
                    'message': 'movie already added'
                }
                return make_response(jsonify(responseObject), 500)
            # if insert ok
            responseObject = {
                'status': 'success',
                'message': 'movie added'
            }
            return make_response(jsonify(responseObject), 200)
        else:
            responseObject = {
                'status': 'fail',
                'message': 'max number of favorites reached'
            }
            return make_response(jsonify(responseObject), 500)
#

class deleteFavorite(Resource):
    def get(self):
        # get user id
        if check_header(request):
            userid = int(request.headers['Cloudmovie-UserId'])
        else:
            responseObject = {
                'status': 'fail',
                'message': 'internal error: user id not found'
            }
            return make_response(jsonify(responseObject), 500)
        
         # get movieid parameter
        try:
            movieid = int(request.args['movieid'])
        except:
            responseObject = {
                'status': 'fail',
                'message': 'parameter incorrect'
            }
            return make_response(jsonify(responseObject), 500)
        
        # delete row
        cur = get_cnx().cursor()
        query = (
            "delete from favorites where userid = %s and movieid = %s"
            %(userid, movieid)
        )
        cur.execute(query)
        get_cnx().commit()
        responseObject = {
            'status': 'success',
            'message': str(cur.rowcount) + ' record(s) deleted'
        }
        return make_response(jsonify(responseObject), 200)
#

class getFavorites(Resource):
    def get(self):
        # get user id
        if check_header(request):
            userid = int(request.headers['Cloudmovie-UserId'])
        else:
            responseObject = {
                'status': 'fail',
                'message': 'internal error: user id not found'
            }
            return make_response(jsonify(responseObject), 500)
        
        # query
        query = "select movieid from favorites where userid = %s" %userid
        cur = get_cnx().cursor()
        cur.execute(query)
        records = cur.fetchall()
        list_movieid = [r[0] for r in records]
        return jsonify(list_movieid)
#


api.add_resource(addFavorite, '/addfavorite')
api.add_resource(deleteFavorite, '/deletefavorite')
api.add_resource(getFavorites, '/getfavorites')
